import sys
import subprocess
import requests
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QDialog,
                             QComboBox, QLabel, QSpinBox, QPushButton)
from PyQt6.QtCore import QTimer
from server import address
from ip import ipaddress


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 400, 300)

        self.theme_label = QLabel("Тема:", self)
        self.theme_label.move(10, 10)
        self.theme_label.setStyleSheet("color: white;")

        self.theme_combo = QComboBox(self)
        self.theme_combo.move(10, 30)
        self.theme_combo.addItems(["Светлая", "Темная", "Системная"])
        self.theme_combo.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.theme_combo.setFixedWidth(150)

        self.font_size_label = QLabel("Размер шрифта:", self)
        self.font_size_label.move(10, 60)
        self.font_size_label.setStyleSheet("color: white;")

        self.font_size_spin = QSpinBox(self)
        self.font_size_spin.move(10, 80)
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.font_size_spin.setFixedWidth(150)

        self.language_label = QLabel("Язык:", self)
        self.language_label.move(220, 10)
        self.language_label.setStyleSheet("color: white;")

        self.language_combo = QComboBox(self)
        self.language_combo.move(220, 30)
        self.language_combo.addItems(["Russian", "English", "Spanish"])
        self.language_combo.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.language_combo.setFixedWidth(150)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.move(10, 120)
        self.save_button.setStyleSheet("background-color: black; color: white; border: 1px solid white;")
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self.save_settings)

    def save_settings(self):
        theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()
        language = self.language_combo.currentText()
        print(f"Тема: {theme}, Размер шрифта: {font_size}, Язык: {language}")


class ChatClient(QMainWindow):
    def __init__(self):
        
        super().__init__()
        uic.loadUi('chat.ui', self)
        self.setWindowTitle("Anon.Net")

        self.sendButton.clicked.connect(self.send_message)
        self.settings_button = QPushButton("Настройки", self)
        self.settings_button.move(300, 10)
        self.settings_button.setStyleSheet(
            "background-color: black; color: white; border: 1px solid white; border-radius: 10px; padding: 5px; font-size: 12px;")
        self.settings_button.clicked.connect(self.open_settings)

        self.export_button = QPushButton("Экспорт", self)
        self.export_button.move(420, 10)
        self.export_button.setStyleSheet(
            "background-color: black; color: white; border: 1px solid white; border-radius: 10px; padding: 5px; font-size: 12px;")
        self.export_button.clicked.connect(self.export_chat)
        self.send_image_button.clicked.connect(self.send_image)
        self.id_send_button.clicked.connect(self.add_id_to_message_input)
        self.country_combo.currentIndexChanged.connect(self.update_server_ip)
        self.update_server_ip()

        self.load_messages()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(5000)

    def open_settings(self):
        settings_dialog = SettingsDialog()
        settings_dialog.exec()

    def update_server_ip(self):
        country = self.country_combo.currentText()
        print(country)
        ip_address = self.get_ip_address(country)
        
        self.send_ip_to_server(ip_address, country)

    def get_ip_address(self, country):
        return ipaddress.get(country, '1.1.1.1') # по умолчанию

    def send_ip_to_server(self, ip_address, country):
        username = "Anonim"  
        requests.post(f'{address}/update_ip', data={
            'username': username,
            'ip': ip_address,
            'country': country
        })

    def add_id_to_message_input(self):
        id_text = self.label_6.text()
        current_text = self.messageInput.text()
        self.messageInput.setText(f"{current_text} {id_text}")

    def send_message(self):
        message = self.messageInput.text()
        if message:
            requests.post(f'{address}/send', data={'username': "Anonim", 'message': message})
            self.messageInput.clear()
            self.load_messages()

    def export_chat_to_file(self, file_path):
        response = requests.get(f'{address}/messages')
        messages = response.json()

        with open(file_path, 'w') as file:
            for username, message in messages:
                file.write(f"{username}: {message}\n")

    def export_chat(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить чат", "", "Текстовый файл (*.txt);;CSV файл (*.csv)")
        if file_path:
            self.export_chat_to_file(file_path)

    def send_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Картинки (*.png *.jpg *.jpeg)")
        if file_path:
            with open(file_path, 'rb') as image_file:
                requests.post(f'{address}/send_image', files={'image': image_file}, data={'username': "Anonim"})

    def load_messages(self):
        response = requests.get(f'{address}/messages')
        print(response.json())
        messages = response.json()

        self.chatDisplayn.clear()
        for username, message in messages:
            if message.startswith("http://") or message.startswith("https://"):
                self.chatDisplayn.append(f"<font color='white'>{username}: </font><img src='{message}' width='200' height='200'>")
            else:
                print(f"Добавление сообщения: {username}: {message}")
                self.chatDisplayn.append(f"<font color='white'>{username}: </font><font color='blue'>{message}</font>")
                

def run_server():
    subprocess.Popen([sys.executable, 'server.py'])


if __name__ == '__main__':
    run_server()
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec())
