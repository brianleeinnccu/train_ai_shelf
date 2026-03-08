"""
裁切貨架層腳本
從 1054_shelf_dataset_v1 資料集中裁切出所有標註的貨架層（shelf）
"""

import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm


def imread_unicode(img_path):
    """
    讀取包含中文路徑的圖片
    
    參數:
        img_path: 圖片路徑（支援中文）
        
    返回:
        numpy array 格式的圖片，如果讀取失敗則返回 None
    """
    try:
        # 使用 numpy 讀取二進制檔案，再用 cv2 解碼
        with open(img_path, 'rb') as f:
            img_data = f.read()
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        return None


def imwrite_unicode(img_path, img):
    """
    儲存圖片到包含中文路徑的位置
    
    參數:
        img_path: 輸出路徑（支援中文）
        img: 圖片 numpy array
        
    返回:
        是否成功儲存
    """
    try:
        # 編碼圖片
        ext = Path(img_path).suffix
        is_success, buffer = cv2.imencode(ext, img)
        if is_success:
            # 寫入檔案
            with open(img_path, 'wb') as f:
                f.write(buffer)
            return True
        return False
    except Exception as e:
        return False


def yolo_to_bbox(x_center, y_center, width, height, img_width, img_height):
    """
    將 YOLO 格式的座標轉換為邊界框座標
    
    參數:
        x_center, y_center: 中心點座標（相對值 0-1）
        width, height: 寬度和高度（相對值 0-1）
        img_width, img_height: 圖片的實際寬高
        
    返回:
        (x1, y1, x2, y2): 邊界框的左上角和右下角座標
    """
    # 轉換為絕對座標
    x_center_abs = x_center * img_width
    y_center_abs = y_center * img_height
    width_abs = width * img_width
    height_abs = height * img_height
    
    # 計算左上角和右下角座標
    x1 = int(x_center_abs - width_abs / 2)
    y1 = int(y_center_abs - height_abs / 2)
    x2 = int(x_center_abs + width_abs / 2)
    y2 = int(y_center_abs + height_abs / 2)
    
    # 確保座標在圖片範圍內
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(img_width, x2)
    y2 = min(img_height, y2)
    
    return x1, y1, x2, y2


def crop_shelves_from_dataset(dataset_path, output_path):
    """
    從資料集中裁切所有貨架層
    
    參數:
        dataset_path: 資料集路徑
        output_path: 輸出資料夾路徑
    """
    # 設定路徑
    images_dir = Path(dataset_path) / 'images' / 'train'
    labels_dir = Path(dataset_path) / 'labels' / 'train'
    output_dir = Path(output_path)
    
    # 建立輸出資料夾
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 取得所有圖片檔案
    image_files = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
    
    print(f"找到 {len(image_files)} 張圖片")
    print(f"開始裁切貨架層...")
    
    total_shelves = 0
    
    # 處理每張圖片
    for img_path in tqdm(image_files, desc="處理圖片"):
        # 讀取圖片（支援中文路徑）
        img = imread_unicode(str(img_path))
        if img is None:
            print(f"\n警告: 無法讀取圖片 {img_path.name}")
            continue
            
        img_height, img_width = img.shape[:2]
        
        # 取得對應的標註檔案
        label_path = labels_dir / (img_path.stem + '.txt')
        
        if not label_path.exists():
            print(f"警告: 找不到標註檔案 {label_path}")
            continue
        
        # 讀取標註
        with open(label_path, 'r', encoding='utf-8') as f:
            annotations = f.readlines()
        
        # 處理每個標註框
        for idx, line in enumerate(annotations, start=1):
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            
            # 解析 YOLO 格式
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # 轉換為邊界框座標
            x1, y1, x2, y2 = yolo_to_bbox(x_center, y_center, width, height, 
                                          img_width, img_height)
            
            # 裁切圖片
            cropped = img[y1:y2, x1:x2]
            
            # 檢查裁切結果是否有效
            if cropped.size == 0:
                print(f"警告: 裁切失敗 {img_path.name} 第 {idx} 個標註框")
                continue
            
            # 產生輸出檔名：原始檔名_編號.jpg
            output_filename = f"{img_path.stem}_{idx}{img_path.suffix}"
            output_filepath = output_dir / output_filename
            
            # 儲存裁切後的圖片（支援中文路徑）
            success = imwrite_unicode(str(output_filepath), cropped)
            if success:
                total_shelves += 1
            else:
                print(f"\n警告: 儲存失敗 {output_filename}")
    
    print(f"\n完成！總共裁切了 {total_shelves} 個貨架層")
    print(f"輸出資料夾: {output_dir.absolute()}")


if __name__ == '__main__':
    # 設定輸入和輸出路徑
    dataset_path = '1054_shelf_dataset_v1'
    output_path = 'cropped_shelves'
    
    # 執行裁切
    crop_shelves_from_dataset(dataset_path, output_path)
