import re
import math

from models.risk import calculate_risk_score
from models.portfolio import generate_allocation
from agent.planner import create_plan


def extract_goal_details(goal_text):
    """
    Extract target amount and years from text like:
    'I want 10l in 5yrs'
    """
    goal_text = goal_text.lower()

    # Extract amount (like 10l or 10 lakh)
    amount_match = re.search(r'(\d+)\s*(l|lakh)?', goal_text)
    years_match = re.search(r'(\d+)\s*(y|yr|yrs|year|years)', goal_text)

    if not amount_match or not years_match:
        return None, None

    amount = int(amount_match.group(1))
    years = int(years_match.group(1))

    # Convert lakh to actual number
    if amount_match.group(2):
        amount = amount * 100000

    return amount, years


def calculate_monthly_sip(target_amount, years, annual_return=12):
    """
    SIP Formula:
    FV = P * [((1+r)^n - 1) / r] * (1+r)
    """
    monthly_rate = annual_return / 100 / 12
    months = years * 12

    sip = target_amount / (((1 + monthly_rate) ** months - 1) / monthly_rate * (1 + monthly_rate))

    return round(sip)


total_months = years * 12
total_invested = monthly_investment * total_months
expected_returns = target_amount - total_invested

print("\n==============================")
print("FINANCIAL SUMMARY")
print("==============================")
print(f"Target Corpus: ₹{target_amount:,.0f}")
print(f"Investment Duration: {years} years")
print(f"Monthly SIP Required: ₹{monthly_investment:,.0f}")
print(f"Total Invested: ₹{total_invested:,.0f}")
print(f"Expected Wealth Gained: ₹{expected_returns:,.0f}")
print("==============================\n")



def display_allocation(monthly_amount, allocation):
    print("\n==============================")
    print(f"You need to invest ₹{monthly_amount:,.0f} per month.")
    print("\nSuggested Allocation:\n")

    for asset, percent in allocation.items():
        amount = (percent / 100) * monthly_amount
        print(f"{asset} ({percent}%)  → ₹{amount:,.0f}")

    print("==============================\n")


def main():
    print("Welcome to FinPilot AI")

    goal = input("Enter your financial goal: ")

    plan = create_plan(goal)

    print("\nGenerated Plan:")
    print(plan)

    # Extract goal details
    target_amount, years = extract_goal_details(goal)

    if target_amount and years:
        monthly_investment = calculate_monthly_sip(target_amount, years)
    else:
        print("\nCould not extract goal amount and years. Using default ₹10L in 5 years.")
        monthly_investment = calculate_monthly_sip(1000000, 5)

    age = int(input("\nEnter your age: "))
    income_stability = input("Income stability (stable/unstable): ")
    experience = input("Investment experience (low/high): ")
    emergency = input("Do you have emergency fund? (yes/no): ")

    emergency_bool = True if emergency.lower() == "yes" else False

    risk_score = calculate_risk_score(age, income_stability, experience, emergency_bool)
    allocation = generate_allocation(risk_score)

    print("\nRisk Score:", risk_score)

    display_allocation(monthly_investment, allocation)


if __name__ == "__main__":
    main()
