import os
import shutil
import uuid
import hashlib

def get_file_hash(filepath):
    """計算檔案的 MD5 哈希值以比較內容是否相同。"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def resolve_conflicts(existing_dirs, new_images_dir, output_dir):
    """
    解決新圖片與舊圖片檔名重複的問題，並檢查內容是否相同。
    
    Args:
        existing_dirs (list): 已訓練或已存在的圖片資料夾列表。
        new_images_dir (str): 待處理的新圖片資料夾。
        output_dir (str): 重新命名或過濾後的圖片輸出位置。
    """
    # 建立輸出目錄
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"建立輸出目錄: {output_dir}")

    # 收集目前所有已存在的檔名及其內容 Hash
    # 格式: { filename: set([hash1, hash2, ...]) }
    existing_files_info = {}
    for d in existing_dirs:
        if os.path.exists(d):
            files = [f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            for f in files:
                filepath = os.path.join(d, f)
                file_hash = get_file_hash(filepath)
                if f not in existing_files_info:
                    existing_files_info[f] = set()
                existing_files_info[f].add(file_hash)
    
    print(f"目前已存在圖片種類數量(依檔名): {len(existing_files_info)}")

    # 處理新圖片
    new_files = [f for f in os.listdir(new_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    renamed_count = 0
    skipped_count = 0
    copied_count = 0

    for filename in new_files:
        src_path = os.path.join(new_images_dir, filename)
        new_hash = get_file_hash(src_path)
        
        target_filename = filename
        
        # 檢查檔名是否重複
        if filename in existing_files_info:
            # 1. 如果檔名相同且內容也相同 -> 跳過（刪除重複意涵）
            if new_hash in existing_files_info[filename]:
                print(f"跳過重複圖片 (名稱與內容皆同): {filename}")
                skipped_count += 1
                continue
            
            # 2. 如果檔名相同但內容不同 -> 重新命名
            suffix = uuid.uuid4().hex[:6]
            base, ext = os.path.splitext(filename)
            target_filename = f"{base}_{suffix}{ext}"
            renamed_count += 1
            print(f"重新命名內容不同之圖片: {filename} -> {target_filename}")
        
        dst_path = os.path.join(output_dir, target_filename)
        shutil.copy2(src_path, dst_path)
        copied_count += 1
        
        # 更新 existing_files_info 以避免新資料夾內也有重複
        if target_filename not in existing_files_info:
            existing_files_info[target_filename] = set()
        existing_files_info[target_filename].add(new_hash)

    print(f"\n處理完成！")
    print(f"總共掃描: {len(new_files)} 張新圖片")
    print(f"複製成功: {copied_count} 張")
    print(f"跳過重複: {skipped_count} 張 (內容與名稱皆相同)")
    print(f"重新命名: {renamed_count} 張 (名稱相同但內容不同)")
    print(f"結果已儲存至: {output_dir}")

if __name__ == "__main__":
    # 使用者可以根據需求修改以下路徑
    CONFIG = {
        "existing_dirs": [
            r"e:\projects\yolo_train\trained\test_shelf_1\images\train",
            r"e:\projects\yolo_train\trained\test_shelf_2_set\images\train"
        ],
        "new_images_dir": r"e:\projects\yolo_train\shelf_test_2",
        "output_dir": r"e:\projects\yolo_train\shelf_test_2_renamed"
    }
    
    resolve_conflicts(
        CONFIG["existing_dirs"], 
        CONFIG["new_images_dir"], 
        CONFIG["output_dir"]
    )
