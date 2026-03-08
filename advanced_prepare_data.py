import os
import random
import shutil
from pathlib import Path
import yaml
from tqdm import tqdm

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
    從 YOLO 資料集中提取子集，並列出所有遺失標籤的檔案。
    """
    if class_names is None:
        class_names = {0: 'product'}
    
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()
    data_txt_path = source_path / train_txt_name

    if not data_txt_path.exists():
        raise FileNotFoundError(f"❌ 錯誤：找不到來源索引檔 {data_txt_path}")

    # 1. 建立輸出目錄結構
    subdirs = [
        output_path / "images" / "train", output_path / "images" / "val",
        output_path / "labels" / "train", output_path / "labels" / "val"
    ]
    for folder in subdirs:
        folder.mkdir(parents=True, exist_ok=True)

    # 2. 讀取清單
    with open(data_txt_path, "r", encoding="utf-8") as f:
        raw_list = [line.strip() for line in f.readlines() if line.strip()]
    
    real_end_idx = min(end_idx, len(raw_list))
    target_list = raw_list[start_idx:real_end_idx]
    
    print(f"📊 原始總數: {len(raw_list)} | 預計處理範圍: {start_idx} ~ {real_end_idx} (共 {len(target_list)} 筆)")

    valid_samples = []
    missing_images = []
    missing_labels = []

    # 3. 驗證完整性
    print("🔍 正在檢查檔案與標籤...")
    for item in tqdm(target_list):
        # 處理圖片路徑：嘗試 1. 原始路徑 2. 相對於 source_dir 3. images/train 內
        p = Path(item)
        potential_img_paths = [
            p,
            source_path / p,
            source_path / "images" / "train" / p.name
        ]
        
        img_src = None
        for path in potential_img_paths:
            if path.exists() and path.is_file():
                img_src = path
                break
        
        if img_src is None:
            missing_images.append(item)
            continue

        # 定位標籤：通常在 labels/train/ 下，且副檔名為 .txt
        label_name = img_src.stem + ".txt"
        potential_label_paths = [
            img_src.parents[2] / "labels" / img_src.parent.name / label_name, # 標準結構
            source_path / "labels" / "train" / label_name,                  # 指定結構
            source_path / "labels" / label_name                            # 根目錄結構
        ]

        label_src = None
        for lp in potential_label_paths:
            if lp.exists():
                label_src = lp
                break

        if label_src:
            valid_samples.append({
                "img_name": img_src.name,
                "label_name": label_name,
                "img_src": img_src,
                "label_src": label_src
            })
        else:
            missing_labels.append(img_src.name)

    # --- 4. 印出詳細遺失報告 ---
    if missing_images:
        print(f"\n❌ 找不到圖片檔案 (共 {len(missing_images)} 筆):")
        for img in missing_images[:10]: print(f"  - {img}")
        if len(missing_images) > 10: print("    ...")

    if missing_labels:
        print(f"\n⚠️ 圖片存在但【找不到標籤】(共 {len(missing_labels)} 筆):")
        for lbl in missing_labels[:210]:  # 設定印出數量
            print(f"  - {lbl} (缺少: {Path(lbl).stem}.txt)")
        if len(missing_labels) > 210: print(f"    ... 還有 {len(missing_labels)-210} 筆")

    print(f"\n✅ 檢查完成。有效樣本: {len(valid_samples)} / 總計: {len(target_list)}")

    # 5. 切分資料並搬運
    if not valid_samples:
        print("停止操作：沒有有效的樣本可以搬運。")
        return

    random.seed(seed)
    random.shuffle(valid_samples)
    split_p = int(len(valid_samples) * split_ratio)
    
    dataset_splits = {
        "train": valid_samples[:split_p],
        "val": valid_samples[split_p:]
    }

    for mode, samples in dataset_splits.items():
        print(f"📦 正在搬運 {mode} 組 ({len(samples)} 筆)...")
        img_dest_dir = output_path / "images" / mode
        lbl_dest_dir = output_path / "labels" / mode
        txt_record = []

        for s in tqdm(samples, leave=False):
            shutil.copy2(s["img_src"], img_dest_dir / s["img_name"])
            shutil.copy2(s["label_src"], lbl_dest_dir / s["label_name"])
            # 儲存相對路徑供 train.txt 使用
            txt_record.append(f"./images/{mode}/{s['img_name']}")
        
        with open(output_path / f"{mode}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(txt_record))

    # 6. 生成 data.yaml
    with open(output_path / "data.yaml", "w", encoding="utf-8") as f:
        yaml.dump({
            "path": str(output_path),
            "train": "train.txt",
            "val": "val.txt",
            "names": class_names
        }, f, sort_keys=False, allow_unicode=True)

    print(f"\n🎉 任務完成！子集已儲存至: {output_path}")

if __name__ == "__main__":
    create_yolo_subset(
        source_dir="/Users/brian/Downloads/task_1_dataset",
        output_dir="./task_1_dataset_v2",
        start_idx=4171,
        end_idx=6169,
        class_names={0: 'product'}
    )