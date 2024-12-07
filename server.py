from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('chat.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT
            )
        ''')
        conn.commit()


@app.route('/send', methods=['POST'])
def send_message():
    username = request.form.get('username', 'Anonymous')
    message = request.form.get('message')

    if message:
        with sqlite3.connect('chat.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
            conn.commit()

    return jsonify(success=True)


@app.route('/messages', methods=['GET'])
def get_messages():
    with sqlite3.connect('chat.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, message FROM messages')
        messages = cursor.fetchall()

    return jsonify(messages)


if __name__ == '__main__':
    init_db()
    app.run(port=8080, debug=True)
