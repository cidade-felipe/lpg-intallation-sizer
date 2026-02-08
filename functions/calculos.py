import math

# Converter unidades
def converter_para_kcalmin(unidade):
   if unidade == 'kw':
      return unidade * 0.01434
   elif unidade == 'kcal/h':
      return unidade / 60
   elif unidade == 'kg/h':
      return unidade * 672000
   else:
      return unidade

# Potencia computada - kcal/min
# Fator de simultaneidade - %
def fator_simultaneidade(pot_computada):
   if pot_computada < 350:
      return 100
   elif pot_computada < 9612:
      return 100/(1 + 0.001*math.pow(pot_computada - 349,0.8712))
   elif pot_computada < 20000:
      return 100/(1 + 0.4705*math.pow(pot_computada - 1055,0.19931))
   else:
      return 23
# Potencia adotada - kcal/h
def potencia_adotada(pot_computada, f):
   return pot_computada * f/100

# Vazao GLP
def vazao_glp(pot_adotada,pci):
   return pot_adotada/pci

# Número cilindros
def num_cilindros(q, s, tv):
   return math.ceil(q*s/tv)