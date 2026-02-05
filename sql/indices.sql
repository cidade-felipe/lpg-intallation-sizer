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