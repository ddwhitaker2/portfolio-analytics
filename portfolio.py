
# This file is going to handle all the calculations for our portfolios.
# We need to calculate how much money was invested, the current value,
# and how much money the user has gained or lost.


def calculate_portfolio_summary(holdings):

    # First we need to set our starting values to 0.
    total_invested = 0
    total_value = 0
    holding_info = []

    # Go through each stock the user has in their portfolio.
    for holding in holdings:

        # Figure out how much the user originally paid for the stock.
        cost = holding["shares"] * holding["purchase_price"]

        # Now we need to figure out what the stock is worth currently.
        current = holding["shares"] * holding["current_price"]

        # Add these values to our overall portfolio totals.
        total_invested += cost
        total_value += current

        # Store the information so we can use it for charts later.
        # We also need to avoid dividing by 0.
        if cost > 0:
            percent = ((current - cost) / cost) * 100
        else:
            percent = 0

        holding_info.append({
            "ticker": holding["ticker"],
            "shares": holding["shares"],
            "cost_basis": cost,
            "market_value": current,
            "gain_loss": current - cost,
            "gain_loss_percent": percent
        })

    # Figure out what percentage of the portfolio each stock makes up.
    for holding in holding_info:
        if total_value > 0:
            holding["allocation_percent"] = (
                holding["market_value"] / total_value
            ) * 100
        else:
            holding["allocation_percent"] = 0

    # Finally we need to calculate the total profit/loss.
    gain_loss = total_value - total_invested

    if total_invested > 0:
        gain_percent = (gain_loss / total_invested) * 100
    else:
        gain_percent = 0

    # Return everything so app.py can display it on the website.
    return {
        "total_invested": total_invested,
        "total_value": total_value,
        "total_gain_loss": gain_loss,
        "total_gain_loss_percent": gain_percent,
        "holdings": holding_info
    }
