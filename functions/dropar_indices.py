def dropar_indices(conn_info, indices):
   import psycopg as psy
   try:
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
            for indice in indices:
               cur.execute(f'DROP INDEX IF EXISTS "{indice}" CASCADE;')
            conn.commit()
   except Exception as e:
      print(f"Erro ao dropar os indices: {e}")
      import traceback
      traceback.print_exc()
   return list(indices)
      
if __name__ == "__main__":
   from conectar import conectar_db
   from criar_indices import indices_nomes

   conexao = conectar_db()
   sql_file = r"sql\indices.sql"
   indices = indices_nomes(sql_file)

   indices_dropados = dropar_indices(conexao[0], indices)
   for indice in indices_dropados:
      print(f'Dropando o indice: {indice}')