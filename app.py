import bcrypt
import hashlib
import secrets
import time
import uuid
import db
import os

from bson import ObjectId
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect
from auth import extract_credential, validate_password
from werkzeug.utils import secure_filename

from flask import (
    Flask,
    request,
    render_template,
    send_from_directory,
    make_response,
    redirect,
    url_for,
    flash,
    jsonify,
)



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.jinja_env.autoescape = True
csrf = CSRFProtect(app)


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


def format_timestamp(timestamp):
    now = datetime.now()
    post_time = datetime.fromtimestamp(timestamp)
    diff = now - post_time
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes}m"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours}h"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}d"
    else:
        return post_time.strftime("%b %d, %Y")


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


# @app.route("/create_post", methods=["POST"])
# def create_post():
#     username = get_current_user()
#     if not username:
#         flash("You need to be logged in to post!", "error")
#         return redirect(url_for("login"))
#     post_content = request.form.get("post_content")
#     if not post_content.strip():
#         flash("Post content cannot be empty!", "error")
#         return redirect(url_for("index"))
#     post_data = {
#         "username": username,
#         "content": post_content,
#         "timestamp": time.time(),
#         "likes": [],
#     }
#     db.posts_collection.insert_one(post_data)
#     flash("Post created successfully!", "success")
#     return redirect(url_for("index"))

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
@app.route("/create_post", methods=["POST"])
def create_post():
    MAX_VIDEO_SIZE_MB = 50
    MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
    MAX_IMAGE_SIZE_MB = 10  
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

    username = get_current_user()
    if not username:
        flash("You need to be logged in to post!", "error")
        return redirect(url_for("login"))

    post_content = request.form.get("post_content")
    video_file = request.files.get("video")
    image_file = request.files.get("image")

    if not post_content.strip():
        flash("Post content cannot be empty!", "error")
        return redirect(url_for("index"))

    video_path = None
    image_path = None

    video_directory = "static/uploads/videos"
    image_directory = "static/uploads/images"

    ensure_directory_exists(video_directory)
    ensure_directory_exists(image_directory)

    if video_file:

        video_file.seek(0, os.SEEK_END)
        file_size = video_file.tell()
        video_file.seek(0)

        if file_size > MAX_VIDEO_SIZE_BYTES:
            flash(f"File size exceeds {MAX_VIDEO_SIZE_MB}MB limit.", "error")
            return redirect(url_for("index"))

        if video_file.filename.split('.')[-1].lower() in ['mp4', 'mov', 'avi', 'mkv']:
            filename = secure_filename(video_file.filename)
            video_path = os.path.join("static/uploads/videos", filename)
            video_file.save(video_path)
        else:
            flash("Invalid file type. Please upload a video file.", "error")
            return redirect(url_for("index"))
        
    if image_file:

        image_file.seek(0, os.SEEK_END)
        file_size = image_file.tell()
        image_file.seek(0)

        if file_size > MAX_IMAGE_SIZE_BYTES:
            flash(f"File size exceeds {MAX_IMAGE_SIZE_MB}MB limit.", "error")
            return redirect(url_for("index"))

        if image_file.filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif']:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join("static/uploads/images", filename)
            image_file.save(image_path)

        else:
            flash("Invalid file type. Please upload a image file.", "error")
            return redirect(url_for("index"))
        

    post_data = {
        "username": username,
        "content": post_content,
        "timestamp": time.time(),
        "likes": [],
        "video_path": video_path,
        "image_path": image_path 
    }

    db.posts_collection.insert_one(post_data)
    flash("Post created successfully!", "success")
    return redirect(url_for("index"))

@app.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):
    username = get_current_user()
    if not username:
        return redirect(url_for("login"))
    post = db.posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        return redirect(url_for("index"))
    if username in post["likes"]:
        db.posts_collection.update_one(
            {"_id": ObjectId(post_id)}, {"$pull": {"likes": username}}
        )
    else:
        db.posts_collection.update_one(
            {"_id": ObjectId(post_id)}, {"$push": {"likes": username}}
        )
    return redirect(url_for("index"))

@app.route("/delete_post/<post_id>", methods=["POST"])
def delete_post(post_id):
    username = get_current_user()
    if not username:
        flash("You need to be logged in to delete a post!", "error")
        return redirect(url_for("login"))
    
    post = db.posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("index"))
    
    if post["username"] != username:
        flash("You can only delete your own posts!", "error")
        return redirect(url_for("index"))
    
    db.posts_collection.delete_one({"_id": ObjectId(post_id)})
    flash("Post deleted successfully!", "success")
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