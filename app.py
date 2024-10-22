import bcrypt
import secrets
from auth import extract_credential, validate_password
from db import get_user_by_username, create_user
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


@app.route("/")  # root route
def home():
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
                flash("Login successful!", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid username or password", "error")
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username, password = extract_credential(
                request.query_string.decode("utf-8")
            )
            is_valid, validation_message = validate_password(password)
            if not is_valid:
                flash(validation_message, "error")
                return render_template("register.html")
            existing_user = get_user_by_username(username)
            if existing_user:
                flash("User already exists!", "error")
                return render_template("register.html")
            create_user(username, password)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("register.html")
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
