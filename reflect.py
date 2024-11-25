import pandas as pd
from sqlalchemy import create_engine

# 데이터베이스 연결 설정
DATABASE_URL = "postgresql+psycopg2://myuser:0000@localhost:5432/miml2"

engine = create_engine(DATABASE_URL)

def export_table_to_csv():
    # 데이터베이스의 모든 테이블 이름 가져오기
    tables = engine.table_names()

    for table in tables:
        # 각 테이블의 데이터를 가져와 DataFrame으로 변환
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, engine)
        
        # 테이블 이름으로 CSV 파일 저장
        file_name = f"{table}.csv"
        df.to_csv(file_name, index=False)
        print(f"Exported {table} to {file_name}")

if __name__ == "__main__":
    export_table_to_csv()