
import os
import unicodedata
from transform_file import process_inplace_rename
# --- 設定區 ---
# 填入你的資料夾路徑
# ---------------------------

def fix_mojibake(text):
    """
    修復亂碼文字的核心邏輯
    """
    text_nfc = unicodedata.normalize('NFC', text)
    encodings = ['cp437', 'iso-8859-1', 'cp1252', 'latin1', 'mac_roman']
    for enc in encodings:
        try:
            raw_bytes = text_nfc.encode(enc)
            decoded = raw_bytes.decode('utf-8')
            if decoded != text:
                return True, decoded
        except Exception:
            continue
    return False, text

def start_fix(directory):
    print("🚀 開始原地修復亂碼檔案內容 🚀")
    
    # 找出所有 txt
    txt_files = [f for f in os.listdir(directory) if f.lower().endswith('.txt')]

    for filename in txt_files:
        path = os.path.join(directory, filename)
        
        try:
            # --- 步驟 1: 先全部讀進記憶體 ---
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # --- 步驟 2: 在記憶體中處理內容 ---
            fixed_lines = [fix_mojibake(line)[1] for line in lines]

            # --- 步驟 3: 關閉讀取後，再重新打開寫入 (覆蓋) ---
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            # --- 步驟 4: 最後才改檔名 (避免路徑迷失) ---
            success, new_filename = fix_mojibake(filename)
            if success:
                new_path = os.path.join(directory, new_filename)
                os.rename(path, new_path) # 改名
                print(f"✅ 已覆蓋並更名: {new_filename}")
            else:
                print(f"✅ 已覆蓋內容: {filename}")

        except Exception as e:
            print(f"❌ 處理 {filename} 失敗: {e}")

