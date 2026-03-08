import os
import shutil
from pathlib import Path

# ==========================================
# 1. 設定你的資料夾路徑 (請依據實際情況修改)
# ==========================================
# 你的 train.txt 檔案路徑
train_txt_path = Path("/Users/brian/Downloads/task_1_dataset/train.txt")

# 你要被刪除/覆蓋標註的目標資料夾
target_labels_dir = Path("/Users/brian/Downloads/task_1_dataset/labels/train")

# 包含新標註資料的來源資料夾 (你說的"本資料夾的 labels/train/")
source_labels_dir = Path("/Users/brian/Desktop/share_2085_annotations-2/labels/train") 

# ==========================================
# 2. 刪除前 2085 筆標註資料
# ==========================================
print("開始讀取 train.txt 並準備刪除前 2085 筆標註...")

with open(train_txt_path, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

# 取出前 2085 行
lines_to_delete = lines[:2085]
delete_count = 0

for line in lines_to_delete:
    if not line.strip():
        continue
    
    # 從路徑中提取主檔名 (例如 "data/images/frame_0000.jpg" -> "frame_0000")
    base_name = Path(line).stem 
    label_file_to_delete = target_labels_dir / f"{base_name}.txt"
    
    # 如果該 txt 存在，就刪除它
    if label_file_to_delete.exists():
        label_file_to_delete.unlink()
        delete_count += 1
print(f"✅ 成功刪除了 {delete_count} 個舊標註檔。") #確認應該是要已刪除 <= 360個標注檔 （2085 - 1725）有些標注檔本來就不存在，因為它們是背景圖或已經被刪除。

# ==========================================
# 3. 複製新標註並覆蓋
# ==========================================
print("開始複製新標註檔並覆蓋...")
copy_count = 0

# 掃描來源資料夾中所有的 .txt 檔
for new_label in source_labels_dir.glob("*.txt"):
    target_path = target_labels_dir / new_label.name
    
    # .resolve() 會產生完整的絕對路徑
    absolute_target = target_path.resolve()
    
    # 執行複製 (覆蓋)
    shutil.copy2(new_label, target_path)
    copy_count += 1
if copy_count > 0:
    print(f"✅ 成功複製了 {copy_count} 個新標註檔並覆蓋到 {target_labels_dir}！")
    



# 請將這段貼在你的腳本最後
source_files_names = {f.name for f in source_labels_dir.glob("*.txt")}
train_names_all = {Path(line).stem + ".txt" for line in lines}
train_names_first_2085 = {Path(line).stem + ".txt" for line in lines[:2085]}

matched_in_2085 = source_files_names.intersection(train_names_first_2085)
matched_in_all = source_files_names.intersection(train_names_all)

print("\n--- 深度診斷報告 ---")
print(f"1. 你提供的新標註總數: {len(source_files_names)}")
print(f"2. 其中『確實對應到前 2085 行』的數量: {len(matched_in_2085)}")
print(f"3. 其中『雖然不在前 2085 行，但在整份文件裡有出現』的數量: {len(matched_in_all) - len(matched_in_2085)}")
print(f"4. 完全『沒在 train.txt 出現過』的幽靈標註: {len(source_files_names) - len(matched_in_all)}")

if len(matched_in_2085) < len(source_files_names):
    print("\n💡 發現問題：你的新標註檔名，與 train.txt 前 2085 行的圖片名稱不一致！")

    # 1. 算出落在 2085 行之後的標註檔集合
train_names_after_2085 = {Path(line).stem + ".txt" for line in lines[2085:]}
cross_border_files = source_files_names.intersection(train_names_after_2085) - matched_in_2085

# 2. 算出完全沒出現過的標註檔 (雖然你之前的報告是 0)
ghost_files = source_files_names - train_names_all

print("\n" + "="*50)
print(f"📂 詳細清單分析 (總共 {len(cross_border_files)} 個跑過界的檔案)")
print("="*50)

if cross_border_files:
    print(f"\n📍 這些檔案出現在 train.txt 的 2085 行之後 (前 50 筆):")
    # 轉成 list 並排序，方便閱讀
    for i, name in enumerate(sorted(list(cross_border_files))[:50], 1):
        print(f"{i}. {name}")
    
    if len(cross_border_files) > 50:
        print(f"... 以及其他 {len(cross_border_files) - 50} 個檔案。")
else:
    print("\n✅ 沒有發現跑過界的檔案。")

if ghost_files:
    print(f"\n👻 這些檔案完全沒在 train.txt 出現過:")
    for name in sorted(list(ghost_files)):
        print(f"- {name}")

print("\n" + "="*50)