import psycopg as psy
from conectar import conectar_db
import json


with open('comp_equivalentes.json', 'r', encoding='utf-8') as f:
   comp_equivalentes = json.load(f)

with open('materiais.json', 'r', encoding='utf-8') as f:
   materiais = json.load(f)  

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
   
def upsert_peca(conn, material_id, diametro, nome, comprimento_equivalente, tipo):
   with conn.cursor() as cur:
      cur.execute("""
         INSERT INTO peca (material_id, diametro, nome, comprimento_equivalente, tipo)
         VALUES (%s, %s, %s, %s, %s)
         ON CONFLICT (material_id, diametro, nome) DO UPDATE SET
            comprimento_equivalente = EXCLUDED.comprimento_equivalente,
            tipo = EXCLUDED.tipo;
      """, (material_id, diametro, nome, comprimento_equivalente, tipo))
   conn.commit()

def material_key_for_comp_equivalentes(nome_material):
   if nome_material in comp_equivalentes:
      return nome_material
   comp_keys_upper = {k.upper(): k for k in comp_equivalentes}
   return comp_keys_upper.get(nome_material.upper())

def alimentar_comp_equivalentes(conn):
   for material in materiais.values():  # Itera sobre os valores do dicionário
      upsert_materiais(conn, material['nome'], material['c'], material['descricao'])
   
   with conn.cursor() as cur:
      for material in materiais.values():
         cur.execute("SELECT id FROM material WHERE nome = %s;", (material['nome'],))
         material_id = cur.fetchone()[0]
         
         comp_key = material_key_for_comp_equivalentes(material['nome'])
         if not comp_key:
            raise KeyError(
               f"Material '{material['nome']}' nao encontrado em comp_equivalentes.json"
            )
         for diametro_str, grupos in comp_equivalentes[comp_key].items():
            if any(isinstance(v, dict) for v in grupos.values()):
               for tipo, pecas in grupos.items():
                  for nome, comprimento_equivalente in pecas.items():
                     upsert_peca(
                        conn,
                        material_id,
                        diametro_str,
                        nome,
                        comprimento_equivalente,
                        tipo,
                     )
            else:
               for nome, comprimento_equivalente in grupos.items():
                  upsert_peca(
                     conn,
                     material_id,
                     diametro_str,
                     nome,
                     comprimento_equivalente,
                     "Conexões",
                  )
               

def main():
   conn = conectar_db()[0]
   try:
      with psy.connect(conn) as conn:
         alimentar_comp_equivalentes(conn)
      print("Banco de dados alimentado com sucesso.")
   except Exception as e:
      print(f"Erro ao alimentar o banco de dados: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   main()