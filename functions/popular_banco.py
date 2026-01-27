import psycopg as psy
from conectar import conectar_db
import json

with open('pecas.json', 'r', encoding='utf-8') as f:
   pecas = json.load(f)

with open('materiais.json', 'r', encoding='utf-8') as f:
   materiais = json.load(f)  

with open('tubos.json', 'r', encoding='utf-8') as f:
   tubos = json.load(f)

with open('cilindros.json', 'r', encoding='utf-8') as f:
   cilindros = json.load(f)

def upsert_materiais(conn, nome, c, descricao=''):
   with conn.cursor() as cur:
      cur.execute("""
         INSERT INTO material (nome, rugosidade_c, descricao)
         VALUES (%s, %s, %s)
         ON CONFLICT (nome) DO UPDATE SET
            rugosidade_c = EXCLUDED.rugosidade_c,
            descricao = EXCLUDED.descricao;
      """, (nome, c, descricao))
   conn.commit()
   
def upsert_cilindros(conn, tipo, taxa_vaporizacao):
   with conn.cursor() as cur:
      cur.execute("""
         INSERT INTO cilindro (tipo, taxa_vaporizacao)
         VALUES (%s, %s)
         ON CONFLICT (tipo) DO UPDATE SET
            taxa_vaporizacao = EXCLUDED.taxa_vaporizacao;
      """, (tipo, taxa_vaporizacao))
   conn.commit()
   
def upsert_tubos(conn, material_id, diametro_nominal, diametro_interno):
   with conn.cursor() as cur:
      cur.execute("""
         INSERT INTO tubo (material_id, diametro_nominal, diametro_interno)
         VALUES (%s, %s, %s)
         ON CONFLICT (material_id, diametro_nominal) DO UPDATE SET
            diametro_interno = EXCLUDED.diametro_interno;
      """, (material_id, diametro_nominal, diametro_interno))
   conn.commit()

def upsert_pecas(conn, material_id, categoria, diametro, nome, comprimento_equivalente):
   with conn.cursor() as cur:
      cur.execute("""
         INSERT INTO peca (material_id, categoria, diametro, nome, comprimento_equivalente)
         VALUES (%s, %s, %s, %s, %s)
         ON CONFLICT (material_id, categoria, diametro, nome) DO UPDATE SET
            comprimento_equivalente = EXCLUDED.comprimento_equivalente;
      """, (material_id, categoria, diametro, nome, comprimento_equivalente))
   conn.commit()

def alimentar_tudo(conn):
   for tipo,taxa_vaporizacao in cilindros.items():      
      upsert_cilindros(conn, tipo, taxa_vaporizacao)
      
   for material in materiais.values():
      upsert_materiais(conn, material['nome'], material['c'], material['descricao'])

   for material_id in tubos.keys():
      for diametro_nominal, diametro_interno in tubos[material_id].items():
         upsert_tubos(conn, material_id, diametro_nominal, diametro_interno)

   for categoria in pecas.keys():
      for material_id in pecas[categoria].keys():
         for diametro in pecas[categoria][material_id].keys():
            for peca, comprimento_equivalente in pecas[categoria][material_id][diametro].items():
               upsert_pecas(conn, material_id, categoria, diametro, peca, comprimento_equivalente)
         

def main():
   conn = conectar_db()[0]
   try:
      with psy.connect(conn) as conn:
         try:
            conn.autocommit = False
            alimentar_tudo(conn)
         except Exception as e:
            print(f"Erro ao configurar o autocommit: {e}")
            import traceback
            traceback.print_exc()         
      print("Banco de dados alimentado com sucesso.")
   except Exception as e:
      print(f"Erro ao alimentar o banco de dados: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   main()