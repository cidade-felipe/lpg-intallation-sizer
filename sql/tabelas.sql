-- PostgreSQL

CREATE TABLE IF NOT EXISTS material(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   rugosidade_c REAL NOT NULL CHECK (rugosidade_c >= 0),
   descricao TEXT,
   CONSTRAINT uq_material_nome UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   tipo_edificacao VARCHAR(100),
   area_total REAL CHECK (area_total > 0),
   area_construida REAL CHECK (area_construida > 0),
   altura REAL CHECK (altura > 0),
   cliente VARCHAR(100),
   descricao TEXT,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT uq_projeto_nome UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS equipamento(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(100) NOT NULL,
   categoria VARCHAR(100) NOT NULL, -- fogao, aquecedor, forno etc
   unidade_medida VARCHAR(10)  NOT NULL, -- kW, kcal/min, kcal/h, kg/h etc
   pot_unitaria REAL NOT NULL CHECK (pot_unitaria > 0),
   fabricante VARCHAR(100),
   modelo VARCHAR(100),
   descricao TEXT,
   CONSTRAINT uq_equipamento UNIQUE (nome, unidade_medida, pot_unitaria)
);

CREATE TABLE IF NOT EXISTS equipamento_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   equipamento_id INTEGER NOT NULL,
   qtde_equipamentos INTEGER NOT NULL CHECK (qtde_equipamentos >= 0),
   CONSTRAINT fk_eqproj_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_eqproj_equip
      FOREIGN KEY (equipamento_id) REFERENCES equipamento(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT uq_eqproj UNIQUE (projeto_id, equipamento_id)
);

CREATE TABLE IF NOT EXISTS cilindro(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   tipo TEXT NOT NULL,
   taxa_vaporizacao REAL NOT NULL CHECK (taxa_vaporizacao > 0),
   CONSTRAINT uq_cilindro_tipo UNIQUE (tipo)
);

CREATE TABLE IF NOT EXISTS cilindro_projeto(
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

CREATE TABLE IF NOT EXISTS tubo(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
   diametro_nominal VARCHAR(10) NOT NULL,
   diametro_interno REAL NOT NULL CHECK (diametro_interno > 0),
   CONSTRAINT fk_tubo_material
      FOREIGN KEY (material_id) REFERENCES material(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT uq_tubo UNIQUE (material_id, diametro_nominal)
);

CREATE TABLE IF NOT EXISTS peca(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   material_id INTEGER NOT NULL,
   categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('conexoes', 'acessorios')),
   diametro VARCHAR(10) NOT NULL,
   nome VARCHAR(50) NOT NULL,
   leqv REAL NOT NULL CHECK (leqv >= 0),
   CONSTRAINT fk_peca_material
      FOREIGN KEY (material_id) REFERENCES material(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT uq_peca UNIQUE (material_id, categoria, diametro, nome)
);

CREATE TABLE IF NOT EXISTS trecho(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   rede VARCHAR(10) NOT NULL CHECK (rede IN ('primaria','secundaria')),
   lreal REAL NOT NULL CHECK (lreal > 0),
   delta_h REAL NOT NULL DEFAULT 0,
   CONSTRAINT uq_trecho UNIQUE (projeto_id, rede),
   CONSTRAINT fk_trecho_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS trecho_peca(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   trecho_id INTEGER NOT NULL,
   peca_id INTEGER NOT NULL,
   qtde_peca INTEGER NOT NULL CHECK (qtde_peca > 0),
   CONSTRAINT fk_trechopeca_trecho
      FOREIGN KEY (trecho_id) REFERENCES trecho(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_trechopeca_peca
      FOREIGN KEY (peca_id) REFERENCES peca(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS calculo(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   trecho_id INTEGER NOT NULL,
   ltotal REAL NOT NULL CHECK (ltotal >= 0),
   potencia REAL NOT NULL CHECK (potencia >= 0),
   velocidade REAL NOT NULL CHECK (velocidade >= 0),
   perda_carga REAL NOT NULL CHECK (perda_carga >= 0),
   pressao_inicial REAL NOT NULL,
   pressao_final REAL NOT NULL,
   ok BOOLEAN NOT NULL,
   observacao TEXT,
   CONSTRAINT fk_calculo_trecho_trecho
      FOREIGN KEY (trecho_id) REFERENCES trecho(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS criterio_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   pressao_operacao REAL NOT NULL CHECK (pressao_operacao >= 0),
   vel_maxima REAL NOT NULL DEFAULT 20,   
   vel_recomendada REAL NOT NULL DEFAULT 15,   
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
   tipo VARCHAR(50) NOT NULL DEFAULT 'ART',
   versao INTEGER NOT NULL,
   data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   observacoes TEXT,
   CONSTRAINT uq_documento_projeto UNIQUE (projeto_id, tipo, versao),
   CONSTRAINT fk_documento_projeto_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS valores_entrada(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   vazao REAL NOT NULL CHECK (vazao >= 0),
   pot_calculada REAL NOT NULL CHECK (pot_calculada >= 0),
   pot_adotada REAL NOT NULL CHECK (pot_adotada >= 0),
   fator_simultaneidade REAL NOT NULL CHECK (fator_simultaneidade >= 0),
   CONSTRAINT uq_parametros_gerais UNIQUE (projeto_id),
   CONSTRAINT fk_parametros_gerais_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS regulador(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   estagio VARCHAR(50) NOT NULL CHECK (estagio IN ('primeiro', 'segundo')),
   modelo VARCHAR(50),
   fabricante VARCHAR(50),
   descricao TEXT,
   CONSTRAINT uq_regulador UNIQUE (estagio)
);

CREATE TABLE IF NOT EXISTS regulador_projeto(
   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   projeto_id INTEGER NOT NULL,
   regulador_id INTEGER NOT NULL,
   CONSTRAINT fk_regproj_projeto
      FOREIGN KEY (projeto_id) REFERENCES projeto(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
   CONSTRAINT fk_regproj_regulador
      FOREIGN KEY (regulador_id) REFERENCES regulador(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT uq_regproj UNIQUE (projeto_id, regulador_id)
);