from pathlib import Path

# 設定路徑
train_txt_path = Path("/Users/brian/Desktop/share_2085_annotations-2/train_top2085.txt")
target_file_stem = "單品_DM_6-2DM(傳統寬粉)_187500左營博愛三156_2" # 去掉 .txt

print(f"🔍 正在搜尋：{target_file_stem} ...")

found = False
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

if not found:
    print("❌ 在 train.txt 中找不到對應的圖片路徑。")