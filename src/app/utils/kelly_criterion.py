def kellyCriterion(odd,win_prob):
    liquid_profit = odd - 1
    loss_prob = 1 - win_prob
    kelly = ((liquid_profit * win_prob) - (loss_prob))/liquid_profit
    return kelly