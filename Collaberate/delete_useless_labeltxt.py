from pathlib import Path
import os 
# ==========================================
# 1. 設定你的資料夾與檔案路徑
# ==========================================
train_txt_path = Path("/Users/brian/Downloads/task_1_dataset/train.txt")
target_labels_dir = Path("/Users/brian/Downloads/task_1_dataset/labels/train")

# ==========================================
# 2. 設定你要刪除的 ID 範圍 (根據 train.txt 的行數)
# ==========================================
# ⚠️ 注意：Python 的計數是從 0 開始的！
# 假設你要刪除第 1 筆到第 2085 筆，設定如下：
#0 ~ 2084 (共 2085 筆)
#2085 ~ 4169 (共 2085 筆)
#4170 ~ 6169 (共 2085 筆)
start_id = 2085      # 起始位置 (包含)
end_id = 4170     # 結束位置 (不包含此行，所以會刪除 0 ~ 2084，共 2085 筆)

# ==========================================
# 3. 開始執行刪除
# ==========================================
print(f"📂 準備讀取 train.txt...")

with open(train_txt_path, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

# 檢查一下設定的範圍有沒有超出檔案總行數
total_lines = len(lines)
print(f"總共有 {total_lines} 筆圖片資料。")
print(f"🎯 準備刪除範圍：從 index {start_id} 到 {end_id} 的標註檔...\n")

# 利用 [start_id:end_id] 切出你要的範圍
lines_to_delete = lines[start_id:end_id]
delete_count = 0
not_found_count = 0

for line in lines_to_delete:
    if not line.strip():
        continue
    
    # 抓出檔名，去找對應的 txt
    base_name = Path(line).stem 
    label_file_to_delete = target_labels_dir / f"{base_name}.txt"
    
    # 如果檔案存在，就刪除它
    if label_file_to_delete.exists():
        label_file_to_delete.unlink()
        delete_count += 1
    else:
        # 如果本來就沒有這個標註檔 (例如它本來就是背景圖)
        not_found_count += 1

# ==========================================
# 4. 顯示結果
# ==========================================
print("-" * 30)
print("✅ 刪除任務完成！")
print(f"🗑️  成功刪除了 {delete_count} 個標註檔。") #360 2085 200
print(f"👻 有 {not_found_count} 個標註檔原本就不存在 (可能是背景圖或已刪除)。")

path = '/Users/brian/Downloads/task_1_dataset/labels/train'
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

print(f"總共有 {len(files)} 個檔案") 