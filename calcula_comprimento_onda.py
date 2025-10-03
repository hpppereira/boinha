'''
Calculo do comprimento de onda em aguas intermediarias
Henrique Pereira
'''

import numpy as np

# Dados de entrada

#periodo de onda (segundos)
Ts = [2,4,6,8,10,12,14,16,18,20]

#profundidade
h = 1

# Inicio do calculo

Lp = []

for T in Ts:

	#comprimento de onda em aguas profundas
	Lo = 1.56 * T ** 2

	L = [Lo]

	for inter in range(500):

		L_aux = 1.56 * T ** 2 * np.tanh(2*np.pi / L[inter] * h)

		L.append(L_aux)

	Lp.append(L[-1])

