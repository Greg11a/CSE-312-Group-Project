from flask import Flask, request, render_template, send_from_directory, make_response, jsonify
from db import get_collection

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
    return "Modify your login page here"

@app.route('/chat')
def chat():
    return "Chat Page"

@app.route('/images/<path:filename>')
def serve_images(filename):
    response = send_from_directory('static/images', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/test') # for test purpose only, Modify this if you have any to try out
def hello_world():
    return '<h1>Hello!</h1>'

# add test data to MongoDB
@app.route('/add_test_data', methods=['GET'])
def add_test_data():
    # test data
    test_data = {"name": "Test User", "email": "testuser@example.com"}

    # use get_collection to get the collection
    collection = get_collection('test_collection')

    # insert data into MongoDB
    collection.insert_one(test_data)

    return "Test data added successfully!"

# get test data from MongoDB
@app.route('/get_test_data', methods=['GET'])
def get_test_data():
    collection = get_collection('test_collection')

    # get all data from the collection
    data = collection.find()
    
    # convert data to list for JSON serialization
    data_list = []
    for item in data:
        # convert ObjectId to string
        item['_id'] = str(item['_id'])
        data_list.append(item)

    return jsonify(data_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    # debug=True allow you to see modification immediately