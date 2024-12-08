import os
import django
import mysql.connector
from django.core.management import call_command
from django.conf import settings
import mclass_settings


def setup_django():
    """Django 설정 초기화"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mclass_manager.settings')
    django.setup()

def create_mariadb_database():
    """MariaDB 데이터베이스 생성"""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password=mclass_settings.db_password,
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )
    cursor = connection.cursor()
    
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS mclass_manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        print("MariaDB 데이터베이스가 생성되었습니다.")
    except Exception as e:
        print(f"데이터베이스 생성 중 오류 발생: {e}")
    finally:
        cursor.close()
        connection.close()

def backup_sqlite_data():
    """SQLite 데이터 백업"""
    backup_path = os.path.join(os.getcwd(), 'backup_data.json')
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            call_command('dumpdata',
                        'auth.group',
                        'auth.user',
                        'common.bank',
                        'common.publisher',
                        'common.subject',
                        'common.purchaselocation',
                        'common.school',
                        'teachers.teacher',
                        'teachers.attendance',
                        'teachers.salary',
                        'maintenance.room',
                        'maintenance.maintenance',
                        'books.book',
                        'students.student',
                        '--exclude', 'auth.permission',
                        '--indent', '2',
                        stdout=f)
        print(f"SQLite 데이터가 {backup_path}에 백업되었습니다.")
        return backup_path
    except Exception as e:
        print(f"데이터 백업 중 오류 발생: {e}")
        return None

def migrate_to_mariadb(backup_path):
    """MariaDB로 데이터 마이그레이션"""
    try:
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mclass_manager_db',
            'USER': 'root',
            'PASSWORD': mclass_settings.db_password,
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET CHARACTER SET utf8mb4; SET collation_connection = 'utf8mb4_general_ci';",
            }
        }
        
        # Django 기본 앱 먼저 마이그레이션
        core_apps = [
            'contenttypes',
            'auth',
            'admin',
            'sessions',
        ]
        
        # 프로젝트 커스텀 앱 마이그레이션
        custom_apps = [
            'common',      # 기본 설정 앱
            'teachers',    # 교사 관련 앱
            'books',      # 책 관련 앱
            'bookstore',  # 서점 관련 앱
            'students',   # 학생 관련 앱
            'maintenance',# 유지보수 앱
        ]
        
        print("기본 앱 마이그레이션 시작...")
        for app in core_apps:
            try:
                call_command('migrate', app)
                print(f"{app} 앱 마이그레이션 완료")
            except Exception as e:
                print(f"{app} 앱 마이그레이션 중 오류 발생: {e}")
                raise e
        
        print("\n커스텀 앱 마이그레이션 시작...")
        for app in custom_apps:
            try:
                call_command('migrate', app)
                print(f"{app} 앱 마이그레이션 완료")
            except Exception as e:
                print(f"{app} 앱 마이그레이션 중 오류 발생: {e}")
                raise e
        
        # 데이터 로드
        if backup_path and os.path.exists(backup_path):
            try:
                print(f"데이터 로드 시작: {backup_path}")
                # 현재 데이터베이스가 MariaDB인지 확인
                from django.db import connection
                print(f"현재 데이터베이스 엔진: {connection.vendor}")
        
                # backup 파일의 내용 확인
                with open(backup_path, 'r', encoding='utf-8') as f:
                    print("백업 파일 내용 확인:", f.read()[:100])  # 처음 100자만 출력
        
                # loaddata 실행
                call_command('loaddata', backup_path, verbosity=3)
        
                # 데이터가 실제로 로드되었는지 확인
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                print(f"로드된 사용자 수: {user_count}")
        
                print("데이터가 성공적으로 MariaDB로 마이그레이션되었습니다.")
            except Exception as e:
                print(f"데이터 로드 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()  # 상세한 에러 메시지 출력
        
    except Exception as e:
        print(f"마이그레이션 중 오류 발생: {e}")

def main():
    """메인 실행 함수"""
    print("Windows 환경에서 데이터베이스 마이그레이션을 시작합니다!!")
    
    # Django 설정 초기화
    setup_django()
    
    # MariaDB 데이터베이스 생성
    create_mariadb_database()
    
    # SQLite 데이터 백업
    backup_path = backup_sqlite_data()
    
    # MariaDB로 마이그레이션
    migrate_to_mariadb(backup_path)
    
    # 백업 파일 정리 (선택사항)
    if backup_path and os.path.exists(backup_path):
        user_input = input("백업 파일을 삭제하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            os.remove(backup_path)
            print("백업 파일이 삭제되었습니다.")
        else:
            print(f"백업 파일이 {backup_path}에 저장되어 있습니다.")

if __name__ == "__main__":
    main()