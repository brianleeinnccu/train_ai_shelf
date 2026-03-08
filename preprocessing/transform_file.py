import os
import unicodedata

def try_fix_filename(filename):
    """
    嘗試還原亂碼檔名
    """
    filename_nfc = unicodedata.normalize('NFC', filename)
    encodings = ['cp437', 'iso-8859-1', 'cp1252', 'latin1', 'mac_roman']

    for enc in encodings:
        try:
            raw_bytes = filename_nfc.encode(enc)
            decoded = raw_bytes.decode('utf-8')
            if decoded != filename:
                return True, decoded, enc
        except Exception:
            continue
    return False, filename, None

def process_inplace_rename(src_root):
    """
    遞迴遍歷資料夾，直接在原地更名（覆蓋）
    """
    success_count = 0
    skip_count = 0
    fail_count = 0

    print(f"🚀 開始原地更名：{src_root}\n")

    # 使用 topdown=False 是為了先改子目錄檔案，再改目錄名稱，避免路徑失效
    for root, dirs, files in os.walk(src_root, topdown=False):
        
        for filename in files:
            if filename.startswith('.'): # 跳過隱藏檔
                continue

            is_fixed, new_filename, method = try_fix_filename(filename)
            
            if is_fixed:
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)

                try:
                    # 如果目標檔名已存在，先刪除舊的或直接覆蓋
                    if os.path.exists(new_path) and old_path != new_path:
                        os.remove(new_path) 
                    
                    os.rename(old_path, new_path)
                    print(f"[成功] {filename} -> {new_filename}")
                    success_count += 1
                except Exception as e:
                    print(f"[失敗] {filename}: {e}")
                    fail_count += 1
            else:
                skip_count += 1

    print(f"\n{'='*50}")
    print(f"✅ 處理完成！")
    print(f"🛠️  成功更名：{success_count} 個檔案")
    print(f"📄 無需變動：{skip_count} 個檔案")
    print(f"❌ 出錯：{fail_count} 個檔案")
    print(f"{'='*50}")
