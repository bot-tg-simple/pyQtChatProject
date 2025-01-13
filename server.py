from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

port = 8080
address = f'http://127.0.0.1:{port}'

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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                theme TEXT,
                font_size INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip (
                id TEXT PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                country TEXT
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


@app.route('/send_image', methods=['POST'])
def send_image():
    username = request.form.get('username', 'Anonymous')
    image = request.files['image']

    if image:
        with sqlite3.connect('chat.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, 'Image sent'))
            conn.commit()

    return jsonify(success=True)


@app.route('/messages', methods=['GET'])
def get_messages():
    with sqlite3.connect('chat.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, message FROM messages')
        messages = cursor.fetchall()

    return jsonify(messages)


@app.route('/update_ip', methods=['POST'])
def update_ip():
    username = request.form.get('username', 'Anonymous')
    ip_address = request.form.get('ip')
    country = request.form.get('country')
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
                        UPDATE ip SET ip = ?, country = ? WHERE id = ?
                        ''', (ip_address, country, username))
    except Exception:
        pass
    conn.commit()
    return jsonify(success=True)


if __name__ == '__main__':
    init_db()
    app.run(port=port, debug=True)
