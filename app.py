from flask import Flask, render_template, redirect, session, request, jsonify
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "zyx987123abc"

db = SQL("sqlite:///lib50.db")

@app.route("/")
def index(alert_details={}):
  if not session.get("user_id"):
    return redirect("/login")
  else:
    borrowed_books = db.execute("""
      SELECT title, author, borrow_date, due_date
      FROM borrowings
      JOIN books ON borrowings.book_id = books.id
      WHERE user_id = ?
    """, session["user_id"])

    now = datetime.now()
    today_date = now.strftime("%B %d, %Y")
    today_date_formatted = datetime.strptime(today_date, "%B %d, %Y")

    for borrowed_book in borrowed_books:
      due_date = borrowed_book["due_date"]

      due_date_formatted = datetime.strptime(due_date, "%B %d, %Y")

      difference_in_days = (due_date_formatted - today_date_formatted).days

      if difference_in_days < 0:
        borrowed_book["overdue"] = True

    return render_template("index.html", name=session["username"], borrowed_books=borrowed_books, alert_details=alert_details, active="home")
  

@app.route("/login", methods=["GET", "POST"])
def login(redirect_from_register=False):
  if redirect_from_register:
    return render_template("login.html", redirect_from_register=True)

  if request.method == "GET":
    return render_template("login.html")
  else:
    username, password = request.form["username"].strip(), request.form["password"]

    rows = (
      db.execute("""
        SELECT id AS user_id, password_hash
        FROM users
        WHERE username = ?
      """, username))
    if len(rows) == 0:
      return render_template("login.html", invalid_credentials=True)

    user_id, password_hash = rows[0].get("user_id"), rows[0].get("password_hash")

    if not check_password_hash(password_hash, password):
      return render_template("login.html", invalid_credentials=True)

    session["user_id"], session["username"] = user_id, username

    return redirect("/")

  
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "GET":
    return render_template("register.html")
  else:
    full_name, username = request.form["full_name"].strip(), request.form["username"].strip()
    password, confirm_password = request.form["password"], request.form["confirm_password"]

    if password != confirm_password:
      return render_template("register.html", passwords_unmatch=True, full_name=full_name, username=username)

    rows = (
      db.execute("""
        SELECT username
        FROM users
        WHERE username = ?
      """, username))
    if len(rows) > 0:
      return render_template("register.html", username_exists=True)

    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    db.execute("""
      INSERT INTO
      users (name, username, password_hash)
      VALUES (?, ?, ?)
    """, full_name, username, password_hash)

    return login(redirect_from_register=True)


@app.route("/browse", methods=["GET", "POST"])
def browse():
  if request.method == "GET":
    return render_template("browse.html", active="browse")
  else:
    book_id = request.form.get("book_id")

    # Check for existence of the book
    rows = db.execute("""
      SELECT id
      FROM books
      WHERE id = ?
    """, book_id)
    if not rows:
      return render_template("browse.html", borrow_book_error=True, active="browse")

    # Check if the book is currently borrowed by anyone
    rows = db.execute("""
      SELECT book_id
      FROM borrowings
      WHERE book_id = ?
    """, book_id)
    if rows:
      return render_template("browse.html", borrow_book_error=True, active="browse")

    now = datetime.now()
    today_date = borrow_date = now.strftime("%B %d, %Y")
    due_date = (now + timedelta(days=7)).strftime("%B %d, %Y")

    db.execute("""
      INSERT INTO
      borrowings (book_id, user_id, borrow_date, due_date)
      VALUES (?, ?, ?, ?)
    """, book_id, session["user_id"], borrow_date, due_date)

    db.execute("""
      INSERT INTO
      history (book_id, user_id, action, date)
      VALUES (?, ?, ?, ?)
    """, book_id, session["user_id"], "Borrow", today_date)

    book_title = db.execute("""
      SELECT title
      FROM books
      WHERE id = ?
    """, book_id)[0]["title"]

    return index(alert_details={'action': 'borrow', 'book_title': book_title})
  

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")

@app.route("/fetch")
def fetch():
  query = request.args.get("q")
  if not query:
    return jsonify([])
  
  results = db.execute("""
    SELECT books.id, title, author, genre, borrowings.user_id
    FROM books
    LEFT JOIN borrowings ON books.id = borrowings.book_id
    WHERE
      title LIKE ? OR
      author LIKE ? OR
      genre LIKE ?
    LIMIT 15
  """, f"%{query}%", f"%{query}%", f"%{query}%")

  return jsonify(results)


@app.route("/return", methods=["GET", "POST"])
def return_book():
  borrowed_books = db.execute("""
    SELECT book_id, title
    FROM borrowings
    JOIN books ON borrowings.book_id = books.id
    WHERE user_id = ?
  """, session["user_id"])

  if request.method == "GET":
    return render_template("return.html", borrowed_books=borrowed_books, active="return")
  else:
    book_id = request.form.get("book_id")
    if not book_id:
      return render_template("return.html", no_book_selected=True, borrowed_books=borrowed_books, active="return")

    # Check if the book exists AND currently borrowed
    rows = db.execute("""
      SELECT book_id
      FROM books
      JOIN borrowings ON books.id = borrowings.book_id
      WHERE user_id = ? AND book_id = ?
    """, session["user_id"], book_id)
    if not rows:
      return render_template("return.html", return_book_error=True, borrowed_books=borrowed_books, active="return")

    db.execute("""
      DELETE FROM
      borrowings
      WHERE user_id = ? AND book_id = ?
    """, session["user_id"], book_id)

    now = datetime.now()
    return_date = now.strftime("%B %d, %Y")

    db.execute("""
      INSERT INTO
      history (book_id, user_id, action, date)
      VALUES (?, ?, ?, ?)
    """, book_id, session["user_id"], "Return", return_date)

    book_title = db.execute("""
      SELECT title
      FROM books
      WHERE id = ?
    """, book_id)[0]["title"]

    return index(alert_details={'action': 'return', 'book_title': book_title})

@app.route("/history", methods=["GET", "POST"])
def history():
  if request.method == "GET":
    history = db.execute("""
      SELECT title, action, date
      FROM history
      JOIN books ON history.book_id = books.id
      WHERE user_id = ?
    """, session["user_id"])

    return render_template("history.html", history=history, active="history")
  else:
    db.execute("""
      DELETE
      FROM history
      WHERE user_id = ?
    """, session["user_id"])

    return render_template("history.html", active="history")
