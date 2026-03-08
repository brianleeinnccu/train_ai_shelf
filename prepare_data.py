import os
import random
import shutil
from pathlib import Path
import yaml
from tqdm import tqdm  # 建議加入 tqdm 顯示進度

def create_yolo_subset(
    source_dir,
    output_dir,
    start_idx,
    end_idx,
    train_txt_name="train.txt",
    split_ratio=0.8,
    class_names=None,
    seed=42
):
    """
    從現有的 YOLO 資料集中提取指定範圍 (start_idx ~ end_idx)，
    並重新切分為 Train/Val 資料集。

    Args:
        source_dir (str): 原始資料集根目錄 (內含 images/train, labels/train, train.txt)。
        output_dir (str): 輸出資料集的路徑。
        start_idx (int): 起始索引 (包含)。
        end_idx (int): 結束索引 (不包含)。
        train_txt_name (str): 原始資料夾內的索引檔名，預設 "train.txt"。
        split_ratio (float): 訓練集比例 (0.0 ~ 1.0)，預設 0.8。
        class_names (dict): data.yaml 的類別名稱，預設為 {0: 'product'}。
        seed (int): 隨機種子，確保結果可重現。
    """
    
    # 0. 參數初始化
    if class_names is None:
        class_names = {0: 'product'}
    
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()
    data_txt_path = source_path / train_txt_name

    # 1. 檢查來源
    if not data_txt_path.exists():
        raise FileNotFoundError(f"❌ 錯誤：找不到來源索引檔 {data_txt_path}")

    # 2. 建立輸出目錄結構
    subdirs = [
        output_path / "images" / "train",
        output_path / "images" / "val",
        output_path / "labels" / "train",
        output_path / "labels" / "val"
    ]
    for folder in subdirs:
        folder.mkdir(parents=True, exist_ok=True)

    # 3. 讀取並篩選清單
    print(f"正在讀取 {data_txt_path} ...")
    with open(data_txt_path, "r", encoding="utf-8") as f:
        # 只取檔名，避免路徑干擾
        raw_list = [Path(line.strip()).name for line in f.readlines() if line.strip()]
    
    # 範圍保護：避免 index out of range
    real_end_idx = min(end_idx, len(raw_list))
    target_list = raw_list[start_idx:real_end_idx]
    
    print(f"原始總數: {len(raw_list)}")
    print(f"擷取範圍: {start_idx} ~ {real_end_idx} (共 {len(target_list)} 張)")

    # 4. 驗證檔案存在性
    img_source_dir = source_path / "images" / "train"
    label_source_dir = source_path / "labels" / "train"
    valid_extensions = [".jpg", ".png", ".jpeg", ".bmp"]
    
    valid_samples = []
    
    # 使用 tqdm 顯示進度
    print("正在驗證檔案完整性...")
    for file_name in tqdm(target_list):
        # 處理可能的副檔名問題
        current_img_path = img_source_dir / file_name
        
        # 如果檔案不存在，嘗試其他副檔名 (若 list 中沒有副檔名)
        if not current_img_path.exists():
            stem = Path(file_name).stem
            found = False
            for ext in valid_extensions:
                probe_path = img_source_dir / (stem + ext)
                if probe_path.exists():
                    file_name = stem + ext
                    current_img_path = probe_path
                    found = True
                    break
            if not found:
                # print(f"⚠️ 找不到圖片: {file_name}") # 除錯用
                continue

        # 檢查標籤
        label_name = Path(file_name).stem + ".txt"
        current_label_path = label_source_dir / label_name
        
        if current_img_path.exists() and current_label_path.exists():
            valid_samples.append({
                "img_name": file_name,
                "label_name": label_name,
                "img_src": current_img_path,
                "label_src": current_label_path
            })

    print(f"有效樣本數: {len(valid_samples)} (遺失/不完整: {len(target_list) - len(valid_samples)})")

    # 5. 切分資料集
    random.seed(seed)
    random.shuffle(valid_samples)
    
    split_point = int(len(valid_samples) * split_ratio)
    train_set = valid_samples[:split_point]
    val_set = valid_samples[split_point:]

    # 6. 定義搬運函式 (內部函式)
    def _copy_and_record(sample_list, subset_type):
        """
        subset_type: 'train' or 'val'
        """
        dest_img_dir = output_path / "images" / subset_type
        dest_lbl_dir = output_path / "labels" / subset_type
        txt_record_path = output_path / f"{subset_type}.txt"
        
        record_lines = []
        
        for sample in sample_list:
            # 複製圖片
            shutil.copy2(sample["img_src"], dest_img_dir / sample["img_name"])
            # 複製標籤
            shutil.copy2(sample["label_src"], dest_lbl_dir / sample["label_name"])
            
            # 紀錄絕對路徑
            full_path = dest_img_dir / sample["img_name"]
            record_lines.append(str(full_path))
            
        with open(txt_record_path, "w", encoding="utf-8") as f:
            f.write("\n".join(record_lines))

    print("開始搬運檔案...")
    _copy_and_record(train_set, "train")
    _copy_and_record(val_set, "val")

    # 7. 生成 data.yaml
    data_config = {
        "path": str(output_path),
        "train": "train.txt",
        "val": "val.txt",
        "names": class_names
    }
    
    yaml_path = output_path / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_config, f, allow_unicode=True, sort_keys=False)

    print(f"✅ 資料集建立完成！位置：{output_path}")

# --- 主程式呼叫範例 ---
if __name__ == "__main__":
    # 設定參數
    SOURCE = "/Users/brian/Downloads/task_1_dataset"
    OUTPUT = "./task_1_dataset_v2"  # 輸出到當前目錄下
    start_index = 0
    end_index = 6169
    # 呼叫函式
    create_yolo_subset(
        source_dir=SOURCE,
        output_dir=OUTPUT,
        start_idx=start_index,
        end_idx=end_index,
        train_txt_name="train.txt",
        split_ratio=0.8,
        class_names={0: 'product'}
    )