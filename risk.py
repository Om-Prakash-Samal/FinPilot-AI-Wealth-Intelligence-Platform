def calculate_risk_score(age, income_stability, experience, emergency_fund):
    score = 0

    if age < 30:
        score += 20
    if income_stability == "stable":
        score += 25
    if experience == "high":
        score += 25
    if emergency_fund:
        score += 30

    return min(score, 100)
