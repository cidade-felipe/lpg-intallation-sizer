# LPG Installation Sizer

Repositório de apoio ao dimensionamento de instalações de GLP. Aqui você encontra o esquema do banco PostgreSQL, dados base (materiais, tubos, peças e cilindros) e scripts Python para criar, remover e popular as tabelas.

**Visão Geral**
O foco do projeto é manter um banco relacional com os parâmetros típicos usados no cálculo de perda de carga e seleção de componentes. Os scripts em `functions/` automatizam a criação do schema, a criação de índices e a carga inicial dos dados.

**Funcionalidades**
- Criação do schema PostgreSQL via SQL.
- Criação e remoção de índices.
- Carga inicial de dados base (materiais, tubos, peças, cilindros).
- Upsert dos dados para facilitar atualizações.

**Tecnologias**
- Python + `psycopg` para acesso ao PostgreSQL.
- `python-dotenv` para carregar variáveis de ambiente.
- SQL para definição de tabelas e índices.

**Estrutura**
- `sql/` scripts SQL de criação de tabelas e índices.
- `json/` dados base para materiais, tubos, peças e cilindros.
- `functions/` utilitários Python para criar/dropar tabelas e índices e popular o banco.
- `.env_exemplo` modelo de variáveis de ambiente para conexão com o banco.

**Pré-Requisitos**
- Python instalado (recomendado 3.9+).
- PostgreSQL disponível e acessível pelas credenciais do `.env`.

**Configuração**
1. Crie o arquivo `.env` a partir de `.env_exemplo`.
2. Preencha as variáveis de conexão.
3. Instale as dependências.

```powershell
Copy-Item .env_exemplo .env
python -m pip install --upgrade pip
python -m pip install psycopg[binary] python-dotenv
```

Exemplo de `.env`:
```env
SCHEMA_NAME=schama_name_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_name_here
DB_USER=db_user_here
DB_PASSWORD=your_password_here
```

**Variáveis De Ambiente**
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` são usadas para montar a string de conexão.
- `DB_PORT` e `SCHEMA_NAME` estão no `.env_exemplo` como referência, mas não são lidas pelos scripts atuais.
- `DB_POOL_URL` é suportada pela função `connection_string()` em `functions/conectar.py` se você preferir usar uma URL única.

**Uso**
Criar tabelas e índices:
```powershell
python functions\criar_tabelas.py
python functions\criar_indices.py
```

Popular o banco com os dados base:
```powershell
python functions\popular_banco.py
```

Remover índices e tabelas:
```powershell
python functions\dropar_indices.py
python functions\dropar_tabelas.py
```

**Fluxo Sugerido**
1. Configure o `.env` com as credenciais do banco.
2. Crie as tabelas com `functions\criar_tabelas.py`.
3. Crie os índices com `functions\criar_indices.py`.
4. Popule o banco com `functions\popular_banco.py`.

**Scripts**
- `functions\criar_tabelas.py` executa `sql\tabelas.sql`.
- `functions\criar_indices.py` executa `sql\indices.sql`.
- `functions\dropar_tabelas.py` remove tabelas listadas em `sql\tabelas.sql`.
- `functions\dropar_indices.py` remove índices listados em `sql\indices.sql`.
- `functions\popular_banco.py` faz upsert dos dados em `json\`.

**Índices**
O script `sql\indices.sql` cria índices para colunas usadas em junções e filtros frequentes, principalmente FKs:
- `equipamento_projeto(projeto_id)` e `equipamento_projeto(equipamento_id)`
- `cilindro_projeto(projeto_id)` e `cilindro_projeto(cilindro_id)`
- `tubo(material_id)`
- `peca(material_id)`
- `trecho(projeto_id)`
- `trecho_peca(peca_id)`
- `regulador_projeto(projeto_id)` e `regulador_projeto(regulador_id)`
- `calculo(projeto_id)`
- `calculo_trecho(calculo_id)` e `calculo_trecho(trecho_id)`
- `criterio_projeto(projeto_id)`
- `central_glp(projeto_id)`
- `documento_projeto(projeto_id)`
- `ponto(projeto_id)`

**Modelo De Dados**
- `material` catálogo de materiais, com rugosidade e descrição.
- `tubo` diâmetros nominais e internos por material.
- `peca` conexões e acessórios com comprimento equivalente.
- `cilindro` tipos de cilindro e taxa de vaporização.
- `projeto` e `equipamento` cadastro de projetos e equipamentos.
- `equipamento_projeto` e `cilindro_projeto` relacionamentos com quantidades.
- `trecho` e `trecho_peca` trechos de rede e suas peças associadas.
- `regulador` catálogo de reguladores por estágio e modelo.
- `regulador_projeto` reguladores associados ao projeto com localização e quantidade.
- `calculo` execuções de cálculo por projeto e tipo, com parâmetros.
- `calculo_trecho` resultados de cálculo por trecho.
- `criterio_projeto` critérios operacionais e limites por projeto.
- `central_glp` dados da central de GLP e verificações.
- `documento_projeto` controle de documentos e versões do projeto.
- `ponto` ponto da instalação sendo analisado

**Dados Base**
- `json/materiais.json` define materiais e rugosidade.
- `json/tubos.json` define diâmetros por material.
- `json/pecas.json` define comprimentos equivalentes por peça.
- `json/cilindros.json` define taxas de vaporização por cilindro.

**Observações**
- Os scripts executam SQL bruto; revise antes de usar em ambientes de produção.
- Caso precise de controle de versões do banco, considere migrar os SQL para uma ferramenta de migração.

**Autor**
Felipe Cidade Soares.  
Linkedin: [cidadefelipe](https://www.linkedin.com/in/cidadefelipe/)  
GitHub: [cidade-felipe](https://github.com/cidade-felipe)

**Licença**
Licença MIT. Veja `LICENSE`.
