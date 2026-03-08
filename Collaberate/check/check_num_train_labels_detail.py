from pathlib import Path

# 設定資料夾路徑
label_dir = Path("/Users/brian/Desktop/share_2085_annotations-2/labels/train")
# 你的目標檔名 (不含副檔名)
target_file_stem = "單品_DM_6-2DM(傳統寬粉)_187500左營博愛三156_2"

train_txt_path = Path("/Users/brian/Desktop/share_2085_annotations-2/train_top2085.txt")
train_txt_path_original = Path("/Users/brian/Downloads/task_1_dataset/train.txt")
# 組合完整路徑：資料夾 / 檔名 . 副檔名
target_path = label_dir / f"{target_file_stem}.txt"

print(f"🔍 正在檢查檔案：{target_path}")

if target_path.exists():
    print(f"✅ 找到了！檔案存在於：{target_path}")
    found = False
    if train_txt_path.exists():
        # 在 train.txt 中尋找對應的圖片路徑
        with open(train_txt_path, 'r', encoding='utf-8') as f:
            for index, line in enumerate(f):
                # 取得該行的檔名（不含路徑與副檔名）
                line_stem = Path(line.strip()).stem
                
                if line_stem == target_file_stem:
                    # index 是從 0 開始，所以第幾行要 +1
                    print(f"✅ 找到了！")
                    print(f"📍 索引值 (Index): {index}")
                    print(f"📝 實際行數 (Line): {index + 1}")
                    print(f"📄 原始內容: {line.strip()}")
                    found = True
                    break # 找到就停止
        print("-" * 30)
        #找尋原始 train.txt 中是否也有這個檔案路徑
        with open(train_txt_path_original, 'r', encoding='utf-8') as f:
            for index, line in enumerate(f):
                # 取得該行的檔名（不含路徑與副檔名）
                line_stem = Path(line.strip()).stem
                
                if line_stem == target_file_stem:
                    # index 是從 0 開始，所以第幾行要 +1
                    print(f"✅ 在原始 train.txt 中也找到了！")
                    print(f"📍 索引值 (Index): {index}")
                    print(f"📝 實際行數 (Line): {index + 1}")
                    print(f"📄 原始內容: {line.strip()}")
                    found = True
                    break # 找到就停止
    if not found:
        print("❌ 在 train.txt 中找不到對應的圖片路徑。")
else:
    print(f"❌ 找不到該 .txt 標註檔。")