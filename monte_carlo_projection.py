import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np
import plotly.graph_objects as go

print("🌟 WELCOME! 🌟")
print("==============")
print("This tool provides investment projections based on historical data to help you visualize potential outcomes. Remember, past performance doesn't dictate future results.")
print("While these insights can be useful, they're not tailored financial advice. If you're making big financial decisions, having a chat with a financial advisor is always a good idea!")
print("Have fun exploring and always invest wisely!")
print("==============")
print("\n")

def main_investment_test():

    # ------------------------------
    # SECTION 1: FETCH HISTORICAL DATA
    # ------------------------------

    # Prompt for the stock ticker
    ticker = input("Which stock or index are you interested in? (e.g., AAPL for Apple or ^GSPC for S&P 500): ")

    # Prompt for the start date
    start_date = input("From which date should we begin the backtest? (format: YYYY-MM-DD): ")

    # Ensure the end_date captures current date, as in your original code
    end_date = input("From which date should we begin the backtest? (format: YYYY-MM-DD): ") #datetime.today().strftime('%Y-%m-%d')

    try:
        data = yf.download(ticker, start=start_date, end=end_date)
    except:
        print("Error fetching data. Please check your ticker and date inputs.")
        exit()

    # ------------------------------
    # SECTION 2: CALCULATE ANNUAL RETURNS
    # ------------------------------

    data['Annual Return'] = data['Close'].resample('A').ffill().pct_change().fillna(0)

    # ------------------------------
    # SECTION 3: CALCULATE AVERAGE ANNUAL RETURN AND VOLATILITY
    # ------------------------------

    average_annual_return = data['Annual Return'].mean()
    std_dev_return = data['Annual Return'].std()

    print(f"Average Annual Return: {average_annual_return*100:.2f}%")
    print(f"Standard Deviation of Returns: {std_dev_return*100:.2f}%")

    # ------------------------------
    # SECTION 4: MONTE CARLO PROJECTION
    # ------------------------------

    # Ask about the type of investment
    investment_type = input("Would you like to invest as a lump sum or periodically? (Enter 'lump sum' or 'periodic'): ").strip().lower()

    if investment_type == "lump sum":
        principal_amount = float(input("How much are you thinking of investing initially (in USD)? "))
        periodic_investment = 0
        periodic_frequency = None
    else:
        principal_amount = float(input("How much are you investing upfront (in USD), excluding any periodic contributions? "))
        periodic_investment = float(input("How much will you invest periodically (in USD)? "))
        periodic_frequency = input("How often will you make this investment? (Enter 'daily', 'weekly', 'monthly', or 'yearly'): ").strip().lower()

    # Prompt for the number of years for projection
    investment_years = int(input("Over how many years are you considering this investment? "))

    # Prompt for the number of simulations
    num_simulations = int(input("To make our projections robust, we'll run several simulations. How many simulations would you like? (typically 1000 or more): "))

    def monte_carlo_projection_with_contributions(principal, avg_return, std_dev, years, simulations=1000, periodic_invest=0, frequency=None):
        simulated_returns = np.random.normal(avg_return, std_dev, (years, simulations))

        if frequency:
            days_per_year = 252  # Trading days
            if frequency == "daily":
                contributions_per_year = days_per_year
            elif frequency == "weekly":
                contributions_per_year = days_per_year / 5
            elif frequency == "monthly":
                contributions_per_year = 12
            elif frequency == "yearly":
                contributions_per_year = 1
            else:
                raise ValueError("Invalid frequency specified")
            
            for year in range(years):
                principal += periodic_invest * contributions_per_year
                principal *= (1 + simulated_returns[year])

        else:
            future_values = principal * np.prod(1 + simulated_returns, axis=0)

        return principal
    
    projected_values = monte_carlo_projection_with_contributions(principal_amount, average_annual_return, std_dev_return, investment_years, num_simulations, periodic_investment, periodic_frequency)

    # ------------------------------
    # SECTION 5: PLOT THE GRAPH
    # ------------------------------

    # Split projected values based on relation to principal
    below_principal = [val for val in projected_values if val < principal_amount]
    above_principal = [val for val in projected_values if val >= principal_amount]

    fig = go.Figure()

    # Plotting values below principal
    fig.add_trace(go.Histogram(x=below_principal, name='LOSS', marker=dict(color='red')))

    # Plotting values above or equal to principal
    fig.add_trace(go.Histogram(x=above_principal, name='PROFIT', marker=dict(color='green')))

    fig.add_shape(
        go.layout.Shape(type='line', x0=np.mean(projected_values), x1=np.mean(projected_values), y0=0, y1=1, yref='paper', line=dict(color='red', dash='dash'))
    )
    fig.update_layout(title=f'{ticker} Investment Projection over {investment_years} Years', xaxis_title='Projected Value', yaxis_title='Frequency')
    fig.show()

    # ------------------------------
    # SECTION 6: CHATBOT ANALYSIS & ADVICE
    # ------------------------------

    def analyze_projections(projected_values, principal_amount):
        mean_projection = np.mean(projected_values)
        median_projection = np.median(projected_values)
        prob_of_loss = len([val for val in projected_values if val < principal_amount]) / len(projected_values)
        
        advice = ""
        
        # Comparative Analysis
        if average_annual_return > 0.07: # Assuming S&P 500 average annual return around 7%
            advice += f"The stock's average annual return is higher than typical benchmarks like the S&P 500. This might indicate a potentially higher reward but remember to evaluate the associated risks.\n"
        else:
            advice += f"The stock's average annual return is lower than benchmarks like the S&P 500. Consider understanding the reasons behind this before investing.\n"

        # Potential Risk Indication
        if std_dev_return > 0.2: # Assuming 20% as a high standard deviation
            advice += "The stock has high volatility, which means your investment might experience significant ups and downs. Ensure you're comfortable with this level of risk.\n"
        
        # Time Horizon Perspective
        if investment_years < 5 and mean_projection > principal_amount:
            advice += "Although the average projected value seems promising, your time horizon is short. Stocks are typically volatile in the short term.\n"
        elif investment_years >= 5 and mean_projection < principal_amount:
            advice += "Despite a longer time horizon, the average projected value is not promising. Diversifying or reconsidering your options might be a good idea.\n"

        # Historical Context
        if data['Close'].iloc[0] < data['Close'].iloc[-1]:
            advice += "Historically, this stock has shown growth from your start date till now. Past performance doesn't guarantee future results, but it provides context.\n"
        else:
            advice += "The stock has declined in value from your chosen start date till now. It's important to understand why before making an investment decision.\n"

        # Diversification Suggestion
        if prob_of_loss > 0.5:
            advice += "There's a substantial probability of not achieving your principal amount based on the simulations. Diversifying your portfolio can help mitigate such risks.\n"
        else:
            advice += "The simulations suggest a favorable outcome. Still, it's a good practice to diversify to protect against unforeseen market changes.\n"

        return advice

    chatbot_advice = analyze_projections(projected_values, principal_amount)
    print(chatbot_advice)

# Start the loop for testing investments
continue_testing = True

while continue_testing:
    main_investment_test()
    
    # Ask the user if they want to test another investment with more user-friendly messaging
    user_decision = input("\nWould you like to test another investment? Enter 'yes' to continue or any other key to exit: ").strip().lower()
    
    if user_decision != 'yes':
        continue_testing = False
        print("\nThank you for using the ELAMIN AI. See you again!")

