import pathlib

# 您的資料夾路徑變數
clear_path = pathlib.Path("/Users/brian/product_train_last3085/1500_for_quality/clear")
original_txt = pathlib.Path("/Users/brian/product_train_last3085/task_1_dataset_v2/labels/train")
original_img = pathlib.Path("/Users/brian/product_train_last3085/task_1_dataset_v2/images/train")
# 1. 取得所有清晰圖片的檔名 (例如會拿到 '汽水貨架層', '餅乾貨架層' 等)
# 這裡用 list 儲存，以便後續做「包含」比對
clear_image_names = [img_file.stem for img_file in clear_path.glob('*.jpg')]

kept_count = 0
removed_count = 0

# 2. 檢查 original_txt 資料夾中的所有 .txt 標籤檔
for txt_file in original_txt.glob('*.txt'):
    
    # 核心邏輯：檢查 txt_file.stem (例如 '汽水貨架層_1') 是否「包含」清單中的圖片名稱
    # any() 函數只要比對到一個符合的就會回傳 True
    if any(img_name in txt_file.stem for img_name in clear_image_names):
        # 如果包含，就保留
        kept_count += 1
    else:
        # 如果完全沒有包含任何清晰圖片的名稱，就刪除該標籤檔
        txt_file.unlink() 
        removed_count += 1

print(f"處理完成！")
print(f"✅ 保留了 {kept_count} 個包含清晰圖片名稱的分支標籤檔。")
print(f"🗑️ 刪除了 {removed_count} 個多餘的標籤檔。")

