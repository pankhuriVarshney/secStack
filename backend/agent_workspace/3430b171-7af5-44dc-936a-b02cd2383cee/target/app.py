
import sqlite3
from flask import Flask, request
app = Flask(__name__)
FLAG = open("/flag.txt").read().strip()
db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript("""
    CREATE TABLE users(username TEXT, password TEXT, flag TEXT);
    INSERT INTO users VALUES('admin','s3cr3t!','FLAG{web-sqli-login_a3a3cc54e9b4}');
    INSERT INTO users VALUES('alice','wonderland','');
    INSERT INTO users VALUES('bob','builder','');
""")
FORM = """
<h2>Admin Panel</h2><form method="POST" action="/login">
<input name="username" placeholder="username">
<input name="password" type="password" placeholder="password">
<button>Login</button></form>
"""
@app.route("/", methods=["GET"])
def home(): return FORM
@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    q = "SELECT username, flag FROM users WHERE username='%s' AND password='%s'" % (u, p)
    try:
        row = db.execute(q).fetchone()
    except Exception as e:
        return f"<pre>SQL error: {e}</pre>" + FORM
    if row and row[0] == "admin":
        return f"<h3>Welcome, admin.</h3><p>Your flag: <b>{row[1]}</b></p>"
    return "Invalid credentials." + FORM
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
