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
    protect_end_idx,
    conf_threshold=0.25  # 預設信心度
):
    print(f"🔄 正在載入模型: {model_path} ...")
    model = YOLO(model_path)
    
    # 建立輸出目錄
    final_images_dir = os.path.join(output_dir, "images", "train")
    final_labels_dir = os.path.join(output_dir, "labels", "train")
    os.makedirs(final_images_dir, exist_ok=True)
    os.makedirs(final_labels_dir, exist_ok=True)

    # 讀取 train.txt
    print(f"📖 讀取清單: {train_list_path}")
    with open(train_list_path, 'r') as f:
        all_lines = [line.strip().split('/')[-1] for line in f.readlines() if line.strip()]
    
    total_imgs = len(all_lines)
    end_boundary = protect_end_idx if protect_end_idx is not None else total_imgs

    print(f"📊 總圖片數: {total_imgs}")
    print(f"🛡️ 保護區間 (保留原標籤): {protect_start_idx} ~ {end_boundary}")
    print(f"🤖 自動標註區間: 其餘部分 (Conf={conf_threshold})")

    # 統計變數
    stats = {
        "protected": 0,
        "predicted": 0,
        "empty_prediction": 0, # 模型真的什麼都沒看到
        "skipped_no_image": 0
    }

    for i, img_name in enumerate(tqdm(all_lines, desc="Processing")):
        
        base_name = os.path.splitext(img_name)[0]
        label_filename = base_name + ".txt"
        
        src_img_path = os.path.join(images_dir, img_name)
        src_label_path = os.path.join(source_labels_dir, label_filename)
        
        dst_img_path = os.path.join(final_images_dir, img_name)
        dst_label_path = os.path.join(final_labels_dir, label_filename)

        # 1. 檢查圖片是否存在
        if not os.path.exists(src_img_path):
            stats["skipped_no_image"] += 1
            continue

        # 2. 複製圖片 (必定執行)
        shutil.copy2(src_img_path, dst_img_path)

        # 3. 判斷是否在保護區間
        is_protected = (protect_start_idx <= i < end_boundary)

        if is_protected:
            # === [保護模式] 保留人工標籤 ===
            stats["protected"] += 1
            if os.path.exists(src_label_path):
                shutil.copy2(src_label_path, dst_label_path)
            else:
                # 雖然在保護區但沒標籤，建立空檔
                open(dst_label_path, 'a').close()
        else:
            # === [自動模式] 跑模型 ===
            
            # 使用 stream=False 確保一次處理一張並回傳結果
            results = model.predict(
                source=src_img_path,
                conf=conf_threshold,
                iou=0.45,
                verbose=False
            )
            
            result = results[0] # 取得單張結果
            
            if len(result.boxes) > 0:
                # --- 有抓到東西，寫入 txt ---
                stats["predicted"] += 1
                with open(dst_label_path, 'w') as f_out:
                    for box in result.boxes:
                        # 取得 class id
                        cls_id = int(box.cls[0])
                        # 取得 normalized xywh (x_center, y_center, width, height)
                        x, y, w, h = box.xywhn[0].tolist()
                        
                        # 寫入格式: class x y w h
                        f_out.write(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
            else:
                # --- 沒抓到東西 (空) ---
                stats["empty_prediction"] += 1
                # 建立空檔 (非常重要，否則訓練程式會報錯找不到標籤檔)
                open(dst_label_path, 'a').close()

    # 生成 data.yaml
    data_yaml = {
        "path": os.path.abspath(output_dir),
        "train": "images/train",
        "val": "images/train",
        "names": model.names
    }
    with open(os.path.join(output_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(data_yaml, f, allow_unicode=True, sort_keys=False)

    print(f"\n{'='*30}")
    print(f"✅ 處理完成！")
    print(f"📁 輸出目錄: {output_dir}")
    print(f"------------------------------")
    print(f"🛡️ 保留人工標籤: {stats['protected']} 張")
    print(f"🤖 模型成功預測: {stats['predicted']} 張 (有框)")
    print(f"💨 模型預測為空: {stats['empty_prediction']} 張 (無框 -> 產生空txt)")
    print(f"❌ 找不到圖片檔: {stats['skipped_no_image']} 張")
    print(f"{'='*30}")
    
    # 提醒使用者
    if stats['predicted'] == 0 and stats['empty_prediction'] > 0:
        print("⚠️ 警告：自動標註區間的所有圖片都沒有抓到任何物件！")
        print("   建議：請檢查模型是否載入正確，或將 conf_threshold 調低 (例如 0.1)。")

if __name__ == "__main__":
    # === 參數設定 ===
    MODEL_FILE = "/Users/brian/product_train_last3085/runs/detect/shelf_finetune_v26_v1_3345/weights/best.pt"
    INPUT_IMAGES = "/Users/brian/Downloads/task_1_dataset/images/train"
    EXISTING_LABELS = "/Users/brian/Downloads/task_1_dataset/labels/train"
    TRAIN_LIST = "/Users/brian/Downloads/task_1_dataset/train.txt"
    OUTPUT_FOLDER = "./auto_annotated_results_v2" # 改個名字避免混淆

    # 設定保留區間
    PROTECT_START = 4172
    PROTECT_END = 5240

    # 執行
    auto_annotate_all_except_range(
        model_path=MODEL_FILE, 
        images_dir=INPUT_IMAGES, 
        source_labels_dir=EXISTING_LABELS, 
        output_dir=OUTPUT_FOLDER, 
        train_list_path=TRAIN_LIST, 
        protect_start_idx=PROTECT_START,
        protect_end_idx=PROTECT_END,
        conf_threshold=0.15  # <--- 這裡可以調低，如果模型比較弱，設 0.1 或 0.05
    )