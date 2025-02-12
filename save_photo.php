<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    die(json_encode(['error' => '許可されていないメソッドです']));
}

// 画像データを取得
$image_data = $_POST['image'];
$image_data = str_replace('data:image/png;base64,', '', $image_data);
$image_data = str_replace(' ', '+', $image_data);
$image_data = base64_decode($image_data);

// 保存用ディレクトリの作成
$upload_dir = 'photos';
if (!file_exists($upload_dir)) {
    mkdir($upload_dir, 0777, true);
}

// ファイル名の生成（日時とランダムな文字列）
$filename = date('Y-m-d_H-i-s') . '_' . uniqid() . '.png';
$filepath = $upload_dir . '/' . $filename;

// 画像を保存
if (file_put_contents($filepath, $image_data)) {
    echo json_encode([
        'success' => true,
        'message' => '写真を保存しました',
        'filename' => $filename,
        'filepath' => $filepath
    ]);
} else {
    http_response_code(500);
    echo json_encode(['error' => '写真の保存に失敗しました']);
}
?> 