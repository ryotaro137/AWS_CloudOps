import os
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader, PdfWriter

# ==========================
# 設定
# ==========================
URL_FILE = "urls.txt"
DOWNLOAD_DIR = "downloads"
MERGED_OUTPUT = "BlackBelt_Config.pdf"
MAX_WORKERS = 5
TIMEOUT = 60

# ==========================
# ダウンロード
# ==========================
def download_file(url):
    try:
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        if os.path.exists(filepath):
            return filepath, f"[SKIP] {filename}"

        response = requests.get(url, stream=True, timeout=TIMEOUT)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        return filepath, f"[OK] {filename}"

    except Exception as e:
        return None, f"[ERROR] {url} -> {e}"

# ==========================
# PDF結合（新方式）
# ==========================
def merge_pdfs(pdf_source, output_file):
    writer = PdfWriter()

    if isinstance(pdf_source, str) and os.path.isdir(pdf_source):
        pdf_files = sorted(
            [os.path.join(pdf_source, f) for f in os.listdir(pdf_source) if f.lower().endswith(".pdf")]
        )
    elif isinstance(pdf_source, list):
        pdf_files = sorted(pdf_source)
    else:
        print("無効な入力です")
        return

    if not pdf_files:
        print("PDFが見つかりません")
        return

    print("\n=== PDF結合開始 ===")

    for path in pdf_files:
        print(f"追加中: {os.path.basename(path)}")
        reader = PdfReader(path)

        for page in reader.pages:
            writer.add_page(page)

    with open(output_file, "wb") as f:
        writer.write(f)

    print(f"\n完了: {output_file} を作成しました")

# ==========================
# メイン
# ==========================
def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with open(URL_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print("=== ダウンロード開始 ===")

    target_pdfs = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(download_file, urls)

    for filepath, msg in results:
        print(msg)
        if filepath and filepath.lower().endswith(".pdf"):
            target_pdfs.append(filepath)

    if target_pdfs:
        merge_pdfs(target_pdfs, MERGED_OUTPUT)
    else:
        print("処理対象のPDFがありません")

if __name__ == "__main__":
    main()