import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson

def betterPoissonStats(lambda_A, lambda_B):
    k = np.arange(0, 10)
    prob_a = poisson.pmf(k, lambda_A)
    prob_b = poisson.pmf(k, lambda_B)

    p_0 = prob_a[0]
    p_1 = prob_a[1]
    p_2 = prob_a[2]
    p_3_more = 1 - (p_0 + p_1 + p_2)
    a_goals = 0
    for g in range(0,10):
        a_goals += (prob_a[g] * g)

    b_p_0 = prob_b[0]
    b_p_1 = prob_b[1]
    b_p_2 = prob_b[2]
    b_p_3_more = 1 - (b_p_0 + b_p_1 + b_p_2)
    b_goals = 0
    for g in range(0,10):
        b_goals += (prob_b[g] * g)

    p_tie = sum(prob_a[i] * prob_b[i] for i in range(10)) # P(A = B)
    p_a_win = 0 # P(A > B)
    p_b_win = 0 # P(B > A)

    for x in range(1,10):
        a_val = prob_a[x]
        b_val = prob_b[x]
        loop_val_a = 0
        loop_val_b = 0
        for y in range(0,x):
            loop_val_a += prob_b[y]
            loop_val_b += prob_a[y]
        p_a_win += (a_val * loop_val_a)
        p_b_win += (b_val * loop_val_b)

    btts = (1 - p_0) * (1 - b_p_0)

    max_goals = 10
    total_goals_probs = np.zeros(max_goals + 1)
    
    for i in range(len(prob_a)):
        for j in range(len(prob_b)):
            total_goals = i + j
            if total_goals <= max_goals:
                total_goals_probs[total_goals] += prob_a[i] * prob_b[j]
    
    unders_overs = {}
    lines = [0.5, 1.5, 2.5, 3.5, 4.5]
    
    for line in lines:
        under_prob = sum(total_goals_probs[i] for i in range(int(line) + 1))
        over_prob = 1 - under_prob
        unders_overs[line] = {'under': f"{round(under_prob * 100,1)}%", 'over': f"{round(over_prob * 100,1)}%"}
    
    results = {
        'team_A': {
            'prob_0_goals': f"{round(p_0 * 100,1)}%",
            'prob_1_goal': f"{round(p_1*100,1)}%",
            'prob_2_goals': f"{round(p_2*100,1)}%",
            'prob_3_plus_goals': f"{round(p_3_more*100,1)}%",
            'expected_goals': round(a_goals,1),
            'win_prob': f"{round(p_a_win * 100,1)}%",
            'win_or_draw_prob': f"{round((p_a_win + p_tie) * 100,1)}%"
        },
        'team_B': {
            'prob_0_goals': f"{round(b_p_0 * 100,1)}%",
            'prob_1_goal': f"{round(b_p_1 * 100,1)}%",
            'prob_2_goals': f"{round(b_p_2 * 100,1)}%",
            'prob_3_plus_goals': f"{round(b_p_3_more * 100,1)}%",
            'expected_goals': round(b_goals,1),
            'win_prob': f"{round(p_b_win * 100,1)}%",
            'win_or_draw_prob': f"{round((p_b_win + p_tie) * 100,1)}%"
        },
        'match_odds': {
            'draw_prob': f"{round(p_tie * 100,1)}%",
            'btts_prob': f"{round(btts * 100,1)}%",
        },
        'total_goals_lines': unders_overs 
    }
    return results