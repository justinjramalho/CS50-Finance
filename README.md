# CS50 Finance

This repository contains the source code for C$50 Finance, a Flask-based web app for virtual stock trading. Built as part of Harvard's CS50x Introduction to Computer Science (Web Track), it simulates managing stock portfolios with real-time quotes from Alpha Vantage.

👉 [View project details on my portfolio](https://www.justinjramalho.com/projects/developer/c50-finance)

## 🚀 Project Overview

C$50 Finance allows users to register, log in, look up stock prices, buy/sell shares, track portfolios, and view transaction history. It uses SQLite for persistent storage of users, transactions, and cash balances, with a responsive UI via Jinja2 templates and Bootstrap. The app follows CS50x guidelines for secure password hashing (via werkzeug.security), error handling (e.g., apologies for invalid inputs), and dynamic routing. Designed for educational purposes, it includes accessibility features like alt text for images and keyboard navigation, making it suitable for K-12 demos. Placeholders/mock data can be used for testing API limits.

## 🛠️ Tech Stack

This web app was developed using the following technologies:

* Backend: Python 3, Flask, Jinja2, CS50 SQL library
* Database: SQLite (for users, transactions, portfolios)
* Frontend: HTML5, CSS3, Bootstrap (for responsive navbar and forms)
* APIs: Alpha Vantage (for stock quotes via `lookup()` helper)
* Security: werkzeug.security (for password hashing)
* Version Control: Git & GitHub
* Deployment: PythonAnywhere (free tier for public hosting)

## ✨ Key Features

* User Authentication: Register/login with hashed passwords; logout functionality.
* Stock Quote Lookup: Search symbols (e.g., NFLX) and display real-time prices/names via `/quote`.
* Buy/Sell Stocks: Purchase/sell shares at current prices, updating cash and portfolios (validates affordability and ownership).
* Portfolio Tracking: View owned stocks, shares, values, cash balance, and grand total in a table at `/index`.
* Transaction History: Chronological log of buys, sells, and cash deposits at `/history`.
* Add Cash: Personal touch feature to deposit funds via `/add_cash`.
* Responsive Design: Mobile-friendly layout with centered forms and tables; accessibility via Bootstrap.
* Error Handling: Custom apologies for invalid inputs (e.g., non-positive shares, invalid symbols).

## 💻 How to Run

1. **Live Demo**: The app is deployed and accessible at [https://cs50finance.pythonanywhere.com/](https://cs50finance.pythonanywhere.com/).
2. **Local Setup**:
   - Clone the repository:
        ```bash
        git clone https://github.com/justinjramalho/CS50-Finance.git
        cd CS50-Finance
   - Create and activate a virtual environment:
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
   - Install dependencies:
        ```bash
        pip install -r requirements.txt
   - Create the SQLite database (finance.db) and schema (run these commands in your terminal to initialize the required tables):
        ```bash
        sqlite3 finance.db
   - Then, inside the sqlite3 prompt, execute:
        ```bash
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            cash NUMERIC NOT NULL DEFAULT 10000.00
        );
        CREATE UNIQUE INDEX username ON users (username);

        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            shares INTEGER NOT NULL,
            price NUMERIC NOT NULL,
            type TEXT NOT NULL,
            transacted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        .quit
   - Set your Alpha Vantage API key (sign up at https://www.alphavantage.co/support/#api-key):
        ```bash
        export API_KEY=your_api_key_here  # On Windows: set API_KEY=your_api_key_here
   - Run the app:
        ```bash
        flask run
   - Visit http://127.0.0.1:5000 in your browser. Register an account to start trading virtually.

**For deployment to PythonAnywhere**, upload code (excluding venv), recreate virtualenv, configure the API key via .env file, configure WSGI, and reload the web app. Detailed steps:
- Create a `.env` file in your app directory with `API_KEY=your_api_key_here`.
- Install `python-dotenv` in your virtualenv: `pip install python-dotenv` and add it to `requirements.txt`.
- Update the WSGI file to load the .env before importing your app (see deployment guide or repo for exact code).
- Reload the web app in the PythonAnywhere dashboard.

This README was last updated on August 02, 2025.