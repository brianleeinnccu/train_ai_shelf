import os

# 你的清單檔案路徑
file_list_path = '/Users/brian/Desktop/share_2085_annotations-2/train_top2085.txt'

if os.path.exists(file_list_path):
    with open(file_list_path, 'r', encoding='utf-8') as f:
        # 讀取每一行，並去掉前後的換行符號與空白
        lines = [line.strip() for line in f.readlines()]
    
    # 篩選出純粹以 .jpg 結尾的行（排除掉空行）
    jpg_files = [line for line in lines if line.lower().endswith('.jpg')]

    print(f"清單檔案中紀錄了 {len(jpg_files)} 個 .jpg 檔案")
else:
    print(f"錯誤：找不到檔案 {file_list_path}")