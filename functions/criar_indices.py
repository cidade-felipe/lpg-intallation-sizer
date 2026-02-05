def indices_nomes(file_path): 
   import re
   try:
      with open(file_path, "r", encoding="utf-8") as f:
         sql = f.read()

      pattern = re.compile(
         r'CREATE\s+INDEX\s+IF\s+NOT\s+EXISTS\s+("?[\w]+"?)',
         re.IGNORECASE
      )
      indices = pattern.findall(sql)
      indice = [t.replace('"', '') for t in indices]
      return indice
   except Exception as e:
      print(f"Erro ao ler o arquivo SQL: {e}")
      return None

def criar_indices(conn_info, caminho_sql):
   import psycopg as psy
   try:
      indices_arquivo = indices_nomes(caminho_sql) or []
      if not indices_arquivo:
         return []
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
               with open(caminho_sql, "r", encoding="utf-8") as f:
                  cur.execute(f.read())
                  # Indices existentes antes
               cur.execute("""
                  SELECT 
                     indexname,
                     schemaname
                  FROM pg_indexes
                  WHERE schemaname = 'public';""")
               criar_indices = {row[0] for row in cur.fetchall()}

               return list(criar_indices)

   except Exception as e:
      print(f"Erro ao criar os indices: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   import re
   from conectar import conectar_db

   file = r"sql\indices.sql"
   conexao = conectar_db()
   criar_indices = criar_indices(conexao[0], file)
   for indice in criar_indices:
      print(f'Criando o indice: {indice}')
   

