import json
import os

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox
)


CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


DEFAULT_SETTINGS = {
    "provider": "mock",
    "model": "mock-free",
    "api_key": "",
    "temperature": "0.2",
    "ollama_url": "http://localhost:11434/api/generate"
}


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Configuración IA")
        self.resize(420, 300)

        self.provider_box = QComboBox()
        self.provider_box.addItems([
            "mock",
            "ollama"
        ])

        self.model_box = QComboBox()

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("No necesario para Mock/Ollama")

        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("Ejemplo: 0.2")

        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434/api/generate")

        self.btn_save = QPushButton("Guardar configuración")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Proveedor IA:"))
        layout.addWidget(self.provider_box)

        layout.addWidget(QLabel("Modelo:"))
        layout.addWidget(self.model_box)

        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key_input)

        layout.addWidget(QLabel("Temperatura:"))
        layout.addWidget(self.temperature_input)

        layout.addWidget(QLabel("URL Ollama:"))
        layout.addWidget(self.ollama_url_input)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.provider_box.currentTextChanged.connect(self.update_models)
        self.btn_save.clicked.connect(self.save_settings)

        self.load_settings()

    def update_models(self):
        provider = self.provider_box.currentText()

        self.model_box.clear()

        if provider == "mock":
            self.model_box.addItems([
                "mock-free"
            ])

        elif provider == "ollama":
            self.model_box.addItems([
        "qwen2.5:1.5b",
        "qwen2.5:3b",
        "gemma2:2b",
        "mistral"
            ])

    def ensure_config_exists(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=4)

    def load_settings(self):
        self.ensure_config_exists()

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            provider = settings.get("provider", "mock")
            model = settings.get("model", "mock-free")
            api_key = settings.get("api_key", "")
            temperature = str(settings.get("temperature", "0.2"))
            ollama_url = settings.get(
                "ollama_url",
                "http://localhost:11434/api/generate"
            )

            index = self.provider_box.findText(provider)
            if index >= 0:
                self.provider_box.setCurrentIndex(index)

            self.update_models()

            model_index = self.model_box.findText(model)
            if model_index >= 0:
                self.model_box.setCurrentIndex(model_index)

            self.api_key_input.setText(api_key)
            self.temperature_input.setText(temperature)
            self.ollama_url_input.setText(ollama_url)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar la configuración:\n{e}"
            )

    def save_settings(self):
        try:
            temperature_text = self.temperature_input.text().strip()

            try:
                temperature = float(temperature_text)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Temperatura inválida",
                    "La temperatura debe ser un número. Ejemplo: 0.2"
                )
                return

            settings = {
                "provider": self.provider_box.currentText(),
                "model": self.model_box.currentText(),
                "api_key": self.api_key_input.text().strip(),
                "temperature": temperature,
                "ollama_url": self.ollama_url_input.text().strip()
            }

            self.ensure_config_exists()

            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)

            QMessageBox.information(
                self,
                "Configuración guardada",
                "La configuración IA se guardó correctamente."
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración:\n{e}"
            )