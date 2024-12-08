import os
import json
import sys
import django
from pathlib import Path

# 프로젝트 루트 디렉토리 경로 설정
current_dir = Path(__file__).resolve().parent

# Python 경로에 현재 디렉토리와 상위 디렉토리 추가
sys.path.insert(0, str(current_dir))

# Django 설정
os.environ['DJANGO_SETTINGS_MODULE'] = 'mclass_manager.settings'  # 프로젝트 이름을 실제 이름으로 변경하세요

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    print("Current directory:", current_dir)
    print("Python path:", sys.path)
    sys.exit(1)

def check_json_structure():
    """JSON 파일의 데이터 구조 확인"""
    with open('backup_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # 각 모델별 필드 구조 출력
    models_data = {}
    for item in data:
        model_name = item['model']
        if model_name not in models_data:
            models_data[model_name] = set(item['fields'].keys())
    
    print("\n=== JSON 파일의 모델 구조 ===")
    for model_name, fields in models_data.items():
        print(f"\n{model_name}:")
        print(sorted(fields))

def check_current_models():
    """현재 Django 모델 구조 확인"""
    try:
        from django.apps import apps
        
        print("\n=== 현재 Django 모델 구조 ===")
        
        # 등록된 모든 모델 순회
        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            print(f"\n{model_name}:")
            fields = [f.name for f in model._meta.fields]
            print(sorted(fields))
            
    except Exception as e:
        print(f"\nError checking models: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Script starting...")
    print("Current directory:", current_dir)
    print("Python path:", sys.path)
    
    try:
        check_json_structure()
        check_current_models()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()