import random
from ultralytics import YOLO
from pathlib import Path

model = YOLO("yolo11n_sku110k_v1.pt")

input_dir = Path("cropped_shelves")
sample_count = None  # 設定數量，或設為 None 來處理全部圖片

images = list(input_dir.glob("*.jpg"))

# 如果 sample_count 是 None，處理全部圖片；否則隨機抽樣
if sample_count is None or len(images) <= sample_count:
    sampled_images = images
    print(f"處理全部 {len(images)} 張圖片")
else:
    sampled_images = random.sample(images, sample_count)
    print(f"從 {len(images)} 張圖片中隨機抽樣 {sample_count} 張")

# 使用 stream=True 避免結果累積在記憶體中
results = model.predict(sampled_images, conf=0.25, save=True, project="inference_results", name="cropped_shelves_inference", stream=True)

# 逐一處理結果
for r in results:
    pass  # 結果已經保存，不需要額外處理