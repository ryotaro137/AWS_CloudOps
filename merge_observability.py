import os
from pypdf import PdfReader, PdfWriter

SOURCE_DIR = "/Users/haradaryoutarou/Library/CloudStorage/GoogleDrive-harada.ryotaro.731@gmail.com/マイドライブ/Study/AWS/CloudOps/Observability2025"
OUTPUT_FILE = "/Users/haradaryoutarou/Library/CloudStorage/GoogleDrive-harada.ryotaro.731@gmail.com/マイドライブ/Study/AWS/CloudOps/Merge_BlackBelt/BlackBelt_Observability2025.pdf"

def merge_pdfs(source_dir, output_file):
    writer = PdfWriter()
    pdf_files = sorted(
        [os.path.join(source_dir, f) for f in os.listdir(source_dir) if f.lower().endswith(".pdf")]
    )

    if not pdf_files:
        print("PDFが見つかりません")
        return

    print(f"=== PDF結合開始: {len(pdf_files)} ファイル ===")

    for path in pdf_files:
        print(f"追加中: {os.path.basename(path)}")
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "wb") as f:
        writer.write(f)

    print(f"\n完了: {output_file} を作成しました")

if __name__ == "__main__":
    merge_pdfs(SOURCE_DIR, OUTPUT_FILE)
