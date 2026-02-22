def generate_allocation(risk_score):
    if risk_score > 70:
        return {"Equity": 70, "Debt": 20, "Gold": 10}
    elif risk_score > 40:
        return {"Equity": 50, "Debt": 40, "Gold": 10}
    else:
        return {"Equity": 30, "Debt": 60, "Gold": 10}
