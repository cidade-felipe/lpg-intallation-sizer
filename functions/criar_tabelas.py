def tabelas_nomes(file_path): 
   import re
   try:
      with open(file_path, "r", encoding="utf-8") as f:
         sql = f.read()

      pattern = re.compile(
         r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+("?[\w]+"?)',
         re.IGNORECASE
      )
      tables = pattern.findall(sql)
      tables = [t.replace('"', '') for t in tables]
      return tables
   except Exception as e:
      print(f"Erro ao ler o arquivo SQL: {e}")
      return None

def criar_tabelas(conn_info, caminho_sql):
   import psycopg as psy
   try:
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
               with open(caminho_sql, "r", encoding="utf-8") as f:
                  cur.execute(f.read())
               # Tabelas existentes antes
               cur.execute("""
                  SELECT tablename
                  FROM pg_tables
                  WHERE schemaname = 'public';""")
               criar_tabelas = {row[0] for row in cur.fetchall()}

               return list(criar_tabelas)

   except Exception as e:
      print(f"Erro ao criar as tabelas: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   import re
   from conectar import connect_to_db

   file = r"sql\tabelas.sql"
   conexao = connect_to_db()
   criar_tabelas = criar_tabelas(conexao[0], file)
   for tabela in criar_tabelas:
      print(f'Criando a tabela: {tabela}')
   

