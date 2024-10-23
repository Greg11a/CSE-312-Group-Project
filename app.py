import bcrypt
import secrets
import hashlib
import uuid
import time
from auth import extract_credential, validate_password
from db import get_user_by_username, create_user, store_auth_token, delete_auth_token
from flask import (
    Flask,
    request,
    render_template,
    send_from_directory,
    make_response,
    redirect,
    url_for,
    flash,
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# --------------------------Helper Functions---------------------------
# ---------------------------------------------------------------------

@app.route("/")  # root route
def index():
    response = make_response(render_template("index.html"))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user_by_username(username)
        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
                auth_token = str(uuid.uuid4())
                hash_auth_token = hashlib.sha256(auth_token.encode("utf-8")).hexdigest()
                store_auth_token(username, hash_auth_token, time.time() + 3600)
                response = make_response(redirect(url_for("index")))
                response.set_cookie('auth_token', auth_token, max_age=60*60, httponly=True)
                flash("Login successful!", "success")
                return response
            else:
                flash("Invalid username or password", "error")
                return render_template("login.html", message="Invalid username or password")
        else:
            flash("Invalid username or password", "error")
            return render_template("login.html", message="Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    auth_token = request.cookies.get("auth_token")
    if auth_token:
            token_hash = hashlib.sha256(auth_token.encode('utf-8')).hexdigest()
            delete_auth_token(token_hash)
    response = make_response(redirect(url_for("index")))
    response.set_cookie('auth_token', '', max_age=0, httponly=True)
    flash("Logout Successfully!", "success")
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            comfirm_password = request.form.get("confirm_password")
            is_valid, validation_message = validate_password(password)
            if not is_valid:
                flash(validation_message, "error")
                return render_template("register.html", message=validation_message)
            existing_user = get_user_by_username(username)
            if existing_user:
                flash("User already exists!", "error")
                return render_template("register.html", message="User already exists!")
            if password != comfirm_password:
                flash("Password mismatched!", "error")
                return render_template("register.html", message="Password Mismatched!")
            create_user(username, password)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "error")
            flash("Registration failed!", "error")
            return render_template("register.html", message="Registration failed!")
    return render_template("register.html")
    

@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template("404.html"), 404)
    return response


@app.route("/static/css/<path:filename>")
def serve_css(filename):
    response = send_from_directory("static/css", filename)
    return response, 200, {"Content-Type": "text/css; charset=utf-8"}


@app.route("/static/js/<path:filename>")
def serve_js(filename):
    response = send_from_directory("static/js", filename)
    return response, 200, {"Content-Type": "text/javascript; charset=utf-8"}


@app.route("/static/images/<path:filename>")
def serve_image(filename):
    response = send_from_directory("static/images", filename)
    return response, 200, {"Content-Type": "image/jpeg"}


# ---------------------------Test Route---------------------------
@app.route("/test")  # for test purpose only, Modify this if you have any to try out
def hello_world():
    return "<h1>Hello!</h1>"


# ---------------------------After Request---------------------------
@app.after_request
def secure_header(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# ---------------------------Other Implementations---------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
    # debug=True allow you to see modification immediately
