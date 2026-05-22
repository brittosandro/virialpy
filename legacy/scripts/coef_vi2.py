from sympy import *
from sympy.stats import *
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

#plt.style.use('fivethirtyeight')
sns.set(style="ticks")


def potencial_LJ(r, epsilon, sigma):
    '''
    Essa função recebe valores de distâncias entre dois átomos
    e retorna o valor da energia de interação.

    Entrada r/(angstron ou pm), epsilon/(eV, J, kK), sigma/(angstron ou pm)
    -------
    A unidade de medida da distância é em angstron ou pm, epsilon é eV, J ou KK
    e sigma é angstrom ou pm.

    Retorno
    -------
    A unidade de saida/retorno depende do valor de epsilon dado como entrada.
    '''
    e = epsilon
    s = sigma
    E = 4*e*(((s/r)**12) - ((s/r)**6))
    return E

def improve_LJ(r, de, req, beta):
    '''
    Essa função recebe valores de distancias entre dois átomos,
    o valor de profundidade do poço, a distância de equilibrio
    e o valor de beta, retornando a energia de interação

    Entrada (req/angstron, de/mev, )
    -------
    A unidade da distância é angstron e do poço é em meV.

    Retorno (E/milieletron-volt)
    -------
    A unidade de saida/retorno é em meV.
    '''

    n_r = (beta + 4*((r/req)**2))
    E = ((de/(n_r - 6)) * ((6 * ((req/r)**(n_r))) - (n_r * ((req/r)**6))))
    return E

def rydberg6(r, de, re, c1, c2, c3, c4, c5, c6):
    potential = -de*(1 + c1*(r-re) + c2*(r-re)**2 + c3*(r-re)**3
    + c4*(r-re)**4 + c5*(r-re)**5 + c6*(r-re)**6)*np.exp(-c1*(r-re))
    return potential

def rydberg6_sympy(r, de, re, c1, c2, c3, c4, c5, c6):
    potential = -de*(1 + c1*(r-re) + c2*(r-re)**2 + c3*(r-re)**3
    + c4*(r-re)**4 + c5*(r-re)**5 + c6*(r-re)**6)*exp(-c1*(r-re))
    return potential

def integra_potencial(r_min, r_max):
    r = symbols('r')
    return integrate(pot, (r, r_min, r_max))

def coef_virial(T, integral):
    Na = 6.022140e23
    kb = 8.617333262e-2
    kbT = kb * T
    a = (2*np.pi)/kbT
    B = a * Na * integral
    return B * 1.0e-28

def coef_virial1(integral):
    '''
    Essa função calcula o coeficiente do virial considerando a aproximação
    em que r é pequeno. Portanto r é aproximadamente zero, enquanto o potencial
    de interações é um valor positivo e grande. A função recebe o valor de
    uma integral em (angstrom^3) e retorna o coeficiente do virial em cm^3/mol.

    Entrada (integral/angstrom^3)
    -------

    Retorno (coeficiente do Virial/(cm^3/mol))
    -------
    '''
    Na = 6.022140e23
    a = 2 * np.pi
    B = a * Na * integral
    return B * 1.0e-24

def calc_pontos_pi(dist1, dist2, x):
    p = (1/2)*(dist1 + dist2) + (1/2)*(dist2 - dist1)*x
    return p

def quad_gaussian(potencial, pi, xi, wi, T, r1, r2):
    '''
    A quadratura gaussiana retorna o valor valor em cm³.
    '''

    kb = 8.617333262e-2         #j/K (joule por kelvin)
    kbT = kb * T
    #ep = 140       #kK (lembre k = 1,38064x10^-23 j/K -> kK = 1,38064x10^-23 j)
    #si = 335       #pm (picometros)
    #potencial = potencial_LJ(pi, ep, si)
    # Aqui o potencial esta em kK.
    #print(potencial)
    a = -potencial/kbT
    #print(np.exp(a))
    c = wi * (1 - np.exp(a)) * (pi**2) * (r2 - r1)/2

    return c * 1e-24


if __name__ == "__main__":

    # Dados experimentais para o coeficiente do virial. Temperatura e coeficiente.
    T_exp = [238.15, 253.15, 273.15, 296.15]
    B_exp = [-73, -62, -52, -43]

    # Com esses dados descreveremos as distâncias e a energia total a partir
    # dos cálculos de química quântica.
    dados = np.loadtxt('sapt2+_s1_aug-cc-pvqz.dat', comments='#')
    distancias1 = dados[:, 0]
    energias = dados[:, 5]

    # Abaixo serão descritos os valores de todos os parâmentros que foram
    # ajustados a partir dos dados que estão no arquivo acima.
    # Os potenciais que calcularemos o coeficiente do virial são:
    # 1) Lennard - Jones
    # 2) Improve Lennard - Jones
    # 3) Rydberg 6
    # As unidades de médida de energias e distâncias devem ser de meV e angstrom.

    # Parâmetros Lennard Jones
    epsilon1 = 1.72275656 #meV
    sigma1 = 3.3012339290   #(angstrom)
    energias2 = [potencial_LJ(r, epsilon1, sigma1) for r in distancias1]

    # Parâmetros Improved Lennard Jones
    beta = 7.59207042
    de_ILJ = 1.74947628 #meV
    req = 3.74273488   #angstrom
    energias3 = [improve_LJ(r, de_ILJ, req, beta) for r in distancias1]

    #Parâmetros para o potencial de Rydberg6
    de = 1.74713045 # meV
    re = 3.73833276  #angstrom
    c1 = 1.80244771
    c2 = -0.90436733
    c3 = 0.68570655
    c4 = -0.19073890
    c5 = 0.03727370
    c6 = 5.43360E-06
    energias4 = [rydberg6(r, de, re, c1, c2, c3, c4, c5, c6) for r in distancias1]

    plt.plot(distancias1, energias2, color='b', linewidth=2.5, label='LJ')
    plt.plot(distancias1, energias3, color='r', linewidth=2.5, label='ILJ')
    plt.plot(distancias1, energias4, color='y', linewidth=2.5, label='Ryd6')
    plt.legend(loc='upper right', shadow=False, fontsize='large',
               bbox_to_anchor=(0.98, 0.98), frameon=False)
    plt.ylabel(r'Energia ($meV$)')
    plt.xlabel(r'R ($\AA$)')
    plt.title(r'Interação $NH_{3} - He$')
    plt.savefig('cep.png', dpi=500, orientation = 'portrait', transparent = True,
             format='png')
    plt.savefig('cep.pdf', dpi=500, orientation = 'portrait', transparent = True,
             format='pdf')


    # Para calcular o coeficiente do virial total vamos repartir o coeficiente
    #em quatro partes de acordo com o a distância de interação.
    # O valor do coeficiente do virial total é dado pela soma abaixo:
    # B(T) = B1(T) + B2(T) + B3(T) + B4(T)

    # Como buscamos calcular o valor de energia para vária temperaturas, então:
    B_tot = []
    B_tot_1 = []
    B_tot_2 = []
    for T in T_exp:

        # Cálculo de B1(T)
        # Região em que r é pequeno
        # -------------------------
        # Se r varia de 0 até r1, então podemos calcular B1(T) assumindo que a
        #integral que devemos resolver é \int_{0}^{r1}r^{2}dr.
        # Note que essa integral é a mesma para qualquer potencial, seja ele:
        # Lennard-Jones, Impove Lennard-Jones ou Rydberb 6.

        r = symbols('r')
        #r1 = distancias1[0]
        r1 = distancias1[0]
        #print(r1)
        #print(f'r inicial = {r1} | rmin = {r_min1}')
        int1 = integrate(r**2, (r, 0, r1))
        #print(f'Integral = {int1}')
        print()
        B1 = coef_virial1(int1)
        print(f'B1({T}) = {B1} cm³/mol')
        print()


        # Cálculo de B2(T)
        # Região em que r1 <= r <= r2
        # ---------------------------
        #  Nesse caso nos vamos resolver a integral:
        # \int_{r1}^{r2}(1-e^(U(r)/kt))r^{2}dr, pelo método de aproximação conhecido
        # como quadratura gaussiana. Nesse caso vamos considerar n = 6, ou seja,
        # seis termos para a aproximação. Teremos então:
        # \int_{r1}^{r2}(1-e^(U(r)/kt))r^{2}dr ~ \sum_{i=1}^{6}w_i(1-e^(U(p_i)/kt))p_i^{2}.
        #  Em que p_i = 1/2*(r1+r2) + 1/2*(r2-r1)xi.
        #  Os valores de x_i e w_i são tabelados e foram retirados do sítio:
        # https://pomax.github.io/bezierinfo/legendre-gauss.html

        # Pegando o índice do ponto mínimo
        minima = 0
        for i in range(1, len(energias2)):
            if energias[minima] > energias[i]:
                minima = i
                j = i
        r_min1 = distancias1[j]

        coef_wi_xi_6 = np.loadtxt('dados_coef6.dat', comments='#')
        wi_6 = coef_wi_xi_6[:, 1]
        xi_6 = coef_wi_xi_6[:, 2]

        # Pegando o ponto associado a energia mínima do potencial.
        r2 = r_min1
        #print()
        #print(r1, r2)
        #print()

        p_i = [calc_pontos_pi(r1, r2, xi) for xi in xi_6]
        #print(p_i)
        valores_quadratura = [quad_gaussian(potencial_LJ(pi, epsilon1, sigma1),
                                       pi, xi, wi, T, r1, r2)
                                       for pi, xi, wi in zip(p_i, xi_6, wi_6)]

        valores_quadratura1 = [quad_gaussian(improve_LJ(pi, de_ILJ, req, beta),
                                       pi, xi, wi, T, r1, r2)
                                       for pi, xi, wi in zip(p_i, xi_6, wi_6)]

        valores_quadratura2 = [quad_gaussian(rydberg6(pi, de, re, c1, c2, c3, c4, c5, c6),
                                       pi, xi, wi, T, r1, r2)
                                       for pi, xi, wi in zip(p_i, xi_6, wi_6)]


        U_para_B2 = [potencial_LJ(r, epsilon1, sigma1) for r in p_i]

        U_para_B2_1 = [improve_LJ(r, de_ILJ, req, beta) for r in p_i]

        U_para_B2_2 = [rydberg6(r, de, re, c1, c2, c3, c4, c5, c6) for r in p_i]

        Na = 6.022140e23
        B2 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura]
        B2_1 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura1]
        B2_2 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura2]
        B2tot = sum(B2)
        B2tot_1 = sum(B2_1)
        B2tot_2 = sum(B2_2)
        print()
        xii = 'xi'
        wii = 'ci'
        r = 'ri [A]'
        U = 'U_LJ [meV]'
        U1 = 'U_ILJ [meV]'
        U2 = 'U_Ryd6 [meV]'
        B = 'B2_LJ [cm³/mol]'
        B_1 = 'B2_ILJ [cm³/mol]'
        B_2 = 'B2_Ryd6 [cm³/mol]'
        print(f'{xii:^11}  {wii:^13} {r:^15} {U:^15} {U1:^10} {U2:^11} {B:^11} {B_1:^10} {B_2:^10}')
        for xi, wi, ri, Ui, Ui1, Ui2, Bi, Bi1, Bi2 in zip(xi_6, wi_6, p_i, U_para_B2, U_para_B2_1, U_para_B2_2, B2, B2_1, B2_2):
            print(f'{xi:12.9f}  {wi:12.9f}  {ri:12.7f}  {Ui:12.7f} {Ui1:12.7f} {Ui2:12.7f} {Bi:12.7f} {Bi1:12.7f} {Bi2:12.7f}')
        print()
        print(f'B2({T}) LJ = {B2tot} cm³/mol')
        print(f'B2({T}) ILJ = {B2tot_1} cm³/mol')
        print(f'B2({T}) Ryd6 = {B2tot_2} cm³/mol')
        print()


        # Cálculo de B3(T)
        # Região em que r2 <= r <= r3
        # ---------------------------
        #  Nesse caso nos vamos resolver a integral:
        # \int_{r1}^{r2}(1-e^(U(r)/kt))r^{2}dr, pelo método de aproximação conhecido
        # como quadratura gaussiana. Nesse caso vamos considerar n = 10, ou seja,
        # dez termos para a aproximação. Teremos então:
        # \int_{r1}^{r2}(1-e^(U(r)/kt))r^{2}dr ~ \sum_{i=1}^{10}w_i(1-e^(U(p_i)/kt))p_i^{2}.
        #  Em que p_i = 1/2*(r1+r2) + 1/2*(r2-r1)xi.
        #  Os valores de x_i e w_i são tabelados e foram retirados do sítio:
        # https://pomax.github.io/bezierinfo/legendre-gauss.html

        r3 = distancias1[-1]
        coef_wi_xi_10 = np.loadtxt('dados_coef10.dat', comments='#')
        wi_10 = coef_wi_xi_10[:, 2]
        xi_10 = coef_wi_xi_10[:, 1]

        #print(r2, r3)

        p_i = [calc_pontos_pi(r2, r3, xi) for xi in xi_10]

        valores_quadratura = [quad_gaussian(potencial_LJ(pi, epsilon1, sigma1),
                                       pi, xi, wi, T, r2, r3)
                                       for pi, xi, wi in zip(p_i, xi_10, wi_10)]

        valores_quadratura1 = [quad_gaussian(improve_LJ(pi, de_ILJ, req, beta),
                                       pi, xi, wi, T, r2, r3)
                                       for pi, xi, wi in zip(p_i, xi_10, wi_10)]

        valores_quadratura2 = [quad_gaussian(rydberg6(pi, de, re, c1, c2, c3, c4, c5, c6),
                                       pi, xi, wi, T, r2, r3)
                                       for pi, xi, wi in zip(p_i, xi_10, wi_10)]

        U_para_B3 = [potencial_LJ(r, epsilon1, sigma1) for r in p_i]

        U_para_B3_1 = [improve_LJ(r, de, req, beta) for r in p_i]

        U_para_B3_2 = [rydberg6(r, de, re, c1, c2, c3, c4, c5, c6) for r in p_i]

        Na = 6.022140e23
        B3 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura]
        B3_1 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura1]
        B3_2 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura2]
        B3tot = sum(B3)
        B3tot_1 = sum(B3_1)
        B3tot_2 = sum(B3_2)

        xii = 'xi'
        wii = 'ci'
        r = 'ri [A]'
        U = 'U_LJ [meV]'
        U1 = 'U_ILJ [meV]'
        U2 = 'U_Ryd6 [meV]'
        B = 'B_LJ [cm³/mol]'
        B_1 = 'B3_ILJ [cm³/mol]'
        B_2 = 'B3_Ryd6 [cm³/mol]'
        print(f'{xii:^11}  {wii:^13} {r:^15} {U:^15} {U1:^10} {U2:^11} {B:^11} {B_1:^10} {B_2:^10}')
        for xi, wi, ri, Ui, Ui1, Ui2, Bi, Bi1, Bi2 in zip(xi_10, wi_10, p_i, U_para_B3, U_para_B3_1, U_para_B3_2, B3, B3_1, B3_2):
            print(f'{xi:12.9f}  {wi:12.9f}  {ri:12.7f}  {Ui:12.7f} {Ui1:12.7f} {Ui2:12.7f} {Bi:12.7f} {Bi1:12.7f} {Bi2:12.7f}')
        print()
        print(f'B3({T}) LJ = {B3tot} cm³/mol')
        print(f'B3({T}) ILJ = {B3tot_1} cm³/mol')
        print(f'B3({T}) Ryd6 = {B3tot_2} cm³/mol')
        print()


        # Cálculo de B4(T)
        # Região em que r3 <= r <= infinito
        # ---------------------------------
        # Nessa parte deveremos calcular a integral data pela relação
        # \int_{r3}^{\inf} U(r)/kT r^2 dr

        kb = 8.617333262e-2  #meV/K
        kbT = kb * T
        infinito = 18.0

        # Aqui o potencial esta em kK.
        # Essa é a função Lennard Jones e podemos resolver a integral de forma
        # analítica
        r = symbols('r')
        p = potencial_LJ(r, epsilon1, sigma1)
        f = (1/kbT) * p * r**2
        int_B4 = integrate(f, (r, r3, infinito))
        B4 = coef_virial1(int_B4)
        print(f'B4({T}) LJ = {B4} cm³/mol')

        # Para função improve Lennard Jones não conseguimos resolver a integral
        # de maneira analítica, portando vamos usar o método de quadratura
        # gaussiana nessa parte. Nesse caso a quadratura que melhor se ajustou
        # aos pontos foi uma quadratura de 24 pontos
        #p1 = improve_LJ(r, de, req, beta)
        #f1 = (1/kbT) * p1 * r**2
        #int_B4_1 = integrate(f1, (r, r3, infinito))
        #print(int_B4)
        #B4_1 = coef_virial1(int_B4_1)
        coef_wi_xi_24 = np.loadtxt('dados_coef24.dat', comments='#')
        wi_24 = coef_wi_xi_24[:, 1]
        xi_24 = coef_wi_xi_24[:, 2]
        valores_quadratura2 = [quad_gaussian(improve_LJ(pi, de, req, beta),
                                       pi, xi, wi, T, r3, infinito)
                                       for pi, xi, wi in zip(p_i, xi_24, wi_24)]

        U_para_B4_1 = [improve_LJ(r, de_ILJ, req, beta) for r in p_i]
        Na = 6.022140e23
        B4_1 = [2*np.pi*Na*quadratura for quadratura in valores_quadratura2]
        B4tot_1 = sum(B4_1)
        print(f'B4({T}) ILJ = {B4tot_1} cm³/mol')

        # Vamos calcular a região 4 para o potencial de Rydber 6
        r = symbols('r')
        p1 = rydberg6_sympy(r, de, re, c1, c2, c3, c4, c5, c6)
        f1 = (1/kbT) * p1 * r**2
        int_B4_2 = integrate(f1, (r, r3, infinito))
        B4_2 = coef_virial1(int_B4_2)
        print(f'B4({T}) Ryd 6 = {B4_2} cm³/mol')
        print()


        Btot = B1 + B2tot + B3tot + B4
        Btot1 = B1 + B2tot_1 + B3tot_1 + B4tot_1
        Btot2 = B1 + B2tot_2 + B3tot_2 + B4_2
        print(f'Btot({T}) LJ = {Btot} cm³/mol')
        print(f'Btot({T}) ILJ = {Btot1} cm³/mol')
        print(f'Btot({T}) Ryd 6 = {Btot2} cm³/mol')

        B_tot.append(Btot)
        B_tot_1.append(Btot1)
        B_tot_2.append(Btot2)

    sns.set(style="ticks")
    fig, ax = plt.subplots(figsize=(8, 6))

    # Ajusta subplots.
    fig.subplots_adjust(
                      left = 0.110,
                      right = 0.675,    # {Define as distâncias entre os extremos}
                      bottom = 0.120,
                      top = 0.910,
                      hspace = 0.24,   # Organiza espaçoes entre os subplots
                      wspace = 0.23    # Organiza espaçoes entre os subplots
                     )

    # Plot do coeficiente do virial experimental com calculado
    fig1 = ax.scatter(T_exp, B_exp, marker='o', color='b', linewidth=2.5,
             label='Experimental')
    fig2 = ax.scatter(T_exp, B_tot, marker='^', color='red', linewidth=2.5,
             label='Calculado | LJ')
    fig3 = ax.scatter(T_exp, B_tot_1, marker='*', color='y', linewidth=2.5,
             label='Calculado | ILJ')
    fig4 = ax.scatter(T_exp, B_tot_2, marker='d', color='black', linewidth=2.5,
             label='Calculado | Ryd 6')
    plt.legend(loc='upper right', shadow=False, fontsize='large',
               bbox_to_anchor=(1.54, 0.32), frameon=False)

    # Descritores dos eixos
    fig.text(
          0.04,                      # Ordena posição x
          0.5,                       # Ordena posição y
          r'B(T) $cm^{3} mol^{-1}$',
          ha = 'center',
          va = 'center',
          fontsize = 'xx-large',
          rotation = 'vertical'
          )

    fig.text(
          0.38,                      # Ordena posição x
          0.03,                     # Ordena posição y
          r'Temperatura ($K$)',
          ha = 'center',
          va = 'center',
          fontsize = 'xx-large'
          )

    fig.text(
          0.38,                      # Ordena posição x
          0.95,                     # Ordena posição y
          r'Interação $NH_{3} - He$ (Sítio 1)',
          ha = 'center',
          va = 'center',
          fontsize = 'xx-large'
          )

    plt.savefig('coef_vi.png', dpi=500, orientation = 'portrait', transparent = True,
             format='png')
    plt.savefig('coef_vi.pdf', dpi=500, orientation = 'portrait', transparent = True,
             format='pdf')
