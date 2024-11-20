import bcrypt
import hashlib
import secrets
import time
import uuid
import db
import os
import json

from gevent import monkey
from flask_socketio import SocketIO, emit
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

# Monkey patch for Socket.IO
monkey.patch_all()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.jinja_env.autoescape = True

csrf = CSRFProtect(app)
socketio = SocketIO(app)

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

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

# ---------------------------------------------------------------------

@app.route("/")
def index():
    username = get_current_user()
    posts = db.posts_collection.find().sort("timestamp", -1)

    posts_with_avatars = []
    for post in posts:
        user = db.get_user_by_username(post["username"])
        avatar_path = (
            url_for("static", filename=user["avatar"])
            if user and "avatar" in user
            else url_for("static", filename="images/default_avatar.png")
        )
        post["avatar_path"] = avatar_path
        posts_with_avatars.append(post)

    response = make_response(
        render_template("index.html", username=username, posts=posts_with_avatars)
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

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
            confirm_password = request.form.get("confirm_password")
            is_valid, validation_message = validate_password(password)
            if not is_valid:
                flash(validation_message, "error")
                return render_template("register.html", message=validation_message)
            existing_user = db.get_user_by_username(username)
            if existing_user:
                flash("User already exists!", "error")
                return render_template("register.html", message="User already exists!")
            if password != confirm_password:
                flash("Password mismatched!", "error")
                return render_template("register.html", message="Password mismatched!")
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
            flash("Invalid file type. Please upload an image file.", "error")
            return redirect(url_for("index"))

    # Retrieve the user data to get the avatar path
    user = db.get_user_by_username(username)
    avatar_path = (
        url_for("static", filename=user["avatar"])
        if user and "avatar" in user
        else url_for("static", filename="images/default_avatar.png")
    )

    post_data = {
        "username": username,
        "content": post_content,
        "timestamp": time.time(),
        "likes": [],
        "video_path": video_path,
        "image_path": image_path,
        "avatar_path": avatar_path,  # Include avatar_path in post data
    }
    result = db.posts_collection.insert_one(post_data)
    post_data["_id"] = result.inserted_id

    # Serialize ObjectId to string
    post_data_serialized = json.loads(json.dumps(post_data, default=json_serializer))
    socketio.emit('new_post', post_data_serialized)
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

@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    username = get_current_user()
    if not username:
        flash("You need to be logged in to delete posts!", "error")
        return redirect(url_for("login"))

    # Delete post from database
    result = db.posts_collection.delete_one({'_id': ObjectId(post_id)})

    if result.deleted_count > 0:
        # Broadcast the post deletion to all clients
        socketio.emit('delete_post', {'post_id': str(post_id)})
        flash("Post deleted successfully!", "success")
    else:
        flash("Failed to delete post!", "error")

    return redirect(url_for("index"))

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('message', {'data': 'Connected to the WebSocket server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

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

# Avatar upload configuration
AVATAR_UPLOAD_FOLDER = "static/uploads/avatars"
if not os.path.exists(AVATAR_UPLOAD_FOLDER):
    os.makedirs(AVATAR_UPLOAD_FOLDER)

MAX_AVATAR_SIZE_MB = 2
MAX_AVATAR_SIZE_BYTES = MAX_AVATAR_SIZE_MB * 1024 * 1024

@app.route("/avatar", methods=["GET", "POST"])
def upload_avatar():
    username = get_current_user()
    if not username:
        flash("You need to be logged in to upload an avatar!", "error")
        return redirect(url_for("login"))

    user = db.get_user_by_username(username)
    avatar_path = user.get("avatar", "images/default_avatar.png")
    current_avatar = url_for('static', filename=avatar_path)

    if request.method == "POST":
        avatar_file = request.files.get("avatar")
        if avatar_file:
            # Check file extension
            allowed_extensions = {"jpg", "jpeg", "png", "gif"}
            if avatar_file.filename.split('.')[-1].lower() not in allowed_extensions:
                flash("Invalid file type. Please upload an image file (jpg, jpeg, png, gif).", "error")
                return redirect(url_for("avatar"))

            avatar_file.seek(0, os.SEEK_END)
            file_size = avatar_file.tell()
            avatar_file.seek(0)

            if file_size > MAX_AVATAR_SIZE_BYTES:
                flash(f"File size exceeds {MAX_AVATAR_SIZE_MB}MB limit.", "error")
                return redirect(url_for("avatar"))

            filename = secure_filename(f"{username}_avatar.{avatar_file.filename.split('.')[-1].lower()}")
            avatar_path = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
            avatar_file.save(avatar_path)

            relative_avatar_path = f"uploads/avatars/{filename}"
            db.update_user_avatar(username, relative_avatar_path)
            flash("Avatar uploaded successfully!", "success")
            return redirect(url_for("index"))

    return render_template("avatar.html", current_avatar=current_avatar)

# ---------------------------Test Route---------------------------
@app.route("/test")
def hello_world():
    return "<h1>Hello!</h1>"

# ---------------------------After Request---------------------------
@app.after_request
def secure_header(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# ---------------------------Run Application---------------------------
if __name__ == "__main__":
    # Use socketio.run instead of app.run for Socket.IO support
    socketio.run(app, debug=True, host="0.0.0.0", port=8080)
