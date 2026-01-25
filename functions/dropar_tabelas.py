def dropar_tabelas(conn_info, tabelas):
   import psycopg as psy
   try:
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
            for tabela in tabelas:
               cur.execute(f'DROP TABLE IF EXISTS "{tabela}" CASCADE;')
            conn.commit()
   except Exception as e:
      print(f"Erro ao dropar as tabelas: {e}")
      import traceback
      traceback.print_exc()
   return list(tabelas)
      
if __name__ == "__main__":
   from conectar import connect_to_db
   from criar_tabelas import tabelas_nomes

   conexao = connect_to_db()
   sql_file = r"sql\tabelas.sql"
   tabelas = tabelas_nomes(sql_file)
   tabelas_dropadas = dropar_tabelas(conexao[0], tabelas)
   for tabela in tabelas_dropadas:
      print(f'Dropando a tabela: {tabela}')