主要程式檔案：
  - prepare_data.py: 資料準備與切分（訓練集/驗證集）
  - train.py: YOLO 模型訓練主程式
  - auto_annotate.py: 使用訓練好的模型進行自動標註
  - resolve_conflicts.py: 解決新舊圖片檔名重複問題

資料目錄：
  - trained/: 已訓練的資料集
  - runs/: 訓練結果與偵測輸出

完整工作流程
------------

步驟 1: 準備新圖片
  - 將待訓練的圖片放入專案目錄（例如：product/）
  - 重要：確保圖片檔名有意義且不重複

步驟 2: 解決檔名衝突（如有需要）
  - 編輯 resolve_conflicts.py 中的 CONFIG 設定
  - 修改 existing_dirs（已存在的圖片資料夾列表）
  - 修改 new_images_dir（新圖片資料夾）
  - 修改 output_dir（處理後的輸出資料夾）
  - 執行: python resolve_conflicts.py
  
  功能說明：
    - 比對新圖片與舊圖片的檔名和內容
    - 檔名相同且內容相同 -> 跳過（避免重複）
    - 檔名相同但內容不同 -> 自動重新命名（加上隨機後綴）
    - 檔名不同 -> 直接複製

步驟 3: 自動標註（若有現有模型）
  - 編輯 auto_annotate.py 中的參數
  - 修改 MODEL_FILE（模型路徑，例如：yolo11n_sku110k_v1.pt）
  - 修改 INPUT_IMAGES（新圖片資料夾）
  - 修改 OUTPUT_FOLDER（輸出資料夾，例如：cvat_upload_package_1）
  - 執行: python auto_annotate.py
  
  輸出格式（CVAT Ultralytics YOLO 格式）：
    cvat_upload_package/
      data.yaml
      images/train/（所有圖片）
      labels/train/（所有標籤檔）

步驟 4: 上傳至 CVAT 進行人工審核
  - 將輸出資料夾（cvat_upload_package）壓縮成 ZIP
  - 在 CVAT 中建立新 project
  - 選擇 import dataset -> 選擇格式 Ultralytics YOLO detection 1.0
  - 上傳 ZIP 檔案
  - 人工檢查並修正標註錯誤

步驟 5: 從 CVAT 匯出標註
  - 在 CVAT 完成標註後，匯出為 Ultralytics YOLO detection 1.0 格式
  - 解壓縮到專案目錄（例如：product_train/）

步驟 6: 準備訓練資料
  - 編輯 prepare_data.py 中的路徑
  - 修改 base_dir（指向你的資料集目錄，例如：product_train）
  - 執行: python prepare_data.py
  
  功能說明：
    - 設定好訓練需要的格式
    - 自動切分訓練集與驗證集（8:2 比例）

步驟 7: 訓練模型
  - 編輯 train.py 中的參數
  - 修改 data 路徑（指向 data.yaml）
  - 修改 epochs（訓練輪數，50-100 適合微調）
  - 修改 batch（批次大小，依 GPU 記憶體調整）
  - 修改 name（輸出資料夾名稱，例如：pricetag_finetune_v1）
  - 執行: python train.py
  
  訓練參數說明：
    - epochs: 訓練輪數（50-100 適合微調）
    - imgsz: 輸入圖片大小（640 是標準尺寸）
    - batch: 批次大小（依 GPU 記憶體調整，16/32 常見）
    - device: 0 使用 GPU，cpu 使用 CPU
    - mosaic, mixup, fliplr: 資料增強（提升泛化能力）

步驟 8: 評估與使用模型
  - 訓練完成後，模型會儲存在 runs/detect/[name]/weights/best.pt
  - 可以使用此模型進行新一輪自動標註（回到步驟 3）
  - 或部署到生產環境進行實際偵測


重要注意事項
------------

檔案命名規則：
  1. python 程式中，必須使用絕對路徑
     如：e:\projects\yolo_train\shelf_test
     否則 yolo 的程式會忽略中文，會出錯
  
環境需求
--------
  pip install -U ultralytics