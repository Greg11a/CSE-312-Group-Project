from flask import Flask, request, render_template, send_from_directory, make_response

app = Flask(__name__)


# url: http[80]/http[443]://www.something.com:443/path
# Need more adjustments. 
@app.route('/') #root route
def home():
    response = make_response(render_template('index.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/login')
def login():
    response = make_response(render_template('login.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/register')
def register():
    response = make_response(render_template('register.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('404.html'), 404)
    return response

@app.route('/static/css/<path:filename>')
def serve_css(filename):
    response = send_from_directory('static/css', filename)
    return response, 200, {'Content-Type': 'text/css; charset=utf-8'}

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    response = send_from_directory('static/js', filename)
    return response, 200, {'Content-Type': 'text/javascript; charset=utf-8'}

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    response = send_from_directory('static/images', filename)
    return response, 200, {'Content-Type': 'image/jpeg'}
# ---------------------------Test Route---------------------------
@app.route('/test') # for test purpose only, Modify this if you have any to try out
def hello_world():
    return '<h1>Hello!</h1>'
# ---------------------------After Request---------------------------
@app.after_request
def secure_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # url = request.url
    # if url.endswith('.css'):
    #     response.headers['Content-Type'] = 'text/css'
    # elif url.endswith('.js'):
    #     response.headers['Content-Type'] = 'text/javascript'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    # debug=True allow you to see modification immediately