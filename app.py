import os
import subprocess
import time
import json
import pandas as pd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

EXCEL_PATH = r"C:\Users\Administrator\Desktop\Book3.xlsx"
JSON_PATH = "data.json"
HTML_PATH = "index.html"
STYLE_PATH = "style.css"
APP_PATH = "app.js"
GIT_BRANCH = "main"

def update_json_from_excel():
    print(f"[INFO] Processing {EXCEL_PATH}...")
    try:
        excel_data = pd.read_excel(EXCEL_PATH, sheet_name=None)
        data_dict = {sheet: df.fillna("-").to_dict(orient="records") for sheet, df in excel_data.items()}
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=4)
        print(f"[INFO] data.json generated successfully at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[ERROR] Excel export failed: {e}")

class ExcelSyncHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(EXCEL_PATH):
            current_time = time.time()
            if current_time - self.last_modified > 5:
                self.last_modified = current_time
                print(f"\n[DETECTED] Changes saved in {EXCEL_PATH}!")
                update_json_from_excel()
                try:
                    repo_dir = os.path.dirname(EXCEL_PATH)
                    subprocess.run(["git", "add", EXCEL_PATH, JSON_PATH, HTML_PATH, STYLE_PATH, APP_PATH], cwd=repo_dir, check=True)
                    subprocess.run(["git", "commit", "-m", f"Auto-sync live data: {time.strftime('%Y-%m-%d %H:%M:%S')}"], cwd=repo_dir, check=True)
                    subprocess.run(["git", "push", "origin", GIT_BRANCH], cwd=repo_dir, check=True)
                    print("[SUCCESS] Live update pushed to GitHub!\n")
                except subprocess.CalledProcessError as err:
                    print(f"[ERROR] Git sync failed: {err}")

if __name__ == "__main__":
    path = os.path.dirname(EXCEL_PATH)
    event_handler = ExcelSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    print(f"[*] Live sync watcher active for '{EXCEL_PATH}'...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()