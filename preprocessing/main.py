from transform_file import process_inplace_rename
from transform_txt import start_fix

if __name__ == "__main__":

    #第一步驟：修復亂碼檔案名稱與內容
    SOURCE = "/Users/brian/Downloads/task_1_dataset"
    try:
        start_fix(SOURCE)
        train_image = '/images/train'
        train_label = '/labels/train'
        process_inplace_rename(SOURCE + train_image)
        process_inplace_rename(SOURCE + train_label)
    except Exception as e:
        print(f"❌ 第一步驟：debug發生錯誤: {e}")