from flask import Flask, request, render_template, send_from_directory, make_response

app = Flask(__name__)


# url: http[80]/http[443]://www.something.com:443/path
# Need more adjustments. 
@app.route('/') #root route
def home():
    response = make_response(render_template('index.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.after_request
def secure_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/login')
def login():
    response = make_response(render_template('login.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('404.html'), 404)
    return response

@app.route('/static/images/<path:filename>')
def serve_images(filename):
    response = send_from_directory('static/images', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/test') # for test purpose only, Modify this if you have any to try out
def hello_world():
    return '<h1>Hello!</h1>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    # debug=True allow you to see modification immediately