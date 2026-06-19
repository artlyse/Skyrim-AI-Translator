import subprocess
import json
import os
import threading
import time
import re
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QWidget,
    QLineEdit
)
from PyQt6.QtCore import QObject, pyqtSignal, Qt


CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# ============================================================================
# MODELOS DE OLLAMA ORGANIZADOS POR CATEGORÍA
# ============================================================================

OLLAMA_MODELS = {
    "🏆 Modelos Recomendados": [
        ("qwen3:4b", "Qwen3 moderno, muy buen equilibrio calidad/velocidad (4B)", 4),
        ("qwen3:8b", "Qwen3 potente para uso general, traducción y razonamiento (8B)", 8),
        ("qwen3:14b", "Qwen3 con mayor calidad, requiere más RAM (14B)", 14),
        ("qwen2.5:1.5b", "Ligero, rápido, bueno para traducciones (1.5B)", 1.5),
        ("qwen2.5:3b", "Equilibrio calidad/velocidad (3B)", 3),
        ("qwen2.5:7b", "Mayor calidad, más recursos (7B)", 7),
        ("qwen2.5:14b", "Alta calidad (14B)", 14),
        ("gemma3:1b", "Google, ultraligero y moderno (1B)", 1),
        ("gemma3:4b", "Google, recomendado para equipos medios (4B)", 4),
        ("gemma3:12b", "Google, más calidad para texto y multilingüe (12B)", 12),
        ("gemma2:2b", "Google, ligero y eficiente (2B)", 2),
        ("gemma2:9b", "Google, buena calidad (9B)", 9),
        ("mistral", "Muy popular, excelente para traducciones (7B)", 7),
        ("llama3.2:3b", "Meta, moderno y eficiente (3B)", 3),
        ("llama3.2:1b", "Meta, ultraligero (1B)", 1),
        ("llama3.1:8b", "Meta, excelente calidad general (8B)", 8),
        ("phi4-mini", "Microsoft, compacto y moderno", 3.8),
        ("phi4", "Microsoft, buena calidad general y razonamiento", 14),
    ],
    "⚡ Modelos Ligeros": [
        ("qwen3:0.6b", "Qwen3 muy pequeño para pruebas rápidas", 0.6),
        ("qwen3:1.7b", "Qwen3 pequeño, rápido y mejor que modelos tiny", 1.7),
        ("gemma3:1b", "Google, muy ligero", 1),
        ("gemma3:4b", "Google, ligero y útil para español", 4),
        ("llama3.2:1b", "Meta, ultraligero (1B)", 1),
        ("llama3.2:3b", "Meta, eficiente (3B)", 3),
        ("phi3.5:3.8b", "Microsoft, muy rápido y eficiente", 3.8),
        ("phi3:3.8b", "Microsoft, versión anterior", 3.8),
        ("phi3.5:mini", "Mini versión de Phi 3.5", 3.8),
        ("phi4-mini", "Microsoft, mini moderno", 3.8),
        ("tinyllama:1.1b", "Extremadamente ligero (1.1B)", 1.1),
        ("stablelm2:1.6b", "Stability AI, compacto", 1.6),
        ("deepseek-coder:1.3b", "Especializado en código", 1.3),
        ("granite3-moe:1b", "IBM, modelo eficiente", 1),
        ("granite3.2:2b", "IBM, pequeño y útil para tareas generales", 2),
        ("smollm2:135m", "Muy pequeño para pruebas básicas", 0.1),
        ("smollm2:360m", "Muy ligero para PCs con pocos recursos", 0.3),
        ("smollm2:1.7b", "Pequeño y rápido", 1.7),
    ],
    "🎯 Modelos Multilingüe": [
        ("qwen3:4b", "Qwen3, muy buen soporte multilingüe", 4),
        ("qwen3:8b", "Qwen3, excelente para español e inglés", 8),
        ("qwen3:14b", "Qwen3, más calidad multilingüe", 14),
        ("qwen2.5:7b", "Alibaba, muy buen multilingüe", 7),
        ("qwen2.5:14b", "Alibaba, alta calidad multilingüe", 14),
        ("qwen2.5:32b", "Alibaba, multilingüe avanzado", 32),
        ("gemma3:4b", "Google, buen soporte multilingüe", 4),
        ("gemma3:12b", "Google, excelente multilingüe", 12),
        ("gemma3:27b", "Google, alta calidad multilingüe", 27),
        ("gemma2:2b", "Google, buen soporte multilingüe", 2),
        ("gemma2:9b", "Google, excelente multilingüe", 9),
        ("mistral", "Excelente para múltiples idiomas", 7),
        ("mistral-nemo", "Mistral/NVIDIA, buen multilingüe y contexto amplio", 12),
        ("aya", "Cohere, orientado a idiomas múltiples", 8),
        ("aya-expanse:8b", "Cohere, multilingüe moderno", 8),
        ("aya-expanse:32b", "Cohere, multilingüe avanzado", 32),
    ],
    "🔤 Modelos Especializados": [
        ("deepseek-r1:1.5b", "DeepSeek, razonamiento ligero", 1.5),
        ("deepseek-r1:7b", "DeepSeek, razonamiento", 7),
        ("deepseek-r1:8b", "DeepSeek, razonamiento moderno", 8),
        ("deepseek-r1:14b", "DeepSeek, razonamiento", 14),
        ("deepseek-r1:32b", "DeepSeek, razonamiento avanzado", 32),
        ("qwq", "Alibaba, razonamiento avanzado", 32),
        ("cogito:3b", "Deep Cogito, razonamiento ligero", 3),
        ("cogito:8b", "Deep Cogito, razonamiento equilibrado", 8),
        ("cogito:14b", "Deep Cogito, razonamiento de mayor calidad", 14),
        ("dolphin3", "Modelo instruct flexible para uso general", 8),
        ("orca-mini", "Modelo instruct ligero", 3),
    ],
    "💻 Modelos para Código": [
        ("qwen2.5-coder:0.5b", "Código, ultraligero", 0.5),
        ("qwen2.5-coder:1.5b", "Código, ligero", 1.5),
        ("qwen2.5-coder:3b", "Código, rápido y útil", 3),
        ("qwen2.5-coder:7b", "Código, buen equilibrio", 7),
        ("qwen2.5-coder:14b", "Código, alta calidad", 14),
        ("qwen2.5-coder:32b", "Código, calidad avanzada", 32),
        ("codellama:7b", "Especializado en código", 7),
        ("codellama:13b", "Especializado en código", 13),
        ("codellama:34b", "Especializado en código", 34),
        ("deepseek-coder:1.3b", "Código, ligero", 1.3),
        ("deepseek-coder:6.7b", "Código, equilibrado", 6.7),
        ("deepseek-coder:33b", "Código, avanzado", 33),
        ("starcoder2:3b", "Especializado en código", 3),
        ("starcoder2:7b", "Especializado en código", 7),
        ("starcoder2:15b", "Especializado en código", 15),
        ("codegemma:2b", "Google, código ligero", 2),
        ("codegemma:7b", "Google, código", 7),
        ("wizardcoder:7b", "Especializado en código", 7),
        ("wizardcoder:13b", "Especializado en código", 13),
        ("wizardcoder:34b", "Especializado en código avanzado", 34),
    ],
    "🧠 Modelos Grandes": [
        ("llama3.1:8b", "Meta, excelente calidad", 8),
        ("llama3.1:70b", "Meta, calidad superior (requiere mucha RAM)", 70),
        ("llama3.3:70b", "Meta, modelo grande moderno", 70),
        ("mixtral:8x7b", "Mistral, mezcla de expertos", 46),
        ("mixtral:8x22b", "Mistral, mezcla de expertos (22B)", 140),
        ("mistral-large", "Mistral, modelo grande", 123),
        ("qwen2.5:32b", "Alibaba, alta calidad", 32),
        ("qwen2.5:72b", "Alibaba, calidad superior", 72),
        ("qwen3:30b", "Alibaba, MoE potente", 30),
        ("qwen3:32b", "Alibaba, calidad avanzada", 32),
        ("qwen3:235b", "Alibaba, muy grande; requiere muchos recursos", 235),
        ("gemma3:27b", "Google, alta calidad", 27),
        ("deepseek-r1:70b", "DeepSeek, alta calidad", 70),
        ("deepseek-r1:671b", "DeepSeek, extremadamente grande", 671),
    ],
    "👁️ Modelos con Visión / Multimodales": [
        ("llava", "Modelo visión + lenguaje", 7),
        ("llava:13b", "Visión + lenguaje con más calidad", 13),
        ("llava:34b", "Visión + lenguaje avanzado", 34),
        ("llava-llama3", "LLaVA basado en Llama 3", 8),
        ("bakllava", "Modelo multimodal tipo LLaVA", 7),
        ("moondream", "Visión ligero para imágenes", 1.8),
        ("minicpm-v", "Modelo visión-lenguaje compacto", 8),
        ("llama3.2-vision", "Meta, visión + texto", 11),
        ("llama3.2-vision:90b", "Meta, visión grande; requiere mucha RAM", 90),
    ],
    "📚 Embeddings": [
        ("nomic-embed-text", "Embeddings de texto", 0.5),
        ("snowflake-arctic-embed", "Embeddings de Snowflake", 0.3),
        ("snowflake-arctic-embed:33m", "Embeddings ligeros", 0.1),
        ("mxbai-embed-large", "Embeddings grandes", 0.5),
        ("all-minilm:33m", "MiniLM embeddings", 0.1),
        ("all-minilm:22m", "MiniLM embeddings ligeros", 0.1),
        ("bge-large", "Embeddings BGE grandes", 0.5),
        ("bge-m3", "Embeddings multilingües y búsqueda semántica", 0.6),
        ("paraphrase-multilingual", "Embeddings para textos multilingües", 0.5),
    ],
    "🧪 Experimentales / Otros": [
        ("command-r", "Cohere, bueno para RAG y tareas largas", 35),
        ("command-r-plus", "Cohere, versión grande", 104),
        ("nemotron-mini", "NVIDIA, instruct compacto", 4),
        ("hermes3", "Nous Research, instruct general", 8),
        ("openhermes", "Modelo instruct general", 7),
        ("solar", "Modelo general de alta calidad", 10.7),
        ("yi:6b", "01.AI, general ligero", 6),
        ("yi:9b", "01.AI, general", 9),
        ("yi:34b", "01.AI, general avanzado", 34),
        ("falcon3:1b", "Falcon 3 ligero", 1),
        ("falcon3:3b", "Falcon 3 eficiente", 3),
        ("falcon3:7b", "Falcon 3 equilibrado", 7),
        ("falcon3:10b", "Falcon 3 más calidad", 10),
    ]
}


# ============================================================================
# WORKER PARA DESCARGAR MODELOS
# ============================================================================

class DownloadWorker(QObject, threading.Thread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, model_name):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.model_name = model_name
        self._is_cancelled = False
        self.process = None

    def find_ollama(self):
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
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except Exception:
                pass
        return None

    def run(self):
        try:
            ollama_exe = self.find_ollama()
            if not ollama_exe:
                self.error.emit("❌ Ollama no está instalado")
                self.finished.emit(False, "Ollama no está instalado")
                return

            self.log.emit(f"> {ollama_exe} pull {self.model_name}")
            self.log.emit("=" * 50)

            self.process = subprocess.Popen(
                [ollama_exe, "pull", self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                shell=False
            )

            progress = 0

            for line in self.process.stdout:
                if self._is_cancelled:
                    self.process.terminate()
                    break

                line = line.strip()
                if line:
                    self.log.emit(line)

                    # Detectar progreso
                    match = re.search(r'(\d+)%', line)
                    if match:
                        progress = int(match.group(1))
                        self.progress.emit(progress, 100)
                    elif "verifying" in line.lower():
                        self.progress.emit(98, 100)
                    elif "success" in line.lower() or "already exists" in line.lower():
                        self.progress.emit(100, 100)

            self.process.wait()
            success = self.process.returncode == 0 and not self._is_cancelled

            if self._is_cancelled:
                self.log.emit("\n⛔ Descarga cancelada")
                self.finished.emit(False, "Cancelada")
            elif success:
                self.log.emit("\n✅ Descarga completada")
                self.progress.emit(100, 100)
                self.finished.emit(True, "Completada")
            else:
                self.log.emit("\n❌ Error en la descarga")
                self.finished.emit(False, "Error en la descarga")

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, str(e))

    def cancel(self):
        self._is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except:
                pass


# ============================================================================
# WORKER PARA LISTAR MODELOS INSTALADOS
# ============================================================================

class ListModelsWorker(QObject, threading.Thread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        threading.Thread.__init__(self)

    def find_ollama(self):
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
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except Exception:
                pass
        return None

    def run(self):
        try:
            ollama_exe = self.find_ollama()
            if not ollama_exe:
                self.finished.emit([])
                return

            result = subprocess.run(
                [ollama_exe, "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )

            models = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('NAME'):
                    parts = line.split()
                    if parts:
                        models.append({
                            'name': parts[0],
                            'size': parts[1] if len(parts) > 1 else '?',
                            'modified': ' '.join(parts[2:]) if len(parts) > 2 else ''
                        })

            self.finished.emit(models)

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit([])


# ============================================================================
# WORKER PARA DESINSTALAR
# ============================================================================

class UninstallWorker(QObject, threading.Thread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, model_name):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.model_name = model_name

    def find_ollama(self):
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
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except Exception:
                pass
        return None

    def run(self):
        try:
            ollama_exe = self.find_ollama()
            if not ollama_exe:
                self.error.emit("Ollama no está instalado")
                self.finished.emit(False, "Ollama no está instalado")
                return

            self.log.emit(f"🗑️ Desinstalando: {self.model_name}")

            result = subprocess.run(
                [ollama_exe, "rm", self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                self.log.emit(f"✅ Modelo {self.model_name} desinstalado")
                self.finished.emit(True, "Desinstalado")
            else:
                error = result.stderr if result.stderr else "Error desconocido"
                self.log.emit(f"❌ Error: {error}")
                self.finished.emit(False, error)

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False, str(e))


# ============================================================================
# DIÁLOGO PRINCIPAL
# ============================================================================

class AIManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Descargar / Configurar IA Gratis")
        self.resize(950, 750)

        self.installed_models = []
        self.current_model = None
        self.download_worker = None
        self.list_worker = None
        self.uninstall_worker = None
        self.is_downloading = False
        self.ollama_exe = None

        # Configurar UI
        self.setup_ui()
        self.apply_theme()

        # Cargar estado inicial
        self.find_ollama()
        self.refresh_model_list()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()

        # ===== BARRA DE ESTADO =====
        status_layout = QHBoxLayout()
        self.status_label = QLabel("🔍 Buscando Ollama...")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        btn_refresh = QPushButton("🔄 Refrescar")
        btn_refresh.clicked.connect(self.refresh_all)
        status_layout.addWidget(btn_refresh)

        btn_install_ollama = QPushButton("📦 Instalar Ollama")
        btn_install_ollama.clicked.connect(self.install_ollama)
        status_layout.addWidget(btn_install_ollama)

        layout.addLayout(status_layout)

        # ===== SPLITTER PRINCIPAL =====
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === PANEL IZQUIERDO ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        left_layout.addWidget(QLabel("📋 Modelos disponibles:"))

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Buscar modelo...")
        self.search_box.textChanged.connect(self.filter_models)
        left_layout.addWidget(self.search_box)

        self.model_list = QListWidget()
        self.model_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2d2d30;
            }
        """)
        self.model_list.itemSelectionChanged.connect(self.on_model_selected)
        left_layout.addWidget(self.model_list)

        # Contador de modelos
        self.model_count_label = QLabel("Mostrando 0 modelos")
        left_layout.addWidget(self.model_count_label)

        # === PANEL DERECHO ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # Información del modelo
        info_group = QGroupBox("📄 Información del modelo")
        info_layout = QVBoxLayout()

        self.model_name_label = QLabel("Selecciona un modelo")
        self.model_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.model_category_label = QLabel("")
        self.model_desc_label = QLabel("")
        self.model_desc_label.setWordWrap(True)
        self.model_size_label = QLabel("")
        self.model_status_label = QLabel("")
        self.model_status_label.setStyleSheet("font-weight: bold;")

        info_layout.addWidget(self.model_name_label)
        info_layout.addWidget(self.model_category_label)
        info_layout.addWidget(self.model_desc_label)
        info_layout.addWidget(self.model_size_label)
        info_layout.addWidget(self.model_status_label)
        info_layout.addStretch()

        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # Acciones
        action_group = QGroupBox("⚙️ Acciones")
        action_layout = QVBoxLayout()

        btn_download = QPushButton("⬇️ Descargar modelo")
        btn_download.setStyleSheet("font-weight: bold; background-color: #094771;")
        btn_download.clicked.connect(self.download_model)
        action_layout.addWidget(btn_download)

        btn_uninstall = QPushButton("🗑️ Desinstalar modelo")
        btn_uninstall.setStyleSheet("color: #ff6b6b;")
        btn_uninstall.clicked.connect(self.uninstall_model)
        action_layout.addWidget(btn_uninstall)

        btn_use = QPushButton("✅ Usar este modelo")
        btn_use.setStyleSheet("font-weight: bold;")
        btn_use.clicked.connect(self.use_model)
        action_layout.addWidget(btn_use)

        action_layout.addStretch()
        action_group.setLayout(action_layout)
        right_layout.addWidget(action_group)

        # Barra de progreso
        progress_group = QGroupBox("📊 Progreso")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                text-align: center;
                color: white;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #094771;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        self.btn_cancel = QPushButton("⛔ Cancelar")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self.cancel_download)
        progress_layout.addWidget(self.btn_cancel)

        progress_group.setLayout(progress_layout)
        right_layout.addWidget(progress_group)

        # Consola
        log_group = QGroupBox("📝 Consola")
        log_layout = QVBoxLayout()

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFontFamily("Consolas")
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                font-size: 12px;
                color: #e6e6e6;
                min-height: 120px;
                max-height: 200px;
            }
        """)
        log_layout.addWidget(self.log_box)

        log_buttons = QHBoxLayout()
        log_buttons.addStretch()

        btn_clear_log = QPushButton("🧹 Limpiar")
        btn_clear_log.clicked.connect(lambda: self.log_box.clear())
        log_buttons.addWidget(btn_clear_log)

        btn_export_log = QPushButton("💾 Exportar log")
        btn_export_log.clicked.connect(self.export_log)
        log_buttons.addWidget(btn_export_log)

        log_layout.addLayout(log_buttons)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 550])

        layout.addWidget(splitter)
        self.setLayout(layout)

        # Cargar modelos disponibles
        self.load_available_models()

    def apply_theme(self):
        """Aplica el tema oscuro"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e6e6e6;
            }
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2d2d30;
                color: white;
                border: 1px solid #3e3e42;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3e3e42;
            }
            QPushButton:disabled {
                background-color: #1e1e1e;
                color: #666;
            }
            QLineEdit {
                background-color: #252526;
                color: white;
                border: 1px solid #3e3e42;
                padding: 7px;
                border-radius: 5px;
            }
            QLabel {
                color: #e6e6e6;
            }
            QSplitter::handle {
                background-color: #3e3e42;
            }
            QScrollBar:vertical {
                background-color: #252526;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3e3e42;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4e4e52;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    # ========================================================================
    # MÉTODOS PRINCIPALES
    # ========================================================================

    def find_ollama(self):
        """Busca el ejecutable de Ollama"""
        self.ollama_exe = None
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
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.ollama_exe = path
                    self.status_label.setText(f"✅ Ollama: {os.path.basename(path)}")
                    self.status_label.setStyleSheet("color: #4CAF50;")
                    return True
            except Exception:
                pass

        self.status_label.setText("❌ Ollama no instalado")
        self.status_label.setStyleSheet("color: #ff6b6b;")
        return False

    def load_available_models(self):
        """Carga la lista de modelos disponibles"""
        self.model_list.clear()
        self.model_items = []

        for category, models in OLLAMA_MODELS.items():
            # Separador de categoría
            item = QListWidgetItem(f"─── {category} ───")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            item.setBackground(Qt.GlobalColor.darkGray)
            item.setForeground(Qt.GlobalColor.lightGray)
            self.model_list.addItem(item)

            for model, description, size in models:
                item = QListWidgetItem(f"  {model}")
                item.setData(Qt.ItemDataRole.UserRole, (model, category, description, size))
                self.model_list.addItem(item)
                self.model_items.append((model, category, description, size))

        self.update_model_count()

    def filter_models(self):
        """Filtra los modelos según la búsqueda"""
        search = self.search_box.text().lower().strip()

        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)

            if not data:
                # Es un separador, mostrar siempre
                item.setHidden(False)
                continue

            model = data[0].lower()
            desc = data[2].lower()

            if search in model or search in desc:
                item.setHidden(False)
            else:
                item.setHidden(True)

        self.update_model_count()

    def update_model_count(self):
        """Actualiza el contador de modelos"""
        visible = 0
        for i in range(self.model_list.count()):
            if not self.model_list.item(i).isHidden():
                visible += 1
        self.model_count_label.setText(f"Mostrando {visible} modelos")

    def refresh_all(self):
        """Refresca todo el estado"""
        self.find_ollama()
        self.refresh_model_list()
        self.status_label.setText(f"✅ Ollama actualizado")

    def refresh_model_list(self):
        """Refresca la lista de modelos instalados"""
        if self.list_worker and self.list_worker.is_alive():
            return

        self.installed_models = []
        self.list_worker = ListModelsWorker()
        self.list_worker.finished.connect(self.on_models_loaded)
        self.list_worker.error.connect(lambda e: self.log(f"❌ Error: {e}"))
        self.list_worker.start()

    def on_models_loaded(self, models):
        """Callback cuando se cargan los modelos instalados"""
        self.installed_models = models
        if self.current_model:
            self.update_model_status(self.current_model)

    def normalize_model_name(self, name):
        """Normaliza nombres para comparar modelos"""
        if not name:
            return ""
        name = str(name).strip().lower()
        if name.endswith(":latest"):
            name = name.replace(":latest", "")
        return name

    def is_model_installed(self, model):
        """Devuelve True si el modelo está instalado"""
        target = self.normalize_model_name(model)
        for installed in self.installed_models:
            installed_name = self.normalize_model_name(installed.get("name", ""))
            if installed_name == target:
                return True
        return False

    def get_installed_model_info(self, model):
        """Obtiene la información del modelo instalado"""
        target = self.normalize_model_name(model)
        for installed in self.installed_models:
            installed_name = self.normalize_model_name(installed.get("name", ""))
            if installed_name == target:
                return installed
        return None

    def update_model_status(self, model):
        """Actualiza el estado del modelo"""
        info = self.get_installed_model_info(model)

        if info:
            size = info.get('size', '')
            installed_name = info.get('name', model)
            self.model_status_label.setText(f"✅ Instalado como {installed_name} ({size})")
            self.model_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.model_status_label.setText("❌ No instalado")
            self.model_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def log(self, text):
        """Añade texto al log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {text}")
        cursor = self.log_box.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_box.setTextCursor(cursor)

    # ========================================================================
    # EVENTOS
    # ========================================================================

    def on_model_selected(self):
        """Cuando se selecciona un modelo"""
        current = self.model_list.currentItem()
        if not current:
            return

        data = current.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        model, category, description, size = data
        self.current_model = model

        self.model_name_label.setText(f"📦 {model}")
        self.model_category_label.setText(f"📌 {category}")
        self.model_desc_label.setText(f"📝 {description}")
        self.model_size_label.setText(f"💾 Tamaño: ~{size} GB")

        self.update_model_status(model)

    # ========================================================================
    # ACCIONES
    # ========================================================================

    def install_ollama(self):
        """Instala Ollama usando Winget"""
        reply = QMessageBox.question(
            self,
            "Instalar Ollama",
            "Se instalará Ollama usando Winget.\n\n"
            "Esto descargará e instalará Ollama en tu sistema.\n"
            "¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.log("📦 Instalando Ollama con Winget...")

        try:
            process = subprocess.Popen(
                ["winget", "install", "Ollama.Ollama"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False
            )

            for line in process.stdout:
                self.log(f"  {line.strip()}")

            process.wait()

            if process.returncode == 0:
                self.log("✅ Ollama instalado correctamente")
                self.find_ollama()
                QMessageBox.information(self, "Instalación", "✅ Ollama se instaló correctamente.")
            else:
                self.log("❌ Error en la instalación")
                QMessageBox.warning(self, "Error", "❌ No se pudo instalar Ollama.")

        except Exception as e:
            self.log(f"❌ Error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def download_model(self):
        """Descarga el modelo seleccionado"""
        if not self.current_model:
            QMessageBox.warning(self, "Selecciona un modelo", "Por favor selecciona un modelo de la lista.")
            return

        if self.is_downloading:
            QMessageBox.warning(self, "Descarga en curso", "Ya hay una descarga en progreso.")
            return

        if not self.ollama_exe:
            reply = QMessageBox.question(
                self,
                "Ollama no instalado",
                "Ollama no está instalado.\n\n"
                "¿Quieres instalarlo ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.install_ollama()
            return

        if self.is_model_installed(self.current_model):
            reply = QMessageBox.question(
                self,
                "Modelo ya instalado",
                f"El modelo {self.current_model} ya está instalado.\n\n"
                "¿Quieres descargarlo de nuevo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.is_downloading = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFormat("Iniciando...")
        self.btn_cancel.setVisible(True)
        self.model_list.setEnabled(False)

        self.log(f"⬇️ Iniciando descarga de: {self.current_model}")

        self.download_worker = DownloadWorker(self.current_model)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.log.connect(self.log)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def on_download_progress(self, current, total):
        """Actualiza la barra de progreso"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setFormat(f"Descargando... {percent}%")

    def on_download_finished(self, success, message):
        """Finaliza la descarga"""
        self.is_downloading = False
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")
        self.btn_cancel.setVisible(False)
        self.model_list.setEnabled(True)

        if success:
            self.log(f"✅ Modelo {self.current_model} descargado")
            self.refresh_model_list()
            self.update_model_status(self.current_model)
            QMessageBox.information(
                self,
                "Descarga completada",
                f"✅ El modelo {self.current_model} se descargó correctamente."
            )
        else:
            self.log(f"❌ Descarga fallida: {message}")
            if message != "Cancelada":
                QMessageBox.warning(self, "Descarga fallida", f"No se pudo descargar el modelo.\n\n{message}")

    def on_download_error(self, error):
        """Error en la descarga"""
        self.is_downloading = False
        self.progress_bar.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.model_list.setEnabled(True)
        self.log(f"❌ Error: {error}")
        QMessageBox.critical(self, "Error", error)

    def cancel_download(self):
        """Cancela la descarga actual"""
        if self.download_worker and self.is_downloading:
            reply = QMessageBox.question(
                self,
                "Cancelar descarga",
                "¿Estás seguro de que quieres cancelar la descarga?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.log("⛔ Cancelando descarga...")
                self.download_worker.cancel()
                self.btn_cancel.setEnabled(False)

    def uninstall_model(self):
        """Desinstala el modelo seleccionado"""
        if not self.current_model:
            QMessageBox.warning(self, "Selecciona un modelo", "Por favor selecciona un modelo de la lista.")
            return

        if not self.ollama_exe:
            QMessageBox.warning(self, "Ollama no instalado", "Ollama no está instalado.")
            return

        if not self.is_model_installed(self.current_model):
            QMessageBox.warning(self, "Modelo no instalado", f"El modelo {self.current_model} no está instalado.")
            return

        reply = QMessageBox.question(
            self,
            "Desinstalar modelo",
            f"¿Estás seguro de que quieres desinstalar el modelo?\n\n"
            f"📦 {self.current_model}\n\n"
            f"⚠️ Esta acción es irreversible y liberará espacio en disco.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.log(f"🗑️ Desinstalando: {self.current_model}")

        self.uninstall_worker = UninstallWorker(self.current_model)
        self.uninstall_worker.log.connect(self.log)
        self.uninstall_worker.finished.connect(self.on_uninstall_finished)
        self.uninstall_worker.error.connect(lambda e: self.log(f"❌ Error: {e}"))
        self.uninstall_worker.start()

    def on_uninstall_finished(self, success, message):
        """Finaliza la desinstalación"""
        if success:
            self.log(f"✅ {message}")
            self.refresh_model_list()
            self.update_model_status(self.current_model)
            QMessageBox.information(
                self,
                "Desinstalado",
                f"✅ El modelo {self.current_model} ha sido desinstalado correctamente."
            )
        else:
            self.log(f"❌ Error al desinstalar: {message}")
            QMessageBox.warning(
                self,
                "Error al desinstalar",
                f"No se pudo desinstalar el modelo.\n\n{message}"
            )

    def use_model(self):
        """Usa el modelo seleccionado"""
        if not self.current_model:
            QMessageBox.warning(self, "Selecciona un modelo", "Por favor selecciona un modelo de la lista.")
            return

        if not self.is_model_installed(self.current_model):
            QMessageBox.warning(
                self,
                "Modelo no instalado",
                f"El modelo {self.current_model} no está instalado.\n\n"
                "Primero descárgalo usando el botón 'Descargar modelo'."
            )
            return

        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        settings = {
            "provider": "ollama",
            "model": self.current_model,
            "api_key": "",
            "temperature": 0.2,
            "ollama_url": "http://localhost:11434/api/generate"
        }

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

        QMessageBox.information(
            self,
            "Configurado",
            f"✅ Ahora se usará Ollama con el modelo:\n\n📦 {self.current_model}"
        )

        self.accept()

    def export_log(self):
        """Exporta el log a un archivo"""
        from datetime import datetime
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar log",
            f"ollama_manager_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_box.toPlainText())
            QMessageBox.information(self, "Exportado", f"✅ Log exportado a:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el log:\n{str(e)}")