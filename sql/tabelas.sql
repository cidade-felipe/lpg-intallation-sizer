-- PostgreSQL

CREATE TABLE IF NOT EXISTS material (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   rugosidade_c REAL NOT NULL CHECK (rugosidade_c >= 0),
   descricao TEXT,
   CONSTRAINT uq_material_nome UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS projeto (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   descricao TEXT,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipamento (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   categoria VARCHAR(100) NOT NULL, -- fogao, aquecedor, forno etc
   unidade_medida VARCHAR(10)  NOT NULL DEFAULT 'kW', -- kW, BTU/h etc
   potencia REAL NOT NULL CHECK (potencia > 0),
   descricao TEXT,
   CONSTRAINT uq_equipamento UNIQUE (nome, unidade_medida, potencia)
);

CREATE TABLE IF NOT EXISTS equipamento_projeto (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id BIGINT NOT NULL,
   equipamento_id BIGINT NOT NULL,
   quantidade_equipamentos INTEGER NOT NULL CHECK (quantidade_equipamentos > 0),
   CONSTRAINT fk_eqproj_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_eqproj_equip
      FOREIGN KEY (equipamento_id) REFERENCES equipamento(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT uq_eqproj UNIQUE (projeto_id, equipamento_id)
);

CREATE TABLE IF NOT EXISTS cilindro (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   tipo TEXT NOT NULL,
   taxa_vaporizacao REAL NOT NULL CHECK (taxa_vaporizacao > 0),
   CONSTRAINT uq_cilindro_tipo UNIQUE (tipo)
);

CREATE TABLE IF NOT EXISTS cilindro_projeto (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id BIGINT NOT NULL,
   cilindro_id BIGINT NOT NULL,
   quantidade_cilindros INTEGER NOT NULL CHECK (quantidade_cilindros > 0),
   CONSTRAINT fk_cilproj_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_cilproj_cilindro
      FOREIGN KEY (cilindro_id) REFERENCES cilindro(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT uq_cilproj UNIQUE (projeto_id, cilindro_id)
);

CREATE TABLE IF NOT EXISTS tubo (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id BIGINT NOT NULL,
   diametro_nominal VARCHAR(10) NOT NULL,
   diametro_interno REAL NOT NULL CHECK (diametro_interno > 0),
   CONSTRAINT fk_tubo_material
      FOREIGN KEY (material_id) REFERENCES material(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT uq_tubo UNIQUE (material_id, diametro_nominal)
);

CREATE TABLE IF NOT EXISTS peca (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id BIGINT NOT NULL,
   categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('conexoes', 'acessorios')),
   diametro VARCHAR(10) NOT NULL,
   nome VARCHAR(50) NOT NULL,
   comprimento_equivalente REAL NOT NULL CHECK (comprimento_equivalente >= 0),
   CONSTRAINT fk_peca_material
      FOREIGN KEY (material_id) REFERENCES material(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT uq_peca UNIQUE (material_id, categoria, diametro, nome)
);

CREATE TABLE IF NOT EXISTS trecho (
   id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id BIGINT NOT NULL,
   rede VARCHAR(10) NOT NULL CHECK (rede IN ('primaria','secundaria')),
   comprimento_real REAL NOT NULL CHECK (comprimento_real > 0),
   vazao REAL NOT NULL CHECK (vazao >= 0),
   pressao_inicial REAL CHECK (pressao_inicial >= 0),
   pressao_final REAL CHECK (pressao_final >= 0),
   velocidade REAL CHECK (velocidade >= 0),
   perda_carga REAL CHECK (perda_carga >= 0),
   CONSTRAINT fk_trecho_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT ck_trecho_pressao
      CHECK (pressao_inicial IS NULL OR pressao_final IS NULL OR pressao_inicial >= pressao_final)
);

CREATE TABLE IF NOT EXISTS trecho_peca (
   trecho_id BIGINT NOT NULL,
   peca_id BIGINT NOT NULL,
   quantidade_peca INTEGER NOT NULL CHECK (quantidade_peca > 0),
   PRIMARY KEY (trecho_id, peca_id),
   CONSTRAINT fk_trechopeca_trecho
      FOREIGN KEY (trecho_id) REFERENCES trecho(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_trechopeca_peca
      FOREIGN KEY (peca_id) REFERENCES peca(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);