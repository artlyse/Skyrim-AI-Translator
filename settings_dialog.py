import json
import os

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QSlider,
    QTabWidget,
    QWidget
)
from PyQt6.QtCore import Qt

from languages import LANGUAGES, get_text


CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Diccionario de idiomas soportados para traducciones
TRANSLATION_LANGUAGES = {
    "Spanish": "Español",
    "English": "Inglés",
    "French": "Francés",
    "German": "Alemán",
    "Italian": "Italiano",
    "Portuguese": "Portugués",
    "Russian": "Ruso",
    "Japanese": "Japonés",
    "Chinese": "Chino",
    "Korean": "Coreano"
}

# Temas disponibles
THEMES = {
    "dark": "Oscuro",
    "light": "Claro",
    "gray": "Gris"
}

DEFAULT_SETTINGS = {
    "provider": "mock",
    "model": "mock-free",
    "api_key": "",
    "temperature": 0.2,
    "ollama_url": "http://localhost:11434/api/generate",
    "target_language": "Spanish",
    "ui_language": "Spanish",
    "theme": "dark",
    "window_opacity": 100,
    "font_size": 13,
    "auto_save": True,
    "confirm_exit": True,
    "show_tooltips": True,
    "same_text_is_translated": False
}


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Obtener idioma actual
        self.ui_language = self.get_current_ui_language()
        
        self.setWindowTitle(self.tr("settings_title"))
        self.resize(500, 650)

        # Crear tabs
        self.tab_widget = QTabWidget()
        
        # Tabs
        self.tab_ai = QWidget()
        self.tab_appearance = QWidget()
        self.tab_behavior = QWidget()
        self.tab_language = QWidget()
        
        self.tab_widget.addTab(self.tab_ai, "🤖 IA")
        self.tab_widget.addTab(self.tab_appearance, "🎨 Apariencia")
        self.tab_widget.addTab(self.tab_behavior, "⚙️ Comportamiento")
        self.tab_widget.addTab(self.tab_language, "🌐 Idioma")
        
        # Configurar cada tab
        self.setup_ai_tab()
        self.setup_appearance_tab()
        self.setup_behavior_tab()
        self.setup_language_tab()
        
        # Botones principales
        self.btn_save = QPushButton(self.tr("Guardar configuración"))
        self.btn_cancel = QPushButton(self.tr("Cancelar"))
        self.btn_reset = QPushButton(self.tr("Restaurar predeterminados"))
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Conectar eventos
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self.reset_settings)
        self.provider_box.currentTextChanged.connect(self.update_models)
        
        # Cargar configuraciones
        self.load_settings()
    
    def tr(self, key, **kwargs):
        """Traduce un texto según el idioma UI actual"""
        return get_text(key, self.ui_language, **kwargs)
    
    def get_current_ui_language(self):
        """Obtiene el idioma actual de la UI desde settings"""
        try:
            settings_path = os.path.join(CONFIG_DIR, "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    return settings.get("ui_language", "Spanish")
        except:
            pass
        return "Spanish"
    
    def setup_language_tab(self):
        """Configura la pestaña de idioma"""
        layout = QVBoxLayout()
        
        # Grupo: Idioma de interfaz
        group_ui = QGroupBox(self.tr("Idioma de la interfaz"))
        ui_layout = QVBoxLayout()
        
        self.ui_language_box = QComboBox()
        # Iterar correctamente sobre LANGUAGES
        for lang_code, lang_data in LANGUAGES.items():
            lang_name = lang_data["name"]  # Obtener el nombre del idioma
            self.ui_language_box.addItem(lang_name, lang_code)
        
        ui_layout.addWidget(QLabel(self.tr("Selecciona el idioma de la interfaz:")))
        ui_layout.addWidget(self.ui_language_box)
        ui_layout.addWidget(QLabel("⚠️ " + self.tr("Los cambios de interfaz se aplican al guardar la configuración")))
        
        group_ui.setLayout(ui_layout)
        layout.addWidget(group_ui)
        
        # Grupo: Idioma de traducción
        group_translation = QGroupBox(self.tr("Idioma de traducción"))
        trans_layout = QVBoxLayout()
        
        self.translation_language_box = QComboBox()
        # Usar TRANSLATION_LANGUAGES que ya está definido en el archivo
        for code, name in TRANSLATION_LANGUAGES.items():
            self.translation_language_box.addItem(name, code)
        
        trans_layout.addWidget(QLabel(self.tr("Idioma destino para las traducciones:")))
        trans_layout.addWidget(self.translation_language_box)
        
        group_translation.setLayout(trans_layout)
        layout.addWidget(group_translation)
        
        layout.addStretch()
        self.tab_language.setLayout(layout)
    
    def setup_ai_tab(self):
        layout = QVBoxLayout()
        
        # Grupo: Proveedor y Modelo
        group_provider = QGroupBox(self.tr("Proveedor de IA"))
        provider_layout = QVBoxLayout()
        
        self.provider_box = QComboBox()
        self.provider_box.addItems(["mock", "ollama"])
        
        self.model_box = QComboBox()
        
        provider_layout.addWidget(QLabel(self.tr("Proveedor:")))
        provider_layout.addWidget(self.provider_box)
        provider_layout.addWidget(QLabel(self.tr("Modelo:")))
        provider_layout.addWidget(self.model_box)
        
        group_provider.setLayout(provider_layout)
        layout.addWidget(group_provider)
        
        # Grupo: Configuración avanzada
        group_advanced = QGroupBox(self.tr("Configuración avanzada"))
        advanced_layout = QVBoxLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("No necesario para Mock/Ollama")
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("Ejemplo: 0.2")
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434/api/generate")
        
        advanced_layout.addWidget(QLabel(self.tr("API Key:")))
        advanced_layout.addWidget(self.api_key_input)
        advanced_layout.addWidget(QLabel(self.tr("Temperatura (0.0 - 1.0):")))
        advanced_layout.addWidget(self.temperature_input)
        advanced_layout.addWidget(QLabel(self.tr("URL Ollama:")))
        advanced_layout.addWidget(self.ollama_url_input)
        
        group_advanced.setLayout(advanced_layout)
        layout.addWidget(group_advanced)
        
        layout.addStretch()
        self.tab_ai.setLayout(layout)
    
    def setup_appearance_tab(self):
        layout = QVBoxLayout()
        
        # Grupo: Tema
        group_theme = QGroupBox(self.tr("Tema"))
        theme_layout = QVBoxLayout()
        
        self.theme_box = QComboBox()
        for code, name in THEMES.items():
            self.theme_box.addItem(name, code)
        
        theme_layout.addWidget(QLabel(self.tr("Tema:")))
        theme_layout.addWidget(self.theme_box)
        
        group_theme.setLayout(theme_layout)
        layout.addWidget(group_theme)
        
        # Grupo: Transparencia
        group_opacity = QGroupBox(self.tr("Transparencia de ventana"))
        opacity_layout = QVBoxLayout()
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout.addWidget(QLabel(self.tr("Opacidad:")))
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        group_opacity.setLayout(opacity_layout)
        layout.addWidget(group_opacity)
        
        # Grupo: Tamaño de fuente
        group_font = QGroupBox(self.tr("Tamaño de fuente"))
        font_layout = QVBoxLayout()
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 20)
        self.font_slider.setValue(13)
        self.font_slider.setTickInterval(1)
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.font_label = QLabel("13px")
        self.font_slider.valueChanged.connect(
            lambda v: self.font_label.setText(f"{v}px")
        )
        
        font_layout.addWidget(QLabel(self.tr("Tamaño:")))
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_label)
        
        group_font.setLayout(font_layout)
        layout.addWidget(group_font)
        
        layout.addStretch()
        self.tab_appearance.setLayout(layout)
    
    def setup_behavior_tab(self):
        layout = QVBoxLayout()
        
        # Grupo: Comportamiento
        group_behavior = QGroupBox(self.tr("Opciones de comportamiento"))
        behavior_layout = QVBoxLayout()
        
        self.auto_save_check = QCheckBox(self.tr("Guardar automáticamente al cerrar"))
        self.confirm_exit_check = QCheckBox(self.tr("Confirmar al salir"))
        self.show_tooltips_check = QCheckBox(self.tr("Mostrar tooltips informativos"))
        
        behavior_layout.addWidget(self.auto_save_check)
        behavior_layout.addWidget(self.confirm_exit_check)
        behavior_layout.addWidget(self.show_tooltips_check)
        
        group_behavior.setLayout(behavior_layout)
        layout.addWidget(group_behavior)
        
        layout.addStretch()
        self.tab_behavior.setLayout(layout)
    
    def update_models(self):
        provider = self.provider_box.currentText()
        self.model_box.clear()
        
        if provider == "mock":
            self.model_box.addItems(["mock-free"])
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
            
            # AI Tab
            provider = settings.get("provider", "mock")
            model = settings.get("model", "mock-free")
            api_key = settings.get("api_key", "")
            temperature = str(settings.get("temperature", 0.2))
            ollama_url = settings.get(
                "ollama_url",
                "http://localhost:11434/api/generate"
            )
            
            # Idiomas
            ui_language = settings.get("ui_language", "Spanish")
            target_language = settings.get("target_language", "Spanish")
            
            # Apariencia
            theme = settings.get("theme", "dark")
            opacity = settings.get("window_opacity", 100)
            font_size = settings.get("font_size", 13)
            
            # Comportamiento
            auto_save = settings.get("auto_save", True)
            confirm_exit = settings.get("confirm_exit", True)
            show_tooltips = settings.get("show_tooltips", True)
            
            # Asignar valores - AI
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
            
            # Idiomas
            ui_index = self.ui_language_box.findData(ui_language)
            if ui_index >= 0:
                self.ui_language_box.setCurrentIndex(ui_index)
            
            trans_index = self.translation_language_box.findData(target_language)
            if trans_index >= 0:
                self.translation_language_box.setCurrentIndex(trans_index)
            
            # Tema
            theme_index = self.theme_box.findData(theme)
            if theme_index >= 0:
                self.theme_box.setCurrentIndex(theme_index)
            
            # Opacidad
            self.opacity_slider.setValue(opacity)
            self.opacity_label.setText(f"{opacity}%")
            
            # Fuente
            self.font_slider.setValue(font_size)
            self.font_label.setText(f"{font_size}px")
            
            # Comportamiento
            self.auto_save_check.setChecked(auto_save)
            self.confirm_exit_check.setChecked(confirm_exit)
            self.show_tooltips_check.setChecked(show_tooltips)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"No se pudo cargar la configuración:\n{e}"
            )
    
    def save_settings(self):
        try:
            temperature_text = self.temperature_input.text().strip()
            
            try:
                temperature = float(temperature_text)
                if temperature < 0 or temperature > 1:
                    raise ValueError("La temperatura debe estar entre 0 y 1")
            except ValueError:
                QMessageBox.warning(
                    self,
                    self.tr("Temperatura inválida"),
                    "La temperatura debe ser un número entre 0.0 y 1.0.\nEjemplo: 0.2"
                )
                return
            
            new_ui_language = self.ui_language_box.currentData()
            
            settings = {
                "provider": self.provider_box.currentText(),
                "model": self.model_box.currentText(),
                "api_key": self.api_key_input.text().strip(),
                "temperature": temperature,
                "ollama_url": self.ollama_url_input.text().strip(),
                "target_language": self.translation_language_box.currentData(),
                "ui_language": new_ui_language,
                "theme": self.theme_box.currentData(),
                "window_opacity": self.opacity_slider.value(),
                "font_size": self.font_slider.value(),
                "auto_save": self.auto_save_check.isChecked(),
                "confirm_exit": self.confirm_exit_check.isChecked(),
                "show_tooltips": self.show_tooltips_check.isChecked()
            }
            
            self.ensure_config_exists()
            
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            # Verificar si cambió el idioma
            if new_ui_language != self.ui_language:
                lang_name = LANGUAGES.get(new_ui_language, {}).get("name", new_ui_language)
                QMessageBox.information(
                    self,
                    self.tr("Idioma cambiado"),
                    self.tr("msg_language_changed").format(lang_name)
                )
                # Actualizar el idioma actual
                self.ui_language = new_ui_language
                # Actualizar textos de la interfaz (se aplicará al cerrar)
                self.setWindowTitle(self.tr("settings_title"))
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"No se pudo guardar la configuración:\n{e}"
            )
    
    def reset_settings(self):
        confirm = QMessageBox.question(
            self,
            self.tr("Restaurar predeterminados"),
            "¿Estás seguro de que quieres restaurar todos los valores predeterminados?"
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Resetear campos
        self.provider_box.setCurrentText("mock")
        self.update_models()
        self.model_box.setCurrentText("mock-free")
        self.api_key_input.clear()
        self.temperature_input.setText("0.2")
        self.ollama_url_input.setText("http://localhost:11434/api/generate")
        
        ui_index = self.ui_language_box.findData("Spanish")
        if ui_index >= 0:
            self.ui_language_box.setCurrentIndex(ui_index)
        
        trans_index = self.translation_language_box.findData("Spanish")
        if trans_index >= 0:
            self.translation_language_box.setCurrentIndex(trans_index)
        
        theme_index = self.theme_box.findData("dark")
        if theme_index >= 0:
            self.theme_box.setCurrentIndex(theme_index)
        
        self.opacity_slider.setValue(100)
        self.opacity_label.setText("100%")
        self.font_slider.setValue(13)
        self.font_label.setText("13px")
        
        self.auto_save_check.setChecked(True)
        self.confirm_exit_check.setChecked(True)
        self.show_tooltips_check.setChecked(True)