################################################################################
#
# Autor: Sandro F. de Brito
#
# Descrição:
#    Esse script tem como característica ajustar uma curva a partir
# de um conjunto de pontos de um arquivo, os quais foram calculas previamente
# por métodos computacionais.
#    O script usa a função Ridberg de grau 6 para obter os valores das
#constantes:
#    - c1, c2, c3, c4, c5, c6
#    Bem como os valores de enerdia de dissociação e R de equilíbrio:
#
#     - de (enerdia de dissociação)
#     - req (distância de equilíbrio).
################################################################################


from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
import seaborn as sns


# A função abaixo define o potencial Lennard - Jones Improve.
def LJ_Inprove(r, de, req, beta):
    n_r = (beta + 4*((r/req)**2))
    return ((de/(n_r - 6)) * ((6 * ((req/r)**(n_r))) - (n_r * ((req/r)**6))))

# Definindo Ryd 6 potential
def rydberg6(x, de, xe, c1, c2, c3, c4, c5, c6):
    potential = -de*(1 + c1*(x-xe) + c2*(x-xe)**2 + c3*(x-xe)**3
    + c4*(x-xe)**4 + c5*(x-xe)**5 + c6*(x-xe)**6)*np.exp(-c1*(x-xe))
    return potential

# Lendo os valores da função ruido afim de obter um ajuste um ajuste pelo método
# fit do módulo lmfitself.
dados = np.loadtxt('sapt0_s1_aug-cc-pvqz.dat')
x1 = dados[:, 0]
y1 = dados[:, 5]

chut_inicial = [-14.50, 3.72, 2, -1, 1, 1, 1, 1] # chute inicial do ajuste com scipy
melhor_variavel, covar = curve_fit(rydberg6, x1, y1, chut_inicial, maxfev=200000)

print('---------------------------------------')
print('  Valores de Ajuste Scipy. curve_fit \n')
print('# de = {}'.format(melhor_variavel[0]))
print('# req = {}'.format(melhor_variavel[1]))
print('# c1 = {}'.format(melhor_variavel[2]))
print('# c2 = {}'.format(melhor_variavel[3]))
print('# c3 = {}'.format(melhor_variavel[4]))
print('# c4 = {}'.format(melhor_variavel[5]))
print('# c5 = {}'.format(melhor_variavel[6]))
print('# c6 = {}'.format(melhor_variavel[7]))
print('---------------------------------------\n')

novo_ajuste = Model(rydberg6) # definimos o modelo de ajuste com Model
resultado_ajuste = novo_ajuste.fit(y1, x=x1, de=-14.50, xe=3.72, c1=2, c2=-1,
                                   c3=1, c4=1, c5=1, c6=1)

print('---------------------------------------------------')
print('      Valores de Ajuste LmFit. Fit Report \n')
print(resultado_ajuste.fit_report(modelpars=None, show_correl=True))
print('-----------------------------------------------------')


d = open('info_ajuste_CEP_Kr.txt', 'w')
d.write('--------------------------------------------------\n')
d.write('- Informações sobre o Ajuste realizado com Scipy -\n')
d.write('- A unidade de medida para De é dada em cm-1     -\n')
d.write('--------------------------------------------------\n\n')
d.write('# de = {} \n'.format(melhor_variavel[0]))
d.write('# req = {} \n'.format(melhor_variavel[1]))
d.write('# c1 = {} \n'.format(melhor_variavel[2]))
d.write('# c2 = {} \n'.format(melhor_variavel[3]))
d.write('# c3 = {} \n'.format(melhor_variavel[4]))
d.write('# c4 = {} \n'.format(melhor_variavel[5]))
d.write('# c5 = {} \n'.format(melhor_variavel[6]))
d.write('# c6 = {} \n'.format(melhor_variavel[7]))
d.write('-------------------------------------------------- \n\n')

d.write('--------------------------------------------------\n')
d.write('- Informações sobre o Ajuste realizado com LmFit -\n')
d.write('- A unidade de medida para De é dada em mev -\n')
d.write('--------------------------------------------------\n')
d.write(resultado_ajuste.fit_report())
d.write('--------------------------------------------------\n')
d.close()

sns.set(style="ticks")
fig, ax = plt.subplots()

# Ajusta subplots.
fig.subplots_adjust(
                      left = 0.130,
                      right = 0.930,    # {Define as distâncias entre os extremos}
                      bottom = 0.140,
                      top = 0.905,
                      hspace = 0.200,   # Organiza espaçoes entre os subplots
                      wspace = 0.200    # Organiza espaçoes entre os subplots
                   )
                   
ax.plot(x1, y1, 'o', color='#0000ff', label='SAPT2+/aug-cc-PVQZ', linewidth=2.)
ax.plot(x1, resultado_ajuste.best_fit, '-',  color='#e80c3d' ,label='Rydberg 6', linewidth=2.)
ax.set_xlabel('Distância ($\AA$)', labelpad = -1.5, fontsize = 'xx-large')
ax.set_ylabel('Energia (meV)', labelpad = 0.0, fontsize = 'xx-large')
#ax.set_xlim(3., 9.3)
#ax.set_ylim(-17.5, 11.5)
ax.legend(
           loc='lower right',
           ncol = 1,
           fontsize='large',
           bbox_to_anchor=(0.999, 0.75),
           fancybox = True,
           frameon=False
           )
ax.set_title('$Ar + NH_{3}$ $(Sítio$ $2)$', fontsize = 'xx-large', fontweight = 'bold')
plt.savefig('ajuste.png', dpi=300, orientation='portrait', transparent=True, format='png')
plt.savefig('ajuste.pdf', dpi=400, orientation='portrait', transparent=True, format='pdf')
plt.show()
