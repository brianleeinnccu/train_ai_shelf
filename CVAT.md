## 影像標註用 cvat

### 安裝說明網址:
https://docs.cvat.ai/docs/administration/community/basics/installation/

- 通常會用 docker
- 在容器啟動後通常運行在: http://localhost:8080

## 簡單操作說明
### project
- 首頁長這樣
![alt text](mdimage\image1.png)

- 按右上 + 新增 project
![alt text](mdimage\image2.png)
- 設定 project name
- 下面 constructor 新增 label，應該只會用單個類別 product，選個顏色
- 然後就 submit

### task
- 進來 project 後長這樣
![alt text](mdimage\image3.png)
- 從零開始應該要先右下 create a new task
- 然後上傳你的照片

### job
- 從 task 下 job 進來長這樣，這是標註操作畫面
![alt text](mdimage\image4.png)
- 基本上我們專案應該都是用矩形，**不旋轉!!**
- 基礎操作:
    - N: 新框
    - F: 下一張
    - N: 上一張
    - delete/backspace: 刪除選取的匡
    - **ctrl + s: 存檔!!**

- 把目標(如: 價格牌)框出來
![alt text](mdimage\image5.png)
- 不完整的、嚴重被遮擋的就先不框
- 記得存檔，或去設定開自動存檔
- 建議可以標註 50-100 張，先訓練一個模型，再用那個模型去自動標註，自動標註完再回到 CVAT 人工檢查、修改
- 可以從 task 頁面 export dataset，如果要一次把所有 task 都匯出，可以去 project 頁面 export dataset
- export 的時候建議選 save images 這樣程式處理比較簡單