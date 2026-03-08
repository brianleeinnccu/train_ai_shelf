import os
import shutil
from ultralytics import YOLO
import yaml

def auto_annotate(model_path, images_dir, output_dir, dataset_name="shelf_auto_annotated"):
    """
    使用 YOLO 模型進行自動標註，並整理成 CVAT 可用的 Ultralytics YOLO 格式。
    
    Args:
        model_path (str): 模型檔案路徑 (.pt)。
        images_dir (str): 待標註的圖片資料夾路徑。
        output_dir (str): 結構化輸出的根目錄。
        dataset_name (str): 輸出的子目錄名稱。
    """
    # 1. 載入模型
    model = YOLO(model_path)
    
    # 2. 建立目錄結構
    # CVAT YOLO 格式需要: 
    # output_dir/
    #   data.yaml
    #   images/
    #     train/
    #   labels/
    #     train/
    
    final_images_dir = os.path.join(output_dir, "images", "train")
    final_labels_dir = os.path.join(output_dir, "labels", "train")
    
    os.makedirs(final_images_dir, exist_ok=True)
    os.makedirs(final_labels_dir, exist_ok=True)
    
    print(f"開始推理圖片目錄: {images_dir}...")
    
    # 3. 執行預測
    # save_txt=True 會在 runs/detect/predict/labels 產生 .txt 檔案
    results = model.predict(
        source=images_dir,
        conf=0.25,        # 信心門檻，可以依需求調整
        save_txt=True,    # 儲存 YOLO 格式標籤
        save_conf=False,  # CVAT 通常不需要 conf 值在 txt 內
        project=os.path.join(output_dir, "temp_results"),
        name="predict",
        exist_ok=True
    )
    
    # 4. 搬移標籤並複製圖片
    temp_labels_path = os.path.join(output_dir, "temp_results", "predict", "labels")
    
    # 獲取模型類別定義
    class_names = model.names
    
    # 列出所有推理成功的圖片 (Ultralytics 只會為有偵測到物品的圖片產生 txt，除非設定 save_hybrid=True)
    # 為了確保 CVAT 對齊，我們需要對每一張圖片都進行處理
    all_images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    processed_count = 0
    for img_name in all_images:
        base_name = os.path.splitext(img_name)[0]
        label_name = base_name + ".txt"
        
        # 複製圖片到 images/train
        shutil.copy2(os.path.join(images_dir, img_name), os.path.join(final_images_dir, img_name))
        
        # 搬移對應的標籤到 labels/train
        src_label = os.path.join(temp_labels_path, label_name)
        dst_label = os.path.join(final_labels_dir, label_name)
        
        if os.path.exists(src_label):
            shutil.copy2(src_label, dst_label)
        else:
            # 如果沒有偵測到物件，建立一個空的 txt (CVAT 有時需要對應的空檔案，視情況而定)
            open(dst_label, 'a').close()
            
        processed_count += 1

    # 5. 生成 data.yaml
    data_yaml = {
        "path": ".",
        "train": "images/train",
        "val": "images/train",  # CVAT 匯入通常沒差，可以指向同一個
        "names": class_names
    }
    
    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml, f, allow_unicode=True, sort_keys=False)
    
    # 6. 清理臨時結果
    shutil.rmtree(os.path.join(output_dir, "temp_results"))
    
    print(f"\n自動標註完成！")
    print(f"處理圖片數: {processed_count}")
    print(f"結果儲存於: {output_dir}")
    print(f"提示：您可以將 {output_dir} 目錄內的內容打包成 ZIP，上傳至 CVAT 的 'Upload annotation'。")

if __name__ == "__main__":
    # 設定參數
    MODEL_FILE = "/Users/brian/product_train_last3085/runs/detect/shelf_finetune_v26_v1_3343/weights/best.pt"
    INPUT_IMAGES = "/Users/brian/Downloads/task_1_dataset/images/train" # 使用您改名後的資料夾
    OUTPUT_FOLDER = "/Users/brian/projects/product_train_last3085/product_auto_annotated"

    auto_annotate(MODEL_FILE, INPUT_IMAGES, OUTPUT_FOLDER)
