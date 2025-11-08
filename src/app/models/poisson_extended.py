import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson

def betterPoissonStats(lambda_A,lambda_B):

    # Valores de k (0 a 9 golos)
    k = np.arange(0, 10)

    # Probabilidades usando Poisson
    prob_a = poisson.pmf(k, lambda_A)
    prob_b = poisson.pmf(k, lambda_B)

    # Plot
    plt.bar(k, prob_a, color='skyblue')
    plt.xlabel('Número de golos')
    plt.ylabel('Probabilidade')
    plt.title(f'Distribuição de Poisson (λ={lambda_A})')
    plt.show()

    plt.bar(k, prob_b, color='red')
    plt.xlabel('Número de golos')
    plt.ylabel('Probabilidade')
    plt.title(f'Distribuição de Poisson (λ={lambda_B})')
    plt.show()

    # Print das probabilidades
    p_0 = prob_a[0]
    p_1 = prob_a[1]
    p_2 = prob_a[2]
    p_3_more = 1 - (p_0 + p_1 + p_2)  # soma das probabilidades de 3 ou mais golos
    a_goals = 0
    for g in range(0,10):
        a_goals += (prob_a[g] * g)

    b_p_0 = prob_b[0]
    b_p_1 = prob_b[1]
    b_p_2 = prob_b[2]
    b_p_3_more = 1 - (b_p_0 + b_p_1 + b_p_2)  # soma das probabilidades de 3 ou mais golos
    b_goals = 0
    for g in range(0,10):
        b_goals += (prob_b[g] * g)

    p_tie = sum(prob_a[i] * prob_b[i] for i in range(10)) # P (A = B)

    p_a_win = 0 # P(A > B)
    p_b_win = 0 # P(B > A)

    for x in range(1,10):
        a_val = prob_a[x]
        b_val = prob_b[x]
        loop_val_a = 0
        loop_val_b = 0
        for y in range(0,x): # p.ex: P(A = 2) * (P(B = 0) + P(B = 1)), i.e: todos os inferiores
            loop_val_a += prob_b[y]
            loop_val_b += prob_a[y]
        p_a_win += (a_val * loop_val_a)
        p_b_win += (b_val * loop_val_b)

    # Ambas marcam: (prob A marcar 1+ * prob B marcar 1+), i.e: 1 - P(A não marcar)
    btts = (1 - p_0) * (1 - b_p_0)
    ajusted_btts = btts + 0.4 * min((1-p_0),(1-b_p_0)) #0.4 sendo um BIAS

    # CÁLCULO DE OVERS E UNDERS
    # Distribuição conjunta do total de golos
    max_goals = 10  # máximo de golos a considerar
    total_goals_probs = np.zeros(max_goals + 1)
    
    for i in range(len(prob_a)):
        for j in range(len(prob_b)):
            total_goals = i + j
            if total_goals <= max_goals:
                total_goals_probs[total_goals] += prob_a[i] * prob_b[j]
    
    # Cálculo dos Overs e Unders
    unders_overs = {}
    lines = [0.5, 1.5, 2.5, 3.5, 4.5]
    
    for line in lines:
        under_prob = sum(total_goals_probs[i] for i in range(int(line) + 1))
        over_prob = 1 - under_prob
        unders_overs[line] = {'under': under_prob, 'over': over_prob}

    print(f'---------------------------------------------------------')
    print(f'A: Probabilidade de 0 golos: {p_0:.3f} ({p_0*100:.1f}%)')
    print(f'A: Probabilidade de 1 golo: {p_1:.3f} ({p_1*100:.1f}%)')
    print(f'A: Probabilidade de 2 golos: {p_2:.3f} ({p_2*100:.1f}%)')
    print(f'A: Probabilidade de 3 ou mais golos: {p_3_more:.3f} ({p_3_more*100:.1f}%)')
    print(f'A: Golos médios esperados: {a_goals:.3f}')
    print(f'A: Moneyline 1: {p_a_win:.3f} ({p_a_win*100:.1f}%)')
    print(f'A: Moneyline 1/X: {(p_a_win + p_tie):.3f} ({(p_a_win + p_tie)*100:.1f}%)')
    print(f'---------------------------------------------------------')
    print(f'B: Probabilidade de 0 golos: {b_p_0:.3f} ({b_p_0*100:.1f}%)')
    print(f'B: Probabilidade de 1 golo: {b_p_1:.3f} ({b_p_1*100:.1f}%)')
    print(f'B: Probabilidade de 2 golos: {b_p_2:.3f} ({b_p_2*100:.1f}%)')
    print(f'B: Probabilidade de 3 ou mais golos: {b_p_3_more:.3f} ({b_p_3_more*100:.1f}%)')
    print(f'B: Golos médios esperados: {b_goals:.3f}')
    print(f'B: Moneyline 2: {p_b_win:.3f} ({p_b_win*100:.1f}%)')
    print(f'B: Moneyline 2/X: {(p_b_win + p_tie):.3f} ({(p_b_win + p_tie)*100:.1f}%)')
    print(f'---------------------------------------------------------')
    print(f'RESULT: Probabilidade de Empate: {p_tie:.3f} ({p_tie*100:.1f}%)')
    print(f'RESULT: Probabilidade de BTTS: {btts:.3f} ({btts*100:.1f}%)')
    print(f'RESULT: Probabilidade de BTTS Ajustada: {ajusted_btts:.3f} ({ajusted_btts*100:.1f}%)')
    print(f'---------------------------------------------------------')
    print(f'OVERS/UNDERS - TOTAL DE GOLOS:')
    for line in lines:
        under_p = unders_overs[line]['under']
        over_p = unders_overs[line]['over']
        print(f'Under {line}: {under_p*100:.1f}%')
        print(f'Over  {line}: {over_p*100:.1f}%')
    return

betterPoissonStats((2.03150283092),(0.35256088156))