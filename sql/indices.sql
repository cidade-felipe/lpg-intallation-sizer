-- Índices úteis para joins e consultas típicas
CREATE INDEX IF NOT EXISTS idx_eqproj_projeto
ON equipamento_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_eqproj_equip 
ON equipamento_projeto (equipamento_id);

CREATE INDEX IF NOT EXISTS idx_cilproj_projeto
ON cilindro_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_cilproj_cilindro
ON cilindro_projeto (cilindro_id);

CREATE INDEX IF NOT EXISTS idx_tubo_material 
ON tubo (material_id);

CREATE INDEX IF NOT EXISTS idx_peca_material
ON peca (material_id);

CREATE INDEX IF NOT EXISTS idx_trecho_projeto
ON trecho (projeto_id);

CREATE INDEX IF NOT EXISTS idx_trechopeca_peca
ON trecho_peca (peca_id);

CREATE INDEX IF NOT EXISTS idx_regproj_projeto
ON regulador_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_regproj_regulador
ON regulador_projeto (regulador_id);

CREATE INDEX IF NOT EXISTS idx_calculo_projeto
ON calculo (projeto_id);

CREATE INDEX IF NOT EXISTS idx_calculo_trecho_calculo
ON calculo_trecho (calculo_id);

CREATE INDEX IF NOT EXISTS idx_calculo_trecho_trecho
ON calculo_trecho (trecho_id);

CREATE INDEX IF NOT EXISTS idx_criterio_projeto
ON criterio_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_central_glp_projeto
ON central_glp (projeto_id);

CREATE INDEX IF NOT EXISTS idx_documento_projeto
ON documento_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_ponto_projeto
ON ponto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_edificacao_projeto
ON edificacao (projeto_id);

CREATE INDEX IF NOT EXISTS idx_parametros_gerais_projeto
ON parametros_gerais (projeto_id);

CREATE INDEX IF NOT EXISTS idx_regulador_projeto
ON regulador_projeto (projeto_id);

CREATE INDEX IF NOT EXISTS idx_trechopeca_trecho
ON trecho_peca (trecho_id);