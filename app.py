from cs50 import SQL
from flask import Flask, render_template, request, redirect, flash
import math
from flask_session import Session
from datetime import datetime
from tempfile import mkdtemp

app = Flask(__name__)

db = SQL("sqlite:///calculation.db")

CONVERT = 1000000000;

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Index page
@app.route("/")
def index():
    return render_template("index.html")

# Calculator
@app.route("/calculator", methods=["GET", "POST"])
def calculator():

    # When input data
    if request.method == "POST":

        # Get parameters from the form
        format = request.form.get("format")
        length = int(request.form.get("length"))
        width = int(request.form.get("width"))
        density = int(request.form.get("density"))
        quantity = int(request.form.get("quantity"))
        defect = int(request.form.get("defect"))
        paper_price = float(request.form.get("paper_price"))
        timestamp = datetime.now().strftime('%H:%M %d/%m')
        
        # Identify price based on density
        list = db.execute("SELECT weight FROM density WHERE name = ?", density)
        weight = float(list[0].get('weight'))

        # Identify price based on density
        list = db.execute("SELECT width, length FROM format WHERE name = ?", format)
        paper_width = int(list[0].get('width'))
        print(paper_width)
        paper_length = int(list[0].get('length'))
        print(paper_length)
        
        # Calculate the maximum number of products on A2
        max_1 = (paper_length // length)*(paper_width // width)
        max_2 = (paper_length // width)*(paper_width // length)
        if (max_1 > max_2):
            max = max_1
        else:
            max = max_2
        print(max)
        # Calculate number of A2 needed
        sheets = math.floor(quantity / max) + defect
        
        # Вес листа
        weight = density * (paper_length + 20) * (paper_width + 12) / CONVERT;
        print (weight)
        
        # Calculate price
        total_price = round(sheets * weight * paper_price, 2)

        # Add data of the order to the history
        db.execute("INSERT INTO history (density, length, width, quantity, price, placed, format) VALUES(?, ?, ?, ?, ?, ?, ?)",
            density, length, width, quantity, total_price, timestamp, format)
            
        # Say that order is added successfully
        flash("New Order Placed!")
        
        # Chose the data from the database to pass to the history page
        elements = db.execute("""SELECT id AS number,
        density, length, width, quantity, placed,
        price, format
        FROM history""")
        
        # Go to the history page once the user posts input
        return render_template("history.html", elements=elements)

    # When just read data
    else:
        # Choose densities from the db
        rows = db.execute("SELECT name FROM density")
        
        # Выбрать формат из базы данных 
        rows2 = db.execute("SELECT name FROM format")
        
        # Выбрать цветность из базы данных 
        rows3 = db.execute("SELECT name FROM color")

        # return the form with densities
        return render_template("calculator.html", densities=[row["name"] for row in rows], formats=[row2["name"] for row2 in rows2], 
            colors=[row3["name"] for row3 in rows3])

# Order History
@app.route("/history")
def history():
    
    # Choose the data from the datatable and dispay in the table 
    elements = db.execute("""SELECT id AS number,
    density, length, width, quantity, placed, price
    FROM history""")
    
    # Show the history page
    return render_template("history.html", elements=elements)
    

