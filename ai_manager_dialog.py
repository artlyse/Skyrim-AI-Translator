import subprocess
import json
import os

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QTextEdit
)


CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


class AIManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Descargar / Configurar IA Gratis")
        self.resize(620, 470)

        self.model_box = QComboBox()
        self.model_box.addItems([
    "qwen2.5:1.5b",
    "qwen2.5:3b",
    "gemma2:2b",
    "mistral"
        ])

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        btn_check = QPushButton("Verificar Ollama")
        btn_install = QPushButton("Instalar Ollama con Winget")
        btn_download = QPushButton("Descargar modelo seleccionado")
        btn_use = QPushButton("Usar este modelo")

        btn_check.clicked.connect(self.check_ollama)
        btn_install.clicked.connect(self.install_ollama)
        btn_download.clicked.connect(self.download_model)
        btn_use.clicked.connect(self.use_model)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Modelo IA gratuito:"))
        layout.addWidget(self.model_box)

        layout.addWidget(btn_check)
        layout.addWidget(btn_install)
        layout.addWidget(btn_download)
        layout.addWidget(btn_use)

        layout.addWidget(QLabel("Salida:"))
        layout.addWidget(self.log_box)

        self.setLayout(layout)

    def log(self, text):
        self.log_box.append(text)

    def run_command(self, command):
        try:
            self.log(f"> {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False
            )

            while True:
                line = process.stdout.readline()

                if not line and process.poll() is not None:
                    break

                if line:
                    try:
                        self.log(line.rstrip())
                    except Exception:
                        pass

            return process.returncode == 0

        except Exception as e:
            self.log(str(e))
            return False

    def find_ollama_exe(self):
        possible_paths = [
            "ollama",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"),
            r"C:\Program Files\Ollama\ollama.exe"
        ]

        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode == 0:
                    return path

            except Exception:
                pass

        return None

    def check_ollama(self):
        ollama_exe = self.find_ollama_exe()

        if ollama_exe:
            self.log(f"Ollama encontrado en: {ollama_exe}")

            QMessageBox.information(
                self,
                "Ollama",
                "Ollama está instalado correctamente."
            )
        else:
            QMessageBox.warning(
                self,
                "Ollama",
                "Ollama no está instalado o no está en PATH."
            )

    def install_ollama(self):
        QMessageBox.information(
            self,
            "Instalación",
            "Se intentará instalar Ollama usando winget. Puede pedir permisos."
        )

        self.run_command([
            "winget",
            "install",
            "Ollama.Ollama"
        ])

    def download_model(self):
        model = self.model_box.currentText()
        ollama_exe = self.find_ollama_exe()

        if not ollama_exe:
            QMessageBox.warning(
                self,
                "Ollama",
                "No se encontró Ollama. Instálalo primero."
            )
            return

        QMessageBox.information(
            self,
            "Descarga",
            f"Se descargará el modelo {model}. Esto puede tardar varios minutos."
        )

        self.run_command([
            ollama_exe,
            "pull",
            model
        ])

    def use_model(self):
        model = self.model_box.currentText()

        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        settings = {
            "provider": "ollama",
            "model": model,
            "api_key": "",
            "temperature": 0.2,
            "ollama_url": "http://localhost:11434/api/generate"
        }

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

        QMessageBox.information(
            self,
            "Configurado",
            f"Ahora se usará Ollama con el modelo {model}."
        )

        self.accept()