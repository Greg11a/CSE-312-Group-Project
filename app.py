from auth import extract_credential, validate_password
import bcrypt
from bson import ObjectId
from datetime import datetime
import db
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
import hashlib
import secrets
import time
import uuid


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.jinja_env.autoescape = True


# --------------------------Helper Functions---------------------------
def get_current_user():
    token = request.cookies.get("auth_token")
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    tokens_collection = db.get_collection("auth_tokens")
    auth_token = tokens_collection.find_one({"hashed_auth_token": token_hash})
    if auth_token and auth_token["expire"] > time.time():
        return auth_token["username"]
    return None


# ---------------------------------------------------------------------


@app.route("/")  # root route
def index():
    username = get_current_user()
    posts = db.posts_collection.find().sort("timestamp", -1)
    response = make_response(
        render_template("index.html", username=username, posts=posts)
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def format_timestamp(value, format="%Y-%m-%d %H:%M:%S"):
    return datetime.fromtimestamp(value).strftime(format)


app.jinja_env.filters["format_timestamp"] = format_timestamp


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.get_user_by_username(username)
        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
                auth_token = str(uuid.uuid4())
                hash_auth_token = hashlib.sha256(auth_token.encode("utf-8")).hexdigest()
                db.store_auth_token(username, hash_auth_token, time.time() + 3600)
                response = make_response(redirect(url_for("index")))
                response.set_cookie(
                    "auth_token", auth_token, max_age=60 * 60, httponly=True
                )
                flash("Login successful!", "success")
                return response
            else:
                flash("Invalid username or password", "error")
                return render_template(
                    "login.html", message="Invalid username or password"
                )
        else:
            flash("Invalid username or password", "error")
            return render_template("login.html", message="Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        token_hash = hashlib.sha256(auth_token.encode("utf-8")).hexdigest()
        db.delete_auth_token(token_hash)
    response = make_response(redirect(url_for("index")))
    response.set_cookie("auth_token", "", max_age=0, httponly=True)
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
            existing_user = db.get_user_by_username(username)
            if existing_user:
                flash("User already exists!", "error")
                return render_template("register.html", message="User already exists!")
            if password != comfirm_password:
                flash("Password mismatched!", "error")
                return render_template("register.html", message="Password Mismatched!")
            db.create_user(username, password)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "error")
            flash("Registration failed!", "error")
            return render_template("register.html", message="Registration failed!")
    return render_template("register.html")


@app.route("/create_post", methods=["POST"])
def create_post():
    username = get_current_user()
    if not username:
        flash("You need to be logged in to post!", "error")
        return redirect(url_for("login"))
    post_content = request.form.get("post_content")
    if not post_content.strip():
        flash("Post content cannot be empty!", "error")
        return redirect(url_for("index"))
    post_data = {
        "username": username,
        "content": post_content,
        "timestamp": time.time(),
        "likes": [],
    }
    db.posts_collection.insert_one(post_data)
    flash("Post created successfully!", "success")
    return redirect(url_for("index"))


@app.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    username = get_current_user()
    if not username:
        flash("You need to be logged in to like a post!", "error")
        return redirect(url_for("login"))
    post = db.posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Post not found!", "error")
        return redirect(url_for("index"))
    if username in post["likes"]:
        db.posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": username}}
        )
        flash("Post unliked successfully!", "success")
    else:
        db.posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"likes": username}}
        )
        flash("Post liked successfully!", "success")
    return redirect(url_for("index"))


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
