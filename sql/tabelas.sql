CREATE TABLE IF NOT EXISTS material(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   rugosidade_c INTEGER NOT NULL,
   descricao TEXT
);

CREATE TABLE IF NOT EXISTS projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   descricao TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipamento(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   categoria VARCHAR(100), -- fogão, aquecedor, forno etc
   unidade_medida VARCHAR(10) NOT NULL DEFAULT 'kW', -- kW, BTU/h etc
   potencia REAL NOT NULL,
   descricao TEXT,
   UNIQUE(nome, unidade_medida, potencia)
);

CREATE TABLE IF NOT EXISTS equipamento_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   equipamento_id INTEGER NOT NULL,
   quantidade_equipamentos INTEGER NOT NULL,
   FOREIGN KEY (projeto_id) REFERENCES projeto(id) ON DELETE CASCADE,
   FOREIGN KEY (equipamento_id) REFERENCES equipamento(id) ON DELETE CASCADE,
   UNIQUE(projeto_id, equipamento_id)
);

CREATE TABLE IF NOT EXISTS cilindro(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   tipo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cilindro_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   cilindro_id INTEGER NOT NULL,
   quantidade_cilindros INTEGER NOT NULL,
   FOREIGN KEY (projeto_id) REFERENCES projeto(id) ON DELETE CASCADE,
   FOREIGN KEY (cilindro_id) REFERENCES cilindro(id) ON DELETE CASCADE,
   UNIQUE(projeto_id, cilindro_id)
);

CREATE TABLE IF NOT EXISTS tubo(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
   diametro_nominal VARCHAR(10) NOT NULL,
   diametro_interno REAL NOT NULL,
   UNIQUE(material_id, diametro_nominal),
   FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conexao(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
   diametro VARCHAR(10) NOT NULL,
   nome VARCHAR(50) NOT NULL,
   comprimento_equivalente REAL NOT NULL,
   UNIQUE(material_id, diametro, nome),
   FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trecho(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   tubo_id INTEGER NOT NULL,
   rede VARCHAR(10) NOT NULL CHECK(rede IN ('primaria','secundaria')),
   comprimento_real REAL NOT NULL,
   vazao REAL NOT NULL,
   pressao_inicial REAL,
   pressao_final REAL,
   velocidade REAL,
   perda_carga REAL,
   FOREIGN KEY (projeto_id) REFERENCES projeto(id) ON DELETE CASCADE,
   FOREIGN KEY (tubo_id) REFERENCES tubo(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trecho_conexao(
   secao_id INTEGER NOT NULL,
   conexao_id INTEGER NOT NULL,
   quantidade_conexoes INTEGER NOT NULL,
   PRIMARY KEY(secao_id, conexao_id),
   FOREIGN KEY (secao_id) REFERENCES trecho(id) ON DELETE CASCADE,
   FOREIGN KEY (conexao_id) REFERENCES conexao(id) ON DELETE CASCADE
);