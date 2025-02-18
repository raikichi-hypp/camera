document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const photo = document.getElementById('photo');
    const cameraButton = document.getElementById('cameraButton');
    let stream = null;

    // サーバーのベースURL
    const SERVER_URL = 'https://9645-240f-f1-8448-1-354f-7505-8d3f-64de.ngrok-free.app';

    // カメラボタンのイベントリスナー
    cameraButton.addEventListener('click', async () => {
        if (!stream) {
            // カメラを起動
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user'
                    },
                    audio: false
                });
                video.srcObject = stream;
                photo.style.display = 'none';
                video.style.display = 'none';
                
                // 自動で写真を撮影
                setTimeout(() => {
                    // 写真を撮影
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const context = canvas.getContext('2d');
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    // 写真は非表示のままにする
                    photo.style.display = 'none';
                    
                    // カメラストリームを停止
                    stream.getTracks().forEach(track => track.stop());
                    stream = null;
                    
                    // 写真をサーバーに送信
                    uploadPhoto(canvas.toDataURL('image/png'));
                }, 500);
            } catch (err) {
                console.error('カメラの起動に失敗しました:', err);
                alert('カメラの起動に失敗しました。カメラへのアクセスを許可してください。');
                // エラー時にボタンを再度有効化
                cameraButton.disabled = false;
            }
        }
    });

    // 写真アップロード関数
    async function uploadPhoto(imageData) {
        try {
            const formData = new FormData();
            formData.append('image', imageData);

            // サーバーの状態をチェック
            try {
                await fetch(SERVER_URL);
            } catch (error) {
                throw new Error('サーバーに接続できません。サーバーが起動しているか確認してください。');
            }

            const response = await fetch(`${SERVER_URL}/upload`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                alert('写真を保存しました');
                // 写真一覧ページに遷移
                window.location.href = SERVER_URL;
            } else {
                throw new Error(result.error || '保存に失敗しました');
            }
        } catch (error) {
            console.error('アップロードエラー:', error);
            if (error.message.includes('サーバーに接続できません')) {
                alert(error.message);
            } else {
                alert('写真の保存に失敗しました: ' + error.message);
            }
        } finally {
            // 処理完了後にボタンを再度有効化
            cameraButton.disabled = false;
        }
    }
}); 