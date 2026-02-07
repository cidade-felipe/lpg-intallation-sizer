-- PostgreSQL

CREATE TABLE IF NOT EXISTS material (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   rugosidade_c REAL NOT NULL CHECK (rugosidade_c >= 0),
   descricao TEXT,
   CONSTRAINT uq_material_nome UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS projeto (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   descricao TEXT,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipamento (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   categoria VARCHAR(100) NOT NULL, -- fogao, aquecedor, forno etc
   unidade_medida VARCHAR(10)  NOT NULL DEFAULT 'kW', -- kW, BTU/h etc
   potencia REAL NOT NULL CHECK (potencia > 0),
   descricao TEXT,
   CONSTRAINT uq_equipamento UNIQUE (nome, unidade_medida, potencia)
);

CREATE TABLE IF NOT EXISTS equipamento_projeto (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   equipamento_id INTEGER NOT NULL,
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
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   tipo TEXT NOT NULL,
   taxa_vaporizacao REAL NOT NULL CHECK (taxa_vaporizacao > 0),
   CONSTRAINT uq_cilindro_tipo UNIQUE (tipo)
);

CREATE TABLE IF NOT EXISTS cilindro_projeto (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   cilindro_id INTEGER NOT NULL,
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
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
   diametro_nominal VARCHAR(10) NOT NULL,
   diametro_interno REAL NOT NULL CHECK (diametro_interno > 0),
   CONSTRAINT fk_tubo_material
      FOREIGN KEY (material_id) REFERENCES material(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT uq_tubo UNIQUE (material_id, diametro_nominal)
);

CREATE TABLE IF NOT EXISTS peca (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
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
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
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
   trecho_id INTEGER NOT NULL,
   peca_id INTEGER NOT NULL,
   quantidade_peca INTEGER NOT NULL CHECK (quantidade_peca > 0),
   PRIMARY KEY (trecho_id, peca_id),
   CONSTRAINT fk_trechopeca_trecho
      FOREIGN KEY (trecho_id) REFERENCES trecho(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_trechopeca_peca
      FOREIGN KEY (peca_id) REFERENCES peca(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS regulador (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   estagio VARCHAR(100) NOT NULL CHECK (estagio IN ('primeiro', 'segundo')),
   modelo VARCHAR(100) NOT NULL,
   CONSTRAINT uq_regulador UNIQUE (estagio, modelo)
);

CREATE TABLE IF NOT EXISTS regulador_projeto (
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   regulador_id INTEGER NOT NULL,
   quantidade_reguladores INTEGER NOT NULL CHECK (quantidade_reguladores > 0),
   localizacao VARCHAR(100) NOT NULL,
   CONSTRAINT fk_regproj_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_regproj_regulador
      FOREIGN KEY (regulador_id) REFERENCES regulador(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT uq_regproj UNIQUE (projeto_id, regulador_id)
);

CREATE TABLE IF NOT EXISTS calculo(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('central', 'rede primaria', 'rede secundaria')),
   data_execucao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   parametros JSONB NOT NULL,
   CONSTRAINT uq_calculo UNIQUE (projeto_id, tipo),
   CONSTRAINT fk_calculo_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS calculo_trecho(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   calculo_id INTEGER NOT NULL,
   trecho_id INTEGER NOT NULL,
   leqv REAL NOT NULL CHECK (leqv >= 0),
   vazao REAL NOT NULL CHECK (vazao >= 0),
   velocidade REAL NOT NULL CHECK (velocidade >= 0),
   perda_carga REAL NOT NULL CHECK (perda_carga >= 0),
   pressao_inicial REAL NOT NULL,
   pressao_final REAL NOT NULL,
   ok BOOLEAN NOT NULL,
   observacao TEXT,
   CONSTRAINT uq_calculo_trecho UNIQUE (calculo_id, trecho_id),
   CONSTRAINT fk_calculo_trecho_calculo
      FOREIGN KEY (calculo_id) REFERENCES calculo(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_calculo_trecho_trecho
      FOREIGN KEY (trecho_id) REFERENCES trecho(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS criterio_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   pressao_operacao REAL NOT NULL CHECK (pressao_operacao >= 0),
   perda_carga_maxima REAL NOT NULL CHECK (perda_carga_maxima >= 0),
   perda_carga_minima REAL NOT NULL CHECK (perda_carga_minima >= 0),
   vel_maxima REAL NOT NULL CHECK (vel_maxima >= 0),
   vel_minima REAL NOT NULL CHECK (vel_minima >= 0),
   vel_max_recomendada REAL NOT NULL CHECK (vel_max_recomendada >= 0),
   vel_min_recomendada REAL NOT NULL CHECK (vel_min_recomendada >= 0),
   densidade_relativa REAL NOT NULL CHECK (densidade_relativa >= 0),
   temperatura_projeto REAL NOT NULL CHECK (temperatura_projeto >= 0),
   observacao TEXT,
   CONSTRAINT uq_criterio_projeto UNIQUE (projeto_id),
   CONSTRAINT fk_criterio_projeto_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS central_glp(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   localizacao VARCHAR(100) NOT NULL,
   afastamentos JSONB NOT NULL,
   observacoes TEXT,
   ok BOOLEAN NOT NULL,
   CONSTRAINT uq_central_glp UNIQUE (projeto_id),
   CONSTRAINT fk_central_glp_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS documento_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   tipo VARCHAR(50) NOT NULL,
   versao INTEGER NOT NULL,
   data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   observacoes TEXT,
   CONSTRAINT uq_documento_projeto UNIQUE (projeto_id, tipo, versao),
   CONSTRAINT fk_documento_projeto_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);
