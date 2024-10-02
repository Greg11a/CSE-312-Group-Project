# app/app.py

from flask import Flask, render_template, send_from_directory, make_response # type: ignore

app = Flask(__name__)

@app.route('/')
def home():
    response = make_response(render_template('index.html'))
    # Set security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

#login page
@app.route('/login')
def login():
    return "modify your page here"

# Serve CSS
@app.route('/css/<path:filename>')
def serve_css(filename):
    response = send_from_directory('static/css', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Serve JavaScript
@app.route('/js/<path:filename>')
def serve_js(filename):
    response = send_from_directory('static/js', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Serve Images
@app.route('/images/<path:filename>')
def serve_images(filename):
    response = send_from_directory('static/images', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)