import os

#from dotenv import load_dotenv  # Load environment variables early (for API_KEY in helpers.lookup)
#load_dotenv()  # Loads .env from app root; falls back silently if missing

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
#db = SQL("sqlite:////home/cs50finance/finance/finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    # Fetch stocks with net shares
    stocks = db.execute("""
        SELECT symbol, SUM(CASE WHEN type = 'buy' THEN shares ELSE -shares END) as total_shares, MAX(transacted) as last_transacted
        FROM transactions
        WHERE user_id = ? AND type IN ('buy', 'sell')
        GROUP BY symbol
        HAVING total_shares > 0
    """, user_id)
    # Fetch deposits
    deposits = db.execute("""
        SELECT 'CASH' as symbol, 1 as total_shares, price, transacted as last_transacted
        FROM transactions
        WHERE user_id = ? AND type = 'deposit'
    """, user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    total_value = cash
    portfolio_items = []
    for stock in stocks:
        quote = lookup(stock["symbol"])
        if quote:
            stock["price"] = quote["price"]
            stock["value"] = stock["price"] * stock["total_shares"]
            stock["name"] = quote["name"]
            total_value += stock["value"]
        else:
            stock["price"] = 0
            stock["value"] = 0
            stock["name"] = stock["symbol"]
        portfolio_items.append(stock)
    for dep in deposits:
        dep["name"] = "Deposit"
        dep["price"] = dep["price"]
        dep["value"] = dep["price"]
        portfolio_items.append(dep)
    # Sort combined by last_transacted
    portfolio_items.sort(key=lambda x: x['last_transacted'])
    return render_template("index.html", portfolio_items=portfolio_items, cash=usd(cash), total=usd(total_value))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")
        if not symbol:
            return apology("must provide symbol")
        if not shares_str:
            return apology("must provide shares")
        try:
            shares = int(shares_str)
            if shares <= 0:
                return apology("shares must be positive integer")
        except ValueError:
            return apology("shares must be integer")
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol")
        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        cost = quote["price"] * shares
        if cost > cash:
            return apology("can't afford")
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, 'buy')", user_id, quote["symbol"], shares, quote["price"])
        flash("Bought!")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("""
        SELECT type, symbol, shares, price, transacted
        FROM transactions
        WHERE user_id = ?
        ORDER BY transacted DESC
    """, session["user_id"])
    for t in transactions:
        t["price"] = usd(t["price"])
        if t["type"] == "deposit":
            t["symbol"] = "CASH"  # Keep for clarity
            t["shares"] = ""  # Blank shares
        t["type"] = t["type"].capitalize()
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol")
        return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if password != confirmation:
            return apology("passwords do not match")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username taken")
        hash_pass = generate_password_hash(password, method='pbkdf2:sha256')
        id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash_pass)
        session["user_id"] = id
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")
        if not symbol:
            return apology("must select symbol")
        if not shares_str:
            return apology("must provide shares")
        try:
            shares = int(shares_str)
            if shares <= 0:
                return apology("shares must be positive integer")
        except ValueError:
            return apology("shares must be integer")
        owned = db.execute("""
            SELECT SUM(CASE WHEN type = 'buy' THEN shares ELSE -shares END) as total
            FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
        """, user_id, symbol)
        owned_shares = owned[0]["total"] if owned else 0
        if owned_shares < shares:
            return apology("not enough shares")
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol")
        proceeds = quote["price"] * shares
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", proceeds, user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, ?, ?, ?, 'sell')", user_id, quote["symbol"], shares, quote["price"])
        flash("Sold!")
        return redirect("/")
    else:
        symbols = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(CASE WHEN type = 'buy' THEN shares ELSE -shares END) > 0
        """, user_id)
        return render_template("sell.html", symbols=[s["symbol"] for s in symbols])


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        amount_str = request.form.get("amount")
        if not amount_str:
            return apology("must provide amount")
        try:
            amount = float(amount_str)
            if amount <= 0:
                return apology("positive amount required")
        except ValueError:
            return apology("invalid amount")
        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES(?, 'CASH', 1, ?, 'deposit')", user_id, amount)
        flash("Cash added!")
        return redirect("/")
    else:
        return render_template("add_cash.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
