from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re

app=Flask(__name__)
app.secret_key="secure_secret_key"
login_attempts={}

def get_db():
    conn=sqlite3.connect("database.db")
    conn.row_factory=sqlite3.Row
    return conn

def create_table():
    conn=get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)""")
    conn.commit()
    conn.close()

create_table()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        if not re.match("^[A-Za-z0-9_]{4,20}$",username):
            flash("Invalid username format")
            return redirect("/register")
        
        if len(password)<6:
            flash("Password must be at least 6 characters")
            return redirect("/register")
        
        hashed_password=generate_password_hash(password)
        conn=get_db()

        try:
            conn.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",(username,hashed_password)
            )
            conn.commit()
            flash("Registration Successful")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists")
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        if username not in login_attempts:
            login_attempts[username]=0

        if login_attempts[username]>=3:
            flash("Account temporarily locked due to failed attempts")
            return redirect("/login")
        
        conn=get_db()
        user=conn.execute(
            "SELECT * FROM users WHERE username=?",(username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"],password):
            session["user"]=username
            login_attempts[username]=0
            flash("Login successful")
            return redirect("/dashboard")
        else:
            login_attempts[username]+=1
            flash("Invalid credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Login required")
        return redirect("/login")
    return render_template("dashboard.html",username=session["user"])


@app.route("/logout")
def logout():
    session.pop("user",None)
    flash("Logged out successfully")
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)