import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_mini_schema():
    print("--- MINI SCHEMA DO BANCO DE DADOS ---")
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', ''),
            db=os.getenv('DB_NAME', 'formulario_db'),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = [list(r.values())[0] for r in cur.fetchall()]
            
            for t in tables:
                cur.execute(f"DESCRIBE `{t}`")
                cols = cur.fetchall()
                col_info = [f"{c['Field']}({c['Type']})" for c in cols]
                print(f"[{t}] => {', '.join(col_info)}")
    except Exception as e:
        print(f"Erro ao ler esquema: {e}")

if __name__ == "__main__":
    get_mini_schema()
