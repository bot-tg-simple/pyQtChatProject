import sys
import subprocess
import requests
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer


class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('chat.ui', self)
        self.setWindowTitle("Anon.Net")

        self.sendButton.clicked.connect(self.send_message)
        self.load_messages()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(5000)

    def send_message(self):
        message = self.messageInput.text()

        if message:
            requests.post('http://127.0.0.1:8080/send', data={'username': "Anonim", 'message': message})
            self.messageInput.clear()
            self.load_messages()

    def load_messages(self):
        response = requests.get('http://127.0.0.1:8080/messages')
        print(response.json())
        messages = response.json()

        self.chatDisplay.clear()
        for username, message in messages:
            print(f"Добавление сообщения: {username}: {message}")
            self.chatDisplay.append(f"{username}: {message}")


def run_server():
    subprocess.Popen([sys.executable, 'server.py'])


if __name__ == '__main__':
    run_server()
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec())
