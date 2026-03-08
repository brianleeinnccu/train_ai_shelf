from ultralytics import YOLO
import json

# 加載模型
model = YOLO(r'E:\projects\product_train\yolo11n_SKU110k_v1.pt')

print("=" * 80)
print("模型基本資訊")
print("=" * 80)

# 1. 查看模型結構
print("\n1. 模型架構:")
model.info()

# 2. 查看模型名稱和類別
print("\n2. 模型資訊:")
print(f"   模型名稱: {model.model_name}")
print(f"   任務類型: {model.task}")
print(f"   類別數量: {model.model.nc if hasattr(model.model, 'nc') else 'N/A'}")

# 3. 查看類別名稱
print("\n3. 類別名稱:")
if hasattr(model, 'names'):
    for class_id, class_name in model.names.items():
        print(f"   [{class_id}] {class_name}")

# 4. 最佳訓練結果
print("\n4. 最佳訓練結果:")
if 'train_results' in model.ckpt:
    results = model.ckpt['train_results']
    # 找出最佳 mAP50-95 對應的 epoch
    if 'metrics/mAP50-95(B)' in results:
        map_scores = results['metrics/mAP50-95(B)']
        best_idx = map_scores.index(max(map_scores))
        best_epoch = results['epoch'][best_idx]
        print(f"   最佳輪數 (epoch): {best_epoch + 1}")
        print(f"   mAP50-95: {map_scores[best_idx]:.4f}")
        print(f"   mAP50: {results['metrics/mAP50(B)'][best_idx]:.4f}")
        print(f"   精準度 (Precision): {results['metrics/precision(B)'][best_idx]:.4f}")
        print(f"   召回率 (Recall): {results['metrics/recall(B)'][best_idx]:.4f}")

# 5. 模型大小和參數
print("\n5. 模型參數:")
if hasattr(model.model, 'parameters'):
    total_params = sum(p.numel() for p in model.model.parameters())
    print(f"   總參數數: {total_params:,}")

print("\n" + "=" * 80)