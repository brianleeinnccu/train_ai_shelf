import os

# 設定你的路徑
path = '/Users/brian/Downloads/task_1_dataset/labels/train'
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

print(f"總共有 {len(files)} 個檔案")