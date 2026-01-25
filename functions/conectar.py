import os
from dotenv import load_dotenv
import psycopg as psy
load_dotenv()
def conectar_db():
   DB_NAME = os.getenv('DB_NAME')
   DB_USER = os.getenv('DB_USER')
   DB_PASSWORD = os.getenv('DB_PASSWORD')
   DB_HOST = os.getenv('DB_HOST')

   conn_info = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST}"
   try:
      with psy.connect(conn_info) as conn:
         print("Connected to database")
         cur = conn.cursor()
         cur.execute("SELECT version();")
         record = cur.fetchone()

   except Exception as e:
      print(f"Error: {e}")
      import traceback
      traceback.print_exc()
      conn.rollback()

   return conn_info,record

def connection_string():
   load_dotenv()

   return os.getenv('DB_POOL_URL')

if __name__ == "__main__":
   conexao = conectar_db()
   print(f'Você está conectado ao banco de dados na versão {conexao[1]}')
   print(connection_string())