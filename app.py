from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, hashlib, base64, re
from PIL import Image
from cryptography.fernet import Fernet
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ---------------- #
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT,
name TEXT,
email TEXT,
mobile TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
action TEXT,
timestamp TEXT)""")

conn.commit()

# ---------------- HELPERS ---------------- #
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def generate_key(k):
    return base64.urlsafe_b64encode(hashlib.sha256(k.encode()).digest())

def log_action(user, action):
    cursor.execute("INSERT INTO history VALUES(NULL,?,?,?)",
                   (user, action,
                    datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()

def is_valid_email(e):
    return re.match(r"[^@]+@[^@]+\.[^@]+", e)

def is_valid_mobile(m):
    return m.isdigit() and len(m) == 10

# ---------------- STEGANOGRAPHY ---------------- #
def encode_image(path, data, out):
    img = Image.open(path)
    encoded = img.copy()
    binary = ''.join(format(ord(i), '08b') for i in data)
    idx = 0

    for r in range(img.height):
        for c in range(img.width):
            pixel = list(img.getpixel((c, r)))
            for n in range(3):
                if idx < len(binary):
                    pixel[n] = pixel[n] & ~1 | int(binary[idx])
                    idx += 1
            encoded.putpixel((c, r), tuple(pixel))
            if idx >= len(binary):
                encoded.save(out)
                return True
    return False


def decode_image(path):
    img = Image.open(path)
    binary = ""

    for r in range(img.height):
        for c in range(img.width):
            pixel = img.getpixel((c, r))
            for n in range(3):
                binary += str(pixel[n] & 1)

    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        chars.append(chr(int(byte, 2)))
        if ''.join(chars).endswith("###"):
            break

    message = ''.join(chars)
    return message.replace("###", "") if "###" in message else ""


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("login.html")


# ---------------- AUTH ---------------- #
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = hash_password(request.form.get("password"))

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, password))
    user = cursor.fetchone()

    if user:
        session["user"] = username
        return redirect("/dashboard")

    return "Invalid credentials"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if not is_valid_email(request.form.get("email")):
        return "Invalid Email"

    if not is_valid_mobile(request.form.get("mobile")):
        return "Invalid Mobile"

    try:
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?)", (
            request.form.get("username"),
            hash_password(request.form.get("password")),
            request.form.get("name"),
            request.form.get("email"),
            request.form.get("mobile")
        ))
        conn.commit()
        return redirect("/")
    except:
        return "Username already exists"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", username=session["user"])


# ---------------- PROFILE ---------------- #
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/")

    user = cursor.execute(
        "SELECT name,email,mobile FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()

    return render_template(
        "profile.html",
        username=session["user"],
        name=user[0],
        email=user[1],
        mobile=user[2]
    )


# ---------------- HISTORY ---------------- #
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")

    rows = cursor.execute(
        "SELECT action, timestamp FROM history WHERE username=?",
        (session["user"],)
    ).fetchall()

    return render_template("history.html", history=rows)


# ---------------- ENCODE ---------------- #
@app.route("/encode", methods=["GET", "POST"])
def encode():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        file = request.files.get("image")
        msg = request.form.get("message")
        key = request.form.get("key")

        if not file or file.filename == "":
            return "No image selected"

        if not msg:
            return "Message missing"

        if not key:
            return "Key missing"

        input_path = "temp_input.png"
        output_path = "encoded.png"

        file.save(input_path)

        encrypted = Fernet(generate_key(key)).encrypt(msg.encode()).decode() + "###"

        if encode_image(input_path, encrypted, output_path):
            log_action(session["user"], "Encoded")
            return send_file(output_path, as_attachment=True)

        return "Encoding failed"

    return render_template("encode.html")


# ---------------- DECODE ---------------- #
@app.route("/decode", methods=["GET", "POST"])
def decode():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        file = request.files.get("image")
        key = request.form.get("key")

        if not file or file.filename == "":
            return render_template("decode.html", error="No image selected")

        if not key:
            return render_template("decode.html", error="Key missing")

        input_path = "temp_decode.png"
        file.save(input_path)

        hidden = decode_image(input_path)

        if not hidden:
            return render_template("decode.html", error="No hidden message found")

        try:
            msg = Fernet(generate_key(key)).decrypt(hidden.encode()).decode()
            log_action(session["user"], "Decoded")
            return render_template("decode.html", message=msg)
        except:
            return render_template("decode.html", error="Wrong key or corrupted image")

    return render_template("decode.html")


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)