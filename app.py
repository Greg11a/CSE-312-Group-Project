from flask import Flask, request, render_template

app = Flask(__name__)


# url: http[80]/http[443]://www.something.com:443/path
# Need more adjustments. 
@app.route('/') #root route
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return "Modify your login page here"

@app.route('/test') # for test purpose only, Modify this if you have any to try out
def hello_world():
    return '<h1>Hello!</h1>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # debug=True allow you to see modification immediately