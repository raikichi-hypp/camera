from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import base64
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)  # クロスオリジン要求を許可

# 写真保存用のディレクトリ
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>写真一覧</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .photo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .photo-item {
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }
        .photo-item img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 4px;
        }
        .photo-item p {
            margin: 10px 0;
            font-size: 14px;
            color: #666;
        }
        .refresh-button, .delete-button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .refresh-button {
            display: block;
            margin: 20px auto;
        }
        .delete-button {
            background-color: #f44336;
            margin-top: 10px;
            width: 100%;
        }
        .refresh-button:hover {
            background-color: #45a049;
        }
        .delete-button:hover {
            background-color: #da190b;
        }
        .controls {
            text-align: center;
            margin-bottom: 20px;
        }
        .camera-button {
            background-color: #2196F3;
            margin: 0 10px;
        }
        .camera-button:hover {
            background-color: #1976D2;
        }
    </style>
    <script>
        async function deletePhoto(filename) {
            if (confirm('この写真を削除してもよろしいですか？')) {
                try {
                    const response = await fetch(`/delete/${filename}`, {
                        method: 'DELETE'
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert('写真を削除しました');
                        location.reload();
                    } else {
                        alert('削除に失敗しました: ' + result.error);
                    }
                } catch (error) {
                    alert('削除中にエラーが発生しました');
                }
            }
        }
    </script>
</head>
<body>
    <h1>撮影した写真一覧</h1>
    <div class="controls">
        <button class="refresh-button camera-button" onclick="window.location.href='index.html'">写真を撮影</button>
        <button class="refresh-button" onclick="location.reload()">更新</button>
    </div>
    <div class="photo-grid">
        {% for photo in photos %}
        <div class="photo-item">
            <img src="/uploads/{{ photo.filename }}" alt="写真">
            <p>撮影日時: {{ photo.date }}</p>
            <button class="delete-button" onclick="deletePhoto('{{ photo.filename }}')">削除</button>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# ルートパスへのアクセスを処理（写真一覧を表示）
@app.route('/')
def serve_index():
    try:
        photos = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.png'):
                # ファイル名から日時を抽出
                date_str = filename.replace('photo_', '').replace('.png', '')
                date = datetime.strptime(date_str, '%Y%m%d_%H%M%S').strftime('%Y/%m/%d %H:%M:%S')
                photos.append({
                    'filename': filename,
                    'date': date
                })
        # 日時でソート（新しい順）
        photos.sort(key=lambda x: x['filename'], reverse=True)
        return render_template_string(HTML_TEMPLATE, photos=photos)
    except Exception as e:
        app.logger.error(f"写真一覧の取得に失敗しました: {str(e)}")
        return jsonify({'error': '写真一覧の取得に失敗しました'}), 500

# 写真の削除
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({
                'success': True,
                'message': '写真を削除しました'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'ファイルが見つかりません'
            }), 404
    except Exception as e:
        app.logger.error(f"写真の削除に失敗しました: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# アップロードされた写真を提供
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 静的ファイルの提供
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_photo():
    # OPTIONSリクエストへの対応
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    try:
        # 画像データを取得
        image_data = request.form.get('image')
        if not image_data:
            return jsonify({'error': '画像データがありません'}), 400

        # Base64デコード
        image_data = image_data.replace('data:image/png;base64,', '')
        image_data = base64.b64decode(image_data)

        # ファイル名を生成（タイムスタンプ使用）
        filename = f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 画像を保存
        with open(filepath, 'wb') as f:
            f.write(image_data)

        return jsonify({
            'success': True,
            'message': '写真を保存しました',
            'filename': filename
        })

    except Exception as e:
        app.logger.error(f"エラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

# エラーハンドラー
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'ページが見つかりません'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'サーバーエラーが発生しました'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 