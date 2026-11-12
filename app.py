# notes:
# for now, I plan to utilize Flask
# In the future, I want to port the project over to react
# import statements
from math import isfinite
from flask import *
from database import *
from portfolio import *

# Init flask application
app = Flask(__name__) # I forgot that its Flask not flask

# We need to init the db
initialize_db()

# im going to section this off similar to assembly
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Home dashboard section:
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route('/')
def home():
    # retrieve port information so that we can create a dashboard
    portfolios = get_portfolios()

    # The dashboard uses the saved holdings for the selected portfolio.
    portfolio_id = request.args.get('portfolio_id', type=int)
    selected_portfolio = get_portfolio(portfolio_id) if portfolio_id is not None else (portfolios[0] if portfolios else None)
    if portfolio_id is not None and selected_portfolio is None:
        abort(404, description="Portfolio not found")
    holdings = get_holdings(selected_portfolio['id']) if selected_portfolio else []
    summary = calculate_portfolio_summary(holdings)

    # return statement should display the index.html screen with the getting started guide
    return render_template(
        "index.html",
        portfolios=portfolios,
        selected_portfolio=selected_portfolio,
        holdings=holdings,
        summary=summary
    )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Portfolio Management section:
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        name = request.form.get('name', '').strip() # gets the name data
        # Only create a port if a name is given
        if not name:
            abort(400, description="Name is required")
        # save port
        create_portfolio(name)

        return redirect(url_for('portfolio'))

    portfolios = get_portfolios()

    # Display list
    return render_template(
        "portfolio.html",
        portfolios=portfolios
    )

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Holdings section:
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# This section is a bit more complex
@app.route("/portfolio/<int:portfolio_id>/holdings")
def manage_holdings(portfolio_id):
    # Find the created port. remember that we are giving it a unique id
    selected_portfolio = get_portfolio(portfolio_id)

    # Return a 404 error if the portfolio does not exist
    if selected_portfolio is None:
        abort(404, description="Portfolio not found")

    holdings = get_holdings(portfolio_id)

    # display the holding management page
    return render_template(
        "holdings.html",
        portfolio=selected_portfolio,
        holdings=holdings
    )

# Add holding:
@app.route("/portfolio/<int:portfolio_id>/add", methods=['GET', 'POST'])
def create_holding(portfolio_id): # input requires port id
    # confirm the selected port is even real
    selected_portfolio = get_portfolio(portfolio_id)
    if selected_portfolio is None:
        abort(404, description="Portfolio not found")
    if request.method == 'POST':
        # retrieve the stock ticker from the form
        # in the future, we will want to make sure this stock ticker exists
        ticker = request.form.get("ticker", "").strip().upper()
        # convert numerical form entires to numbers
        try:
            shares = float(request.form.get("shares", ""))
            purchase_price = float(request.form.get("purchase_price", ""))
            current_price = float(request.form.get("current_price", "")) # automate this part in the future

        # handle invalid inputs
        except ValueError:
            abort(400, description="Invalid numerical values")

        # check if the inputs are acceptable
        if (not ticker or not all(isfinite(value) for value in (shares, purchase_price, current_price))
                or shares <= 0 or purchase_price < 0 or current_price < 0):
            abort(400, description="Invalid values")

        # If all is true and right, add to db
        add_holding(portfolio_id, ticker, shares, purchase_price, current_price)

        # return to the holdings page
        return redirect(url_for('manage_holdings', portfolio_id=portfolio_id))

        # display the form for adding new holding
    return render_template(
        "add_holding.html",
        portfolio=selected_portfolio,
    )

# Edit holding:
@app.route("/holding/<int:holding_id>/edit", methods=['GET', 'POST'])
def edit_holding(holding_id):
    # retrieve all info that we would want to modify
    holding = get_holding(holding_id)

    # Check if holding is true or not
    if holding is None:
        abort(404, description="Holding not found")

    if request.method == 'POST':
        # retrieve the updated symbol
        ticker = request.form.get("ticker", "").strip().upper()

        # now we need to convert the values to numbers
        try:
            shares = float(request.form.get("shares", ""))
            purchase_price = float(request.form.get("purchase_price", ""))
            current_price = float(request.form.get("current_price", ""))
        except ValueError:
            # if the numbers are wrong abort
            abort(400, description="Invalid numerical values")
        if (not ticker or not all(isfinite(value) for value in (shares, purchase_price, current_price))
                or shares <= 0 or purchase_price < 0 or current_price < 0):
            abort(400, description="Invalid values")
        # save info and update to db
        update_holding(holding_id, ticker, shares, purchase_price, current_price)

        # return to original port
        return redirect(url_for('manage_holdings', portfolio_id=holding["portfolio_id"]))
    return render_template("edit_holding.html", holding=holding)

# Remove holding:
@app.route("/holding/<int:holding_id>/delete", methods=["POST"])
def remove_holding(holding_id):
    # copy most of the above part
    # retrieve all info that we would want to modify
    holding = get_holding(holding_id)

    # Check if holding is true or not
    if holding is None:
        abort(404, description="Holding not found")

    # remember which port the holding is in
    portfolio_id = holding["portfolio_id"]

    # delete the holding
    delete_holding(holding_id)

    # return statement
    return redirect(url_for('manage_holdings', portfolio_id=portfolio_id))

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Port Information section:
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/portfolio/<int:portfolio_id>/information")
def  portfolio_information(portfolio_id):
    # retrieve the portfolio and all of its information (holdings)
    selected_portfolio = get_portfolio(portfolio_id)

    if selected_portfolio is None:
        abort(404, description="Portfolio not found")

    holdings = get_holdings(portfolio_id)

    # calc total value, invest amount, and p/l
    summary = calculate_portfolio_summary(holdings)

    # Display summary/detailed stats
    return render_template("information.html", portfolio=selected_portfolio, holdings=holdings, summary=summary)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Port Charts section:
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/portfolio/<int:portfolio_id>/charts")
def charts(portfolio_id):

    # Retrieve the selected portfolio.
    selected_portfolio = get_portfolio(portfolio_id)

    if selected_portfolio is None:
        abort(404, description="Portfolio not found")

    # Retrieve investment information for charting.
    holdings = get_holdings(portfolio_id)

    # Calculate portfolio statistics for our charts.
    summary = calculate_portfolio_summary(holdings)

    # Display the charting page.
    return render_template(
        "charts.html",
        portfolio=selected_portfolio,
        holdings=holdings,
        summary=summary
    )

# App Start section:
# Only start Flask when this file is run directly.
if __name__ == "__main__":
    app.run(debug=True)