import json
import mysql.connector
import traceback
import mclass_settings


def connect_to_db():
    """MariaDB 연결 설정"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password= mclass_settings.db_password,
        database='mclass_manager_db',
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

def get_table_fields(cursor, table_name):
    """테이블의 컬럼 목록 가져오기"""
    cursor.execute(f"DESCRIBE {table_name}")
    return [row[0] for row in cursor.fetchall()]

def process_fields(fields, table_name, valid_fields):
    """필드 데이터 처리"""
    processed_fields = {}
    
    # auth.user 특별 처리
    if table_name == 'auth_user':
        fields.pop('groups', None)
        fields.pop('user_permissions', None)
        fields['first_name'] = fields.get('first_name', '') or ''
        fields['last_name'] = fields.get('last_name', '') or ''

    # 유효한 필드만 선택
    for key, value in fields.items():
        if key in valid_fields:
            processed_fields[key] = value if value is not None else ''
            
    return processed_fields

def migrate_data():
    conn = None
    cursor = None
    
    try:
        # 데이터베이스 연결
        print("Connecting to database...")
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # JSON 파일 읽기
        print("Reading JSON file...")
        with open('backup_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 외래 키 체크 비활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # 모델 순서 정의
        models = [
            'auth.user',
            'common.bank',
            'common.publisher',
            'common.subject',
            'common.school',
            'common.purchaselocation',
            'teachers.teacher',
            'teachers.attendance',
            'teachers.salary',
            'maintenance.room',
            'maintenance.maintenance',
            'books.book',
            'students.student'
        ]
        
        for model in models:
            table_name = model.replace('.', '_')
            print(f"\nProcessing {table_name}...")
            
            # 테이블의 유효한 필드 목록 가져오기
            valid_fields = get_table_fields(cursor, table_name)
            print(f"Valid fields: {', '.join(valid_fields)}")
            
            # 테이블 비우기
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            
            # 해당 모델의 데이터 필터링
            model_data = [item for item in data if item['model'] == model]
            print(f"Found {len(model_data)} records")
            
            for item in model_data:
                try:
                    # 기본 필드 처리
                    fields = item['fields']
                    pk = item['pk']
                    
                    # 필드 처리
                    processed_fields = process_fields(fields, table_name, valid_fields)
                    
                    # id 추가
                    processed_fields['id'] = pk
                    
                    # SQL 쿼리 생성
                    columns = ', '.join(processed_fields.keys())
                    placeholders = ', '.join(['%s'] * len(processed_fields))
                    values = list(processed_fields.values())
                    
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, values)
                    print(f"Inserted record {pk}")
                    
                except mysql.connector.Error as err:
                    print(f"Error inserting record {pk}: {err}")
                    print("SQL:", sql)
                    print("Values:", values)
                    continue
            
            # 각 테이블마다 커밋
            conn.commit()
        
        # 외래 키 체크 활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        print("\nMigration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_data()