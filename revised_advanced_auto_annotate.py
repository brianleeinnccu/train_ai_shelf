import os
import shutil
from ultralytics import YOLO
import yaml
from tqdm import tqdm

def auto_annotate_all_except_range(
    model_path, 
    images_dir, 
    source_labels_dir, 
    output_dir, 
    train_list_path, 
    protect_start_idx, 
    protect_end_idx
):
    print(f"🔄 正在載入模型: {model_path} ...")
    model = YOLO(model_path)
    
    final_images_dir = os.path.join(output_dir, "images", "train")
    final_labels_dir = os.path.join(output_dir, "labels", "train")
    os.makedirs(final_images_dir, exist_ok=True)
    os.makedirs(final_labels_dir, exist_ok=True)

    # 讀取清單
    with open(train_list_path, 'r') as f:
        all_lines = [line.strip().split('/')[-1] for line in f.readlines() if line.strip()]
    
    total_imgs = len(all_lines)
    print(f"📊 總圖片數: {total_imgs}")
    
    # === 為了 Debug，我們設定一個計數器 ===
    count_skipped = 0
    count_protected = 0
    count_predicted = 0
    count_empty_predict = 0

    for i, img_name in enumerate(tqdm(all_lines, desc="Processing")):
        
        base_name = os.path.splitext(img_name)[0]
        label_filename = base_name + ".txt"
        
        src_img_path = os.path.join(images_dir, img_name)
        src_label_path = os.path.join(source_labels_dir, label_filename)
        
        dst_img_path = os.path.join(final_images_dir, img_name)
        dst_label_path = os.path.join(final_labels_dir, label_filename)

        # DEBUG 1: 檢查圖片路徑是否正確
        if not os.path.exists(src_img_path):
            # 只有前幾次錯誤會印出來，避免洗版
            if count_skipped < 3:
                print(f"⚠️ [找不到圖片] 路徑錯誤: {src_img_path}")
            count_skipped += 1
            continue

        shutil.copy2(src_img_path, dst_img_path)

        # 判斷保護區間
        end_boundary = protect_end_idx if protect_end_idx is not None else total_imgs
        is_protected = (protect_start_idx <= i < end_boundary)

        if is_protected:
            count_protected += 1
            if os.path.exists(src_label_path):
                shutil.copy2(src_label_path, dst_label_path)
            else:
                open(dst_label_path, 'a').close()
        else:
            # === 自動標註區間 ===
            count_predicted += 1
            
            # 執行預測
            # 這裡把 conf 調低一點 (0.1) 測試看看是否因為門檻太高
            results = model.predict(
                source=src_img_path,
                conf=0.1,         # <--- 暫時調低信心度，看有沒有東西
                iou=0.45,
                save_txt=True,
                project=os.path.join(output_dir, "temp_results"),
                name="predict",
                exist_ok=True,
                verbose=False
            )
            
            # 取得預測路徑
            # YOLO v8 的 labels 預設在 project/name/labels 底下
            generated_label = os.path.join(output_dir, "temp_results", "predict", "labels", label_filename)
            
            if os.path.exists(generated_label):
                shutil.copy2(generated_label, dst_label_path)
            else:
                # DEBUG 2: 模型跑了但沒產生檔案 -> 代表沒偵測到任何東西
                # print(f"ℹ️ [無偵測結果] {img_name} (建立空檔)") 
                count_empty_predict += 1
                open(dst_label_path, 'a').close()

    # 生成 data.yaml
    data_yaml = {
        "path": os.path.abspath(output_dir), # 使用絕對路徑比較安全
        "train": "images/train",
        "val": "images/train",
        "names": model.names
    }
    with open(os.path.join(output_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(data_yaml, f, allow_unicode=True, sort_keys=False)

    # 清理暫存
    temp_dir = os.path.join(output_dir, "temp_results")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    print(f"\n{'='*30}")
    print(f"✅ 處理完成！統計如下：")
    print(f"❌ 找不到圖片 (Skipped): {count_skipped} (若此數字很大，請檢查圖片路徑)")
    print(f"🛡️ 保護區間 (Protected): {count_protected}")
    print(f"🤖 執行預測 (Predicted): {count_predicted}")
    print(f"💨 預測為空 (No Detection): {count_empty_predict} (若此數字接近 '執行預測' 總數，代表模型什麼都沒抓到)")
    print(f"📁 輸出位置: {output_dir}")
    print(f"{'='*30}")

if __name__ == "__main__":
    MODEL_FILE = "/Users/brian/product_train_last3085/runs/detect/shelf_finetune_v26_v1_3343/weights/best.pt"
    INPUT_IMAGES_DIR = "/Users/brian/Downloads/task_1_dataset/images/train"
    EXISTING_LABELS_DIR = "/Users/brian/Downloads/task_1_dataset/labels/train"
    OUTPUT_FOLDER = "./auto_annotated_results"
    TRAIN_LIST = "/Users/brian/Downloads/task_1_dataset/train.txt"

    PROTECT_START = 4170
    PROTECT_END = 4810

    auto_annotate_all_except_range(
        model_path=MODEL_FILE, 
        images_dir=INPUT_IMAGES_DIR, 
        source_labels_dir=EXISTING_LABELS_DIR, 
        output_dir=OUTPUT_FOLDER, 
        train_list_path=TRAIN_LIST, 
        protect_start_idx=PROTECT_START,
        protect_end_idx=PROTECT_END
    )