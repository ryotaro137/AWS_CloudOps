import os
import shutil
from blackbelt_pipeline import merge_pdfs

def main():
    downloads_dir = "downloads"
    categories = {
        "CloudWatch": [],
        "EventBridge": [],
        "CloudFormation": [],
        "SystemManager": []
    }
    
    for f in os.listdir(downloads_dir):
        if not f.endswith(".pdf"):
            continue
        
        name = f.lower()
        if "container" in name:
            categories["CloudWatch"].append(f)
        elif "cloudwatch" in name:
            categories["CloudWatch"].append(f)
        elif "eventbridge" in name:
            categories["EventBridge"].append(f)
        elif "cloudformation" in name:
            categories["CloudFormation"].append(f)
        elif "systemmanager" in name or "systemsmanager" in name or "systems-manager" in name or "systems_manager" in name:
            categories["SystemManager"].append(f)
            
    for category, files in categories.items():
        if not files:
            continue
            
        print(f"\\n--- 処理中: {category} ---")
        temp_dir = f"temp_{category}"
        os.makedirs(temp_dir, exist_ok=True)
        
        for f in files:
            shutil.copy(os.path.join(downloads_dir, f), os.path.join(temp_dir, f))
            
        output_name = f"BlackBelt_{category}.pdf"
        merge_pdfs(temp_dir, output_name)
        
        # Cleanup
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
