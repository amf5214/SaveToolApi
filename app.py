from flask import Flask, g, request, jsonify
import sqlite3
import random
import string

DATABASE = 'store.db'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    cur = get_db().execute(query, args)
    cur.connection.commit()

def generate_random_string(length):
  """Generates a random string of letters and digits."""

  characters = string.ascii_letters + string.digits
  return ''.join(random.choice(characters) for i in range(length))

@app.route("/")
def home():
    return "Welcome"

@app.route("/save", methods=["POST"])
def save_information():
    """Path to save information using url:port/save with json of {information: <information to store>}"""

    data = request.get_json()

    save_text = data.get("information")
    short_url = generate_random_string(15)

    insert_db("insert into information (short_url, data) values (?, ?);", [short_url, save_text])

    print(save_text, short_url)

    return (str("Saved = " + short_url), 200)


@app.route("/retrieve/<url>", methods=["GET"])
def retrieve(url):
    """Path to retrieve the stored information using url:port/retrieve/<short_url>"""

    output = query_db('select data from information where short_url = ?', [url], one=True)
    print(output[0])
    return (output[0], 200)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run()