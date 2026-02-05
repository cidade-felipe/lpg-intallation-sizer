import psycopg as psy
from conectar import conectar_db
import json
import re

with open(r'json\pecas.json', 'r', encoding='utf-8') as f:
   pecas = json.load(f)

with open(r'json\materiais.json', 'r', encoding='utf-8') as f:
   materiais = json.load(f)  

with open(r'json\tubos.json', 'r', encoding='utf-8') as f:
   tubos = json.load(f)

with open(r'json\cilindros.json', 'r', encoding='utf-8') as f:
   cilindros = json.load(f)

def upsert_materiais(conn, dados):
   try:   
      with conn.cursor() as cur:
         cur.executemany("""
            INSERT INTO material (nome, rugosidade_c, descricao)
            VALUES (%s, %s, %s)
            ON CONFLICT (nome) DO UPDATE SET
               rugosidade_c = EXCLUDED.rugosidade_c,
               descricao = EXCLUDED.descricao;
         """, dados)
   except Exception as e:
      print(f"Erro ao inserir material: {e}")
      import traceback
      traceback.print_exc()

def upsert_cilindros(conn, dados):
   try:   
      with conn.cursor() as cur:
         cur.executemany("""
            INSERT INTO cilindro (tipo, taxa_vaporizacao)
            VALUES (%s, %s)
            ON CONFLICT (tipo) DO UPDATE SET
               taxa_vaporizacao = EXCLUDED.taxa_vaporizacao;
         """, dados)
   except Exception as e:
      print(f"Erro ao inserir cilindro: {e}")
      import traceback
      traceback.print_exc()
      
def upsert_tubos(conn, dados):
   try:
      with conn.cursor() as cur:
         cur.executemany("""
            INSERT INTO tubo (material_id, diametro_nominal, diametro_interno)
            VALUES (%s, %s, %s)
            ON CONFLICT (material_id, diametro_nominal) DO UPDATE SET
               diametro_interno = EXCLUDED.diametro_interno;
         """, dados)
   except Exception as e:
      print(f"Erro ao inserir tubo: {e}")
      import traceback
      traceback.print_exc()

def upsert_pecas(conn, dados):
   try:
      with conn.cursor() as cur:
         cur.executemany("""
            INSERT INTO peca (material_id, categoria, diametro, nome, comprimento_equivalente)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (material_id, categoria, diametro, nome) DO UPDATE SET
               comprimento_equivalente = EXCLUDED.comprimento_equivalente;
         """, dados)
   except Exception as e:
      print(f"Erro ao inserir peca: {e}")
      import traceback
      traceback.print_exc()

def alimentar_tudo(conn):
   dados_cilindros = [(tipo, taxa) for tipo, taxa in cilindros.items()]
   upsert_cilindros(conn, dados_cilindros)

   dados_materiais = [(m['nome'], m['c'], m.get('descricao', '')) for m in materiais.values()]
   upsert_materiais(conn, dados_materiais)

   dados_tubos = []
   for material_id, itens in tubos.items():
      for dn, di in itens.items():
         dados_tubos.append((material_id, dn, di))
   upsert_tubos(conn, dados_tubos)

   dados_pecas = []
   for categoria, mat_dict in pecas.items():
      for material_id, diam_dict in mat_dict.items():
         for diametro, pecas_dict in diam_dict.items():
            for nome, comp in pecas_dict.items():
               dados_pecas.append((material_id, categoria, diametro, nome, comp))
   upsert_pecas(conn, dados_pecas)
   
   conn.commit()
         

def main():
   conn = conectar_db()[0]
   try:
      with psy.connect(conn) as conn:
         try:
            conn.autocommit = False
            alimentar_tudo(conn)
            print("Banco de dados alimentado com sucesso.")
         except Exception as e:
            print(f"Erro ao configurar o autocommit: {e}")
            conn.rollback()
            import traceback
            traceback.print_exc()
         else:
            conn.commit()

   except Exception as e:
      print(f"Erro ao alimentar o banco de dados: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   main()