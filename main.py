import sys
import json
import os
import pandas as pd
import chardet

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QMessageBox, QLabel, QLineEdit, QProgressBar,
    QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

from languages import LANGUAGES, get_text
from settings_dialog import SettingsDialog
from ai_manager_dialog import AIManagerDialog
from prompt_editor_dialog import PromptEditorDialog
from providers.local_provider import MockProvider, OllamaProvider
from translation_worker import TranslationWorker


SUPPORTED_ENCODINGS = [
    "utf-8-sig",
    "utf-8",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "cp1252",
    "latin1",
    "cp1250",
    "cp1251",
    "cp1253",
    "cp1254",
    "cp932",
    "shift_jis",
    "gbk",
    "big5",
    "euc-kr",
]

CACHE_FILE = os.path.join(
    "config",
    "translation_cache.json"
)


class SkyrimTranslator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar configuración primero para saber el idioma
        self.settings = self.load_settings()
        self.ui_language = self.settings.get("ui_language", "Spanish")
        self.target_language = self.settings.get("target_language", "Spanish")
        
        self.setWindowTitle(self.tr("window_title"))
        self.resize(1400, 800)

        # Aplicar personalizaciones
        self.apply_appearance_settings()

        # MENÚ SUPERIOR
        self.create_menu_bar()

        # TABLA Y ESTADO
        self.table = QTableWidget()
        self.current_encoding = "utf-8"
        self.current_filter = "Todos"
        self.dictionary = {}
        self._row_data = {}

        # INFO
        self.label_info = QLabel(self.tr("no_file_loaded"))

        self.lbl_total = QLabel(self.tr("total").format(0))
        self.lbl_translated = QLabel(self.tr("translated").format(0))
        self.lbl_pending = QLabel(self.tr("pending").format(0))

        # BUSCADOR
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("search_placeholder"))
        self.search_box.textChanged.connect(self.apply_filters)

        # BOTONES PRINCIPALES (SOLO TRADUCCIONES)
        btn_copy_original = QPushButton(self.tr("btn_copy_original"))
        btn_translate_selected = QPushButton(self.tr("btn_translate_selected"))
        btn_translate_visible = QPushButton(self.tr("btn_translate_visible"))
        btn_translate_all = QPushButton(self.tr("btn_translate_all"))
        
        # BOTONES FILTRO
        btn_all = QPushButton(self.tr("btn_all"))
        btn_pending = QPushButton(self.tr("btn_pending"))
        btn_translated = QPushButton(self.tr("btn_translated"))

        # EVENTOS
        btn_copy_original.clicked.connect(self.copy_original_to_translation)
        btn_translate_selected.clicked.connect(self.translate_selected_ai)
        btn_translate_visible.clicked.connect(self.translate_visible_ai)
        btn_translate_all.clicked.connect(self.translate_all_ai)
        btn_all.clicked.connect(self.show_all)
        btn_pending.clicked.connect(self.show_pending)
        btn_translated.clicked.connect(self.show_translated)

        # LAYOUT BOTONES PRINCIPALES
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_copy_original)
        buttons_layout.addWidget(btn_translate_selected)
        buttons_layout.addWidget(btn_translate_visible)
        buttons_layout.addWidget(btn_translate_all)

        # LAYOUT ESTADÍSTICAS
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.lbl_total)
        stats_layout.addWidget(self.lbl_translated)
        stats_layout.addWidget(self.lbl_pending)

        # LAYOUT FILTROS
        filter_buttons = QHBoxLayout()
        filter_buttons.addWidget(btn_all)
        filter_buttons.addWidget(btn_pending)
        filter_buttons.addWidget(btn_translated)

        # BARRA DE PROGRESO Y BOTÓN CANCELAR
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        btn_cancel_translation = QPushButton(self.tr("btn_cancel"))
        btn_cancel_translation.clicked.connect(self.cancel_translation)
        btn_cancel_translation.setVisible(False)

        self.btn_cancel_translation = btn_cancel_translation
        self.translation_worker = None
        self.translation_cache = self.load_translation_cache()
        self.migrate_cache_to_multilang()
        self.same_text_is_translated = self.settings.get("same_text_is_translated", False)
        self.pending_duplicate_rows = {}

        # LAYOUT GENERAL
        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(self.label_info)
        layout.addLayout(stats_layout)
        layout.addWidget(self.search_box)
        layout.addLayout(filter_buttons)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_cancel_translation)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # CARGAR AUTO-SAVE AL INICIAR
        self.load_auto_save()

        self.table.itemChanged.connect(self.on_translation_changed)

    def tr(self, key, **kwargs):
        """Traduce un texto según el idioma UI actual"""
        return get_text(key, self.ui_language, **kwargs)

    def create_menu_bar(self):
        """Crea la barra de menú completa"""
        menubar = self.menuBar()

        # ===== MENÚ ARCHIVO =====
        self.archivo_menu = menubar.addMenu(self.tr("menu_file"))
        
        action_open_txt = QAction("📂 Abrir TXT de xEdit", self)
        action_open_txt.triggered.connect(self.open_file)
        self.archivo_menu.addAction(action_open_txt)
        
        self.archivo_menu.addSeparator()
        
        action_export = QAction(self.tr("menu_export"), self)
        action_export.triggered.connect(self.export_file)
        self.archivo_menu.addAction(action_export)
        
        self.archivo_menu.addSeparator()
        
        # Cargar auto-save manualmente
        action_load_auto_save = QAction("📂 Cargar auto-save", self)
        action_load_auto_save.triggered.connect(self.load_auto_save)
        self.archivo_menu.addAction(action_load_auto_save)
        
        action_save_project = QAction(self.tr("menu_save_project"), self)
        action_save_project.triggered.connect(self.save_project)
        self.archivo_menu.addAction(action_save_project)
        
        action_open_project = QAction(self.tr("menu_open_project"), self)
        action_open_project.triggered.connect(self.open_project)
        self.archivo_menu.addAction(action_open_project)
        
        self.archivo_menu.addSeparator()
        
        action_auto_save = QAction(self.tr("menu_auto_save"), self)
        action_auto_save.setCheckable(True)
        action_auto_save.setChecked(self.settings.get("auto_save", True))
        action_auto_save.triggered.connect(self.toggle_auto_save)
        self.archivo_menu.addAction(action_auto_save)
        
        self.archivo_menu.addSeparator()
        
        action_exit = QAction(self.tr("menu_exit"), self)
        action_exit.triggered.connect(self.close)
        self.archivo_menu.addAction(action_exit)

        # ===== MENÚ HERRAMIENTAS =====
        self.herramientas_menu = menubar.addMenu(self.tr("menu_tools"))
        
        action_load_dictionary = QAction(self.tr("menu_load_dictionary"), self)
        action_load_dictionary.triggered.connect(self.load_dictionary)
        self.herramientas_menu.addAction(action_load_dictionary)
        
        action_apply_dictionary = QAction(self.tr("menu_apply_dictionary"), self)
        action_apply_dictionary.triggered.connect(self.apply_dictionary)
        self.herramientas_menu.addAction(action_apply_dictionary)
        
        self.herramientas_menu.addSeparator()
        
        # Exportar traducciones para xEdit (formato completo)
        action_export_xedit = QAction("📥 Exportar traducciones para xEdit (completo)", self)
        action_export_xedit.triggered.connect(self.export_to_xedit_complete)
        self.herramientas_menu.addAction(action_export_xedit)
        
        self.herramientas_menu.addSeparator()
        
        action_clear_cache = QAction("🗑️ Limpiar caché de traducciones", self)
        action_clear_cache.triggered.connect(self.clear_cache)
        self.herramientas_menu.addAction(action_clear_cache)
        
        # NUEVO: Reconstruir caché
        action_rebuild_cache = QAction("🔄 Reconstruir caché (traducciones consistentes)", self)
        action_rebuild_cache.triggered.connect(self.rebuild_cache)
        self.herramientas_menu.addAction(action_rebuild_cache)

        action_retranslate_selected = QAction("♻️ Retraducir seleccionados (ignorar caché)", self)
        action_retranslate_selected.triggered.connect(self.retranslate_selected_ai)
        self.herramientas_menu.addAction(action_retranslate_selected)

        self.action_same_text_translated = QAction("✅ Texto igual cuenta como traducido", self)
        self.action_same_text_translated.setCheckable(True)
        self.action_same_text_translated.setChecked(self.settings.get("same_text_is_translated", False))
        self.action_same_text_translated.triggered.connect(self.toggle_same_text_translated)
        self.herramientas_menu.addAction(self.action_same_text_translated)
        
        self.herramientas_menu.addSeparator()
        
        action_copy_original = QAction(self.tr("menu_copy_original"), self)
        action_copy_original.triggered.connect(self.copy_original_to_translation)
        self.herramientas_menu.addAction(action_copy_original)

        # ===== MENÚ IA =====
        self.ia_menu = menubar.addMenu(self.tr("menu_ai"))
        
        action_ai_settings = QAction(self.tr("menu_ai_settings"), self)
        action_ai_settings.triggered.connect(self.open_ai_settings)
        self.ia_menu.addAction(action_ai_settings)
        
        action_ai_manager = QAction(self.tr("menu_ai_manager"), self)
        action_ai_manager.triggered.connect(self.open_ai_manager)
        self.ia_menu.addAction(action_ai_manager)
        
        self.ia_menu.addSeparator()
        
        action_prompt_editor = QAction(self.tr("menu_prompt_editor"), self)
        action_prompt_editor.triggered.connect(self.open_prompt_editor)
        self.ia_menu.addAction(action_prompt_editor)
        
        self.ia_menu.addSeparator()
        
        action_translate_selected = QAction(self.tr("menu_translate_selected"), self)
        action_translate_selected.triggered.connect(self.translate_selected_ai)
        self.ia_menu.addAction(action_translate_selected)
        
        action_translate_visible = QAction(self.tr("menu_translate_visible"), self)
        action_translate_visible.triggered.connect(self.translate_visible_ai)
        self.ia_menu.addAction(action_translate_visible)
        
        action_translate_all = QAction(self.tr("menu_translate_all"), self)
        action_translate_all.triggered.connect(self.translate_all_ai)
        self.ia_menu.addAction(action_translate_all)

        # ===== MENÚ AYUDA =====
        self.ayuda_menu = menubar.addMenu(self.tr("menu_help"))
        
        action_about = QAction(self.tr("menu_about"), self)
        action_about.triggered.connect(self.show_about)
        self.ayuda_menu.addAction(action_about)

    def load_settings(self):
        settings_path = os.path.join("config", "settings.json")
        
        if not os.path.exists(settings_path):
            return {
                "ui_language": "Spanish",
                "target_language": "Spanish",
                "theme": "dark",
                "window_opacity": 100,
                "font_size": 13,
                "auto_save": True,
                "confirm_exit": True,
                "show_tooltips": True
            }
        
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {
                "ui_language": "Spanish",
                "target_language": "Spanish",
                "theme": "dark",
                "window_opacity": 100,
                "font_size": 13,
                "auto_save": True,
                "confirm_exit": True,
                "show_tooltips": True
            }

    def save_settings(self):
        """Guarda la configuración actual"""
        try:
            os.makedirs("config", exist_ok=True)
            settings_path = os.path.join("config", "settings.json")
            
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def apply_appearance_settings(self):
        # Aplicar opacidad
        opacity = self.settings.get("window_opacity", 100)
        self.setWindowOpacity(opacity / 100.0)
        
        # Aplicar tamaño de fuente
        font_size = self.settings.get("font_size", 13)
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Aplicar tema
        theme = self.settings.get("theme", "dark")
        if theme == "light":
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e6e6e6;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #e6e6e6;
            }
            QMenuBar::item {
                background-color: #2d2d30;
                color: #e6e6e6;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenu {
                background-color: #2d2d30;
                color: #e6e6e6;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QPushButton {
                background-color: #2d2d30;
                color: white;
                border: 1px solid #3e3e42;
                padding: 8px;
                border-radius: 5px;
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
            QTableWidget {
                background-color: #252526;
                color: #e6e6e6;
                gridline-color: #3e3e42;
                selection-background-color: #094771;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: white;
                padding: 6px;
                border: 1px solid #3e3e42;
            }
            QLabel {
                color: #e6e6e6;
            }
            QProgressBar {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #094771;
                border-radius: 5px;
            }
            QTabWidget::pane {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #e6e6e6;
                padding: 8px 12px;
                border: 1px solid #3e3e42;
            }
            QTabBar::tab:selected {
                background-color: #094771;
            }
        """)
    
    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QWidget {
                background-color: #f0f0f0;
                color: #000000;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #000000;
            }
            QMenuBar::item {
                background-color: #ffffff;
                color: #000000;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #094771;
                color: white;
            }
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 7px;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #000000;
                gridline-color: #cccccc;
                selection-background-color: #094771;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                color: #000000;
                padding: 6px;
                border: 1px solid #cccccc;
            }
            QLabel {
                color: #000000;
            }
            QProgressBar {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #094771;
                border-radius: 5px;
            }
            QTabWidget::pane {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #000000;
                padding: 8px 12px;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: #094771;
                color: white;
            }
        """)

    def toggle_auto_save(self, checked):
        self.settings["auto_save"] = checked
        self.save_settings()

    def load_auto_save(self):
        """Carga automáticamente el auto-save al iniciar la aplicación"""
        auto_save_path = os.path.join("config", "auto_save.json")
        
        if not os.path.exists(auto_save_path):
            return
        
        if self.table.rowCount() > 0:
            return
        
        try:
            with open(auto_save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "records" not in data or not data["records"]:
                return
            
            rows = []
            for r in data["records"]:
                row_data = {
                    "formid": r.get("formid", ""),
                    "edid": r.get("edid", ""),
                    "original": r.get("original", ""),
                    "translated": r.get("translated", ""),
                    "signature": r.get("signature", ""),
                    "fields": r.get("fields", {"FULL": r.get("original", "")})
                }
                rows.append(row_data)
            
            self.setup_table(rows)
            self.label_info.setText(
                f"📂 Auto-save cargado automáticamente: {len(rows)} registros"
            )
            print(f"✅ Auto-save cargado: {len(rows)} registros")
            
        except Exception as e:
            print(f"❌ Error cargando auto-save: {e}")

    def save_auto_save(self):
        """Guarda el auto-save manualmente"""
        if self.table.rowCount() == 0:
            return
        
        try:
            os.makedirs("config", exist_ok=True)
            data = {
                "app": "Skyrim AI Translator",
                "version": "0.6",
                "records": []
            }
            for row in range(self.table.rowCount()):
                record = {
                    "formid": self.safe_text(row, 0),
                    "edid": self.safe_text(row, 1),
                    "original": self.safe_text(row, 2),
                    "translated": self.safe_text(row, 3)
                }
                if row in self._row_data:
                    record["signature"] = self._row_data[row].get("signature", "")
                    record["fields"] = self._row_data[row].get("fields", {})
                data["records"].append(record)
                
            auto_save_path = os.path.join("config", "auto_save.json")
            with open(auto_save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error guardando auto-save: {e}")

    def load_translation_cache(self):
        """Carga la caché multidioma"""
        if not os.path.exists(CACHE_FILE):
            return {}

        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_translation_cache(self, cache):
        """Guarda la caché multidioma"""
        os.makedirs("config", exist_ok=True)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)

    def migrate_cache_to_multilang(self):
        """Convierte la caché antigua (string) al nuevo formato multidioma"""
        if not self.translation_cache:
            return
        
        migrated = False
        for key, value in self.translation_cache.items():
            if not isinstance(value, dict):
                self.translation_cache[key] = {"Spanish": value}
                migrated = True
        
        if migrated:
            self.save_translation_cache(self.translation_cache)
            print("✅ Caché migrada a formato multidioma")

    def get_cached_translation(self, original, language):
        """Obtiene una traducción de la caché para un idioma específico"""
        if original in self.translation_cache:
            lang_cache = self.translation_cache[original]
            if isinstance(lang_cache, dict):
                # Si existe en el idioma solicitado
                if language in lang_cache:
                    return lang_cache[language]
                # Si no existe en el idioma, devolver None (no usar español como fallback)
                return None
            elif language == "Spanish":
                return lang_cache
        return None

    def set_cached_translation(self, original, language, translation):
        """Guarda una traducción en la caché para un idioma específico"""
        if original not in self.translation_cache:
            self.translation_cache[original] = {}
        
        if not isinstance(self.translation_cache[original], dict):
            old_value = self.translation_cache[original]
            self.translation_cache[original] = {"Spanish": old_value}
        
        self.translation_cache[original][language] = translation
        self.save_translation_cache(self.translation_cache)

    def clear_cache_entry(self, original):
        """Elimina una entrada específica de la caché"""
        if original in self.translation_cache:
            del self.translation_cache[original]
            self.save_translation_cache(self.translation_cache)
            return True
        return False

    def rebuild_cache(self):
        """Reconstruye la caché traduciendo nuevamente todos los textos únicos"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Primero carga un archivo.")
            return
        
        # Obtener todos los textos originales únicos
        originals = set()
        for row in range(self.table.rowCount()):
            original = self.safe_text(row, 2)
            if original:
                originals.add(original)
        
        if not originals:
            QMessageBox.warning(self, "Aviso", "No hay textos para procesar.")
            return
        
        confirm = QMessageBox.question(
            self,
            "Reconstruir caché",
            f"Se traducirán {len(originals)} textos únicos para el idioma '{self.target_language}'.\n\n"
            "Esto puede tardar varios minutos.\n\n"
            "¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            provider = self.get_ai_provider()
            target_lang = self.target_language
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(originals))
            self.btn_cancel_translation.setVisible(True)
            
            translated_count = 0
            current = 0
            
            for original in originals:
                try:
                    translated = provider.translate(original)
                    if translated:
                        # El worker limpia mejor, pero aquí al menos evitamos cachear vacío.
                        self.set_cached_translation(original, target_lang, translated)
                        translated_count += 1
                except Exception as e:
                    print(f"Error traduciendo '{original}': {e}")
                
                current += 1
                self.progress_bar.setValue(current)
            
            self.progress_bar.setVisible(False)
            self.btn_cancel_translation.setVisible(False)
            
            # Recargar la tabla para mostrar las nuevas traducciones
            self.reload_table_translations()
            
            QMessageBox.information(
                self,
                "Caché reconstruida",
                f"✅ Se tradujeron {translated_count} nuevos textos al idioma '{target_lang}'.\n\n"
                f"Los textos duplicados ahora usarán las mismas traducciones."
            )
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.btn_cancel_translation.setVisible(False)
            QMessageBox.critical(self, "Error", str(e))

    def reload_table_translations(self):
        """Recarga las traducciones de la tabla con el nuevo idioma destino"""
        if self.table.rowCount() == 0:
            return
        
        self.table.blockSignals(True)
        
        for row in range(self.table.rowCount()):
            original = self.safe_text(row, 2)
            if not original:
                continue
            
            cached = self.get_cached_translation(original, self.target_language)
            if cached:
                self.table.setItem(row, 3, QTableWidgetItem(cached))
                self.refresh_row_status(row)
            else:
                self.table.setItem(row, 3, QTableWidgetItem(original))
                self.table.setItem(row, 4, QTableWidgetItem(self.tr("status_pending")))
        
        self.table.blockSignals(False)
        self.update_stats()
        self.apply_filters()

    def update_ui_texts(self):
        """Actualiza todos los textos de la interfaz cuando cambia el idioma"""
        self.setWindowTitle(self.tr("window_title"))
        self.label_info.setText(self.tr("no_file_loaded"))
        self.lbl_total.setText(self.tr("total").format(self.table.rowCount()))
        self.lbl_translated.setText(self.tr("translated").format(0))
        self.lbl_pending.setText(self.tr("pending").format(0))
        self.search_box.setPlaceholderText(self.tr("search_placeholder"))
        
        self.archivo_menu.setTitle(self.tr("menu_file"))
        self.herramientas_menu.setTitle(self.tr("menu_tools"))
        self.ia_menu.setTitle(self.tr("menu_ai"))
        self.ayuda_menu.setTitle(self.tr("menu_help"))
        
        self.table.setHorizontalHeaderLabels([
            self.tr("col_formid"),
            self.tr("col_edid"),
            self.tr("col_original"),
            self.tr("col_translation"),
            self.tr("col_status")
        ])
        
        self.update_stats()

    def open_ai_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            old_target = self.target_language
            self.settings = self.load_settings()
            self.ui_language = self.settings.get("ui_language", "Spanish")
            self.target_language = self.settings.get("target_language", "Spanish")
            
            if self.table.rowCount() > 0:
                self.reload_table_translations()
            
            self.apply_appearance_settings()
            self.update_ui_texts()

    def open_ai_manager(self):
        dialog = AIManagerDialog(self)
        dialog.exec()

    def open_prompt_editor(self):
        dialog = PromptEditorDialog(self)
        dialog.exec()

    def show_about(self):
        QMessageBox.about(
            self,
            self.tr("msg_about_title"),
            self.tr("msg_about_text")
        )

    def load_ai_settings(self):
        path = os.path.join("config", "settings.json")
        if not os.path.exists(path):
            return {
                "provider": "mock",
                "model": "mock-free",
                "target_language": self.target_language
            }
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            settings["target_language"] = self.target_language
            return settings

    def get_ai_provider(self):
        settings = self.load_ai_settings()
        provider = settings.get("provider", "mock")
        if provider == "ollama":
            return OllamaProvider(settings)
        return MockProvider(settings)

    def translate_rows_ai(self, rows, force_retranslate=False):
        if not rows:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_no_rows"))
            return

        try:
            provider = self.get_ai_provider()
            target_lang = self.target_language

            # PRIMERO: Recopilar todos los textos únicos
            originals_map = {}
            unique_texts = {}
            for row in rows:
                original = self.safe_text(row, 2)
                if original:
                    originals_map[row] = original
                    if original not in unique_texts:
                        unique_texts[original] = []
                    unique_texts[original].append(row)

            # SEGUNDO: Buscar en caché y diccionario
            cached_translations = {}
            texts_to_translate = []
            
            for original, row_list in unique_texts.items():
                translation = None
                
                # Verificar en diccionario/caché, salvo cuando se fuerce retraducción
                if not force_retranslate and original in self.dictionary:
                    translation = self.dictionary[original]
                elif not force_retranslate:
                    translation = self.get_cached_translation(original, target_lang)
                
                if translation:
                    # Asignar a todas las filas que tienen este texto
                    for row in row_list:
                        cached_translations[row] = translation
                else:
                    # Marcar para traducción (solo una vez por texto único)
                    texts_to_translate.append((original, row_list[0]))
                    self.pending_duplicate_rows[row_list[0]] = row_list

            # TERCERO: Aplicar traducciones en caché
            if cached_translations:
                self.table.blockSignals(True)
                for row, translation in cached_translations.items():
                    self.table.setItem(row, 3, QTableWidgetItem(translation))
                    self.refresh_row_status(row)
                self.table.blockSignals(False)
                self.update_stats()

            # CUARTO: Traducir textos únicos que faltan
            if not texts_to_translate:
                QMessageBox.information(
                    self,
                    "Caché/Diccionario",
                    self.tr("msg_cache_dictionary").format(len(cached_translations))
                )
                self.apply_filters()
                return

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(texts_to_translate))
            self.btn_cancel_translation.setVisible(True)

            # Crear worker con los textos únicos
            self.translation_worker = TranslationWorker(
                texts_to_translate,  # [(original, row)]
                {original: original for original, row in texts_to_translate},
                provider,
                self.translation_cache,
                self.dictionary,
                target_lang,
                force_retranslate=force_retranslate,
                cache_same_as_original=self.same_text_is_translated
            )

            self.translation_worker.progress.connect(self.on_translation_progress)
            self.translation_worker.row_translated.connect(self.on_row_translated)
            self.translation_worker.finished.connect(self.on_translation_finished)
            self.translation_worker.error.connect(self.on_translation_error)
            self.translation_worker.cache_updated.connect(self.on_cache_updated)

            self.translation_worker.start()

        except Exception as e:
            QMessageBox.critical(self, self.tr("error_ai"), str(e))

    def on_translation_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def on_row_translated(self, row, original, translated):
        self.table.blockSignals(True)
        rows_to_update = self.pending_duplicate_rows.pop(row, [row])
        for target_row in rows_to_update:
            self.table.setItem(target_row, 3, QTableWidgetItem(translated))
            self.refresh_row_status(target_row)
        self.table.blockSignals(False)
        self.update_stats()

    def on_cache_updated(self, original, language, translated):
        self.set_cached_translation(original, language, translated)

    def on_translation_finished(self, translated_count):
        self.progress_bar.setVisible(False)
        self.btn_cancel_translation.setVisible(False)
        self.update_stats()
        self.apply_filters()
        QMessageBox.information(
            self,
            self.tr("Traducción finalizada"),
            self.tr("msg_translation_finished").format(translated_count, CACHE_FILE)
        )

    def on_translation_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.btn_cancel_translation.setVisible(False)
        QMessageBox.critical(self, self.tr("error_ai"), error_message)

    def cancel_translation(self):
        if self.translation_worker:
            self.translation_worker.cancel()
            QMessageBox.information(self, self.tr("Cancelando"), self.tr("msg_cancel_translation"))


    def retranslate_selected_ai(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_select_rows"))
            return
        rows = sorted(set(item.row() for item in selected))
        self.translate_rows_ai(rows, force_retranslate=True)

    def toggle_same_text_translated(self, checked):
        self.same_text_is_translated = bool(checked)
        self.settings["same_text_is_translated"] = self.same_text_is_translated
        self.save_settings()
        self.refresh_all_statuses()
        self.apply_filters()

    def translate_selected_ai(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_select_rows"))
            return
        rows = sorted(set(item.row() for item in selected))
        self.translate_rows_ai(rows)

    def translate_visible_ai(self):
        rows = []
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                rows.append(row)
        self.translate_rows_ai(rows)

    def translate_all_ai(self):
        rows = list(range(self.table.rowCount()))
        confirm = QMessageBox.question(
            self,
            self.tr("Confirmar"),
            self.tr("msg_confirm_translate_all").format(len(rows))
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.translate_rows_ai(rows)

    def read_file_with_multiple_encodings(self, path):
        """Intenta leer un archivo con múltiples codificaciones"""
        from io import StringIO

        encodings = [
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
            "cp1252",
            "latin1",
            "cp1251",
            "gbk",
            "big5",
            "shift_jis",
            "cp932",
            "euc-kr",
            "cp949"
        ]

        last_error = None

        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    text = f.read()

                text = text.replace("\ufeff", "")

                if "|" not in text:
                    continue

                df = pd.read_csv(
                    StringIO(text),
                    sep="|",
                    dtype=str,
                    keep_default_na=False
                )

                df.columns = [
                    str(c).replace("\ufeff", "").strip()
                    for c in df.columns
                ]

                self.current_encoding = enc
                return df

            except Exception as e:
                last_error = e
                continue

        raise Exception(
            "No se pudo leer el archivo.\n\n"
            "Formato esperado:\n"
            "FormID|Signature|EDID|Field|Original\n"
            "o\n"
            "FormID|EDID|FULL\n\n"
            f"Último error: {last_error}"
        )

    def open_file(self):
        """Abre un archivo exportado desde xEdit"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir TXT de xEdit",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            df = self.read_file_with_multiple_encodings(path)

            # Limpiar nombres de columnas
            df.columns = [
                str(c).replace("\ufeff", "").strip()
                for c in df.columns
            ]

            columns = df.columns.tolist()
            print(f"📋 Columnas encontradas: {columns}")

            # Detectar formato y cargar
            if "Signature" in columns and "Field" in columns and "Original" in columns:
                # Formato completo: FormID|Signature|EDID|Field|Original
                self.load_xedit_export(df, path)
            elif "FULL" in columns:
                # Formato simple: FormID|EDID|FULL
                self.load_simple_export(df, path)
            else:
                raise Exception(
                    f"No se pudo identificar el formato del archivo.\n\n"
                    f"Columnas encontradas: {columns}\n\n"
                    f"Formatos soportados:\n"
                    f"1. FormID|Signature|EDID|Field|Original\n"
                    f"2. FormID|EDID|FULL"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error al abrir archivo", str(e))

    def clean_ai_explanation_text(self, text):
        """Quita notas y explicaciones que la IA pudo haber metido en el texto."""
        import re
        text = str(text or "").replace("\ufeff", "").strip()
        text = re.sub(r'^\s*["“”\'`]+|["“”\'`]+\s*$', '', text).strip()

        markers = [
            r'Traducci[oó]n\s*\([^)]*\)\s*:', r'Traducci[oó]n\s*:',
            r'Translation\s*\([^)]*\)\s*:', r'Translation\s*:',
            r'Respuesta\s*(?:en\s+espa[nñ]ol)?\s*:', r'Response\s*:',
            r'Resultado\s*:', r'Result\s*:', r'Output\s*:', r'Salida\s*:',
            r'Correct translation\s*\([^)]*\)\s*:', r'Correction in Spanish\s*:'
        ]
        for marker in markers:
            matches = list(re.finditer(marker, text, flags=re.I))
            if matches:
                text = text[matches[-1].end():].strip()

        cut_patterns = [
            r'\s*\(\s*(?:please note|remember|note|notes|nota|notas|explanation|explicaci[oó]n|incorrect|wrong|keep|as per|for consistency|blood loss|no requiere|there is no need|this is because|this translation).*?\)\s*$',
            r'\s+(?:Please note|Remember|Note|Notes|Nota|Notas|Explanation|Explicaci[oó]n|Incorrect|Wrong)\s*:.*$',
            r'\s+(?:This translation|This keeps|This is because|I have|I\'ve|He mantenido|As per your rules|For consistency).*$',
            r'\s+(?:KEEP|Keep)\s+(?:as is|exactly|MC|the).*$',
            r'\s+No se requiere traducci[oó]n\s*.*$',
            r'\s+There(?:\'s| is) no need for translation\s*.*$',
            r'\s+In this case, there(?:\'s| is) no need for translation\s*.*$',
            r'\s+Correct translation\s*.*$',
            r'\s+Correction in Spanish\s*.*$',
        ]
        changed = True
        while changed:
            before = text
            for pat in cut_patterns:
                text = re.sub(pat, '', text, flags=re.I | re.S).strip()
            changed = before != text

        text = re.sub(r'[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\s+([.,;:!?])', r'\1', text).strip()
        return text

    def load_xedit_export(self, df, path):
        """Carga un archivo exportado con el formato completo de xEdit"""
        rows = []
        grouped = {}
        
        print(f"📊 Procesando {len(df)} filas...")
        
        for idx, r in df.iterrows():
            try:
                formid = str(r["FormID"]).strip()
                signature = str(r["Signature"]).strip()
                edid = str(r["EDID"]).strip()
                field = str(r["Field"]).strip()
                original = str(r["Original"]).strip()
                
                # Saltar filas vacías o con datos inválidos
                if not formid or formid == 'FormID' or not original:
                    continue
                
                # Crear clave única
                key = f"{formid}|{edid}"
                
                if key not in grouped:
                    grouped[key] = {
                        "formid": formid,
                        "edid": edid,
                        "signature": signature,
                        "fields": {}
                    }
                
                grouped[key]["fields"][field] = original
                
            except Exception as e:
                print(f"⚠️ Error en fila {idx}: {e}")
                continue
        
        print(f"📊 Agrupados: {len(grouped)} registros únicos")
        
        # Convertir a filas de tabla
        for key, data in grouped.items():
            formid = data["formid"]
            edid = data["edid"]
            signature = data["signature"]
            
            # Determinar texto principal
            if "FULL" in data["fields"]:
                original = data["fields"]["FULL"]
            elif "DESC" in data["fields"]:
                original = data["fields"]["DESC"]
            elif "CNAM" in data["fields"]:
                original = data["fields"]["CNAM"]
            elif "DNAM" in data["fields"]:
                original = data["fields"]["DNAM"]
            else:
                original = list(data["fields"].values())[0]
            
            rows.append({
                "formid": formid,
                "edid": edid,
                "original": original,
                "translated": original,
                "signature": signature,
                "fields": data["fields"]
            })
        
        if not rows:
            raise Exception("No se encontraron registros válidos en el archivo.")
        
        self.setup_table(rows)
        
        total_fields = sum(len(r["fields"]) for r in rows)
        self.label_info.setText(
            f"📂 Archivo cargado: {os.path.basename(path)} | "
            f"Registros: {len(rows)} | "
            f"Campos totales: {total_fields} | "
            f"Encoding: {self.current_encoding}"
        )
        
        self.save_auto_save()
        print(f"✅ Cargados {len(rows)} registros con {total_fields} campos")

    def load_simple_export(self, df, path):
        """Carga un archivo con formato simple (FormID|EDID|FULL)"""
        rows = []
        
        for idx, r in df.iterrows():
            try:
                formid = str(r["FormID"]).strip()
                edid = str(r["EDID"]).strip()
                original = self.clean_ai_explanation_text(r["FULL"])
                
                if not original or original == 'FULL':
                    continue
                
                rows.append({
                    "formid": formid,
                    "edid": edid,
                    "original": original,
                    "translated": original,
                    "signature": "",
                    "fields": {"FULL": original}
                })
            except Exception as e:
                print(f"⚠️ Error en fila {idx}: {e}")
                continue
        
        if not rows:
            raise Exception("No se encontraron registros válidos en el archivo.")
        
        self.setup_table(rows)
        self.label_info.setText(
            f"📂 Archivo cargado: {os.path.basename(path)} | "
            f"Registros: {len(rows)} | "
            f"Encoding: {self.current_encoding}"
        )
        
        self.save_auto_save()

    def setup_table(self, rows):
        """Configura la tabla con los datos cargados"""
        self.table.blockSignals(True)
        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            self.tr("col_formid"),
            self.tr("col_edid"),
            self.tr("col_original"),
            self.tr("col_translation"),
            self.tr("col_status")
        ])
        self.table.setRowCount(len(rows))
        
        self._row_data = {}

        for row, item in enumerate(rows):
            formid = item["formid"]
            edid = item["edid"]
            original = item["original"]
            translated = item["translated"]
            estado = self.tr("status_translated") if self.is_translation_done(original, translated) else self.tr("status_pending")
            
            self.table.setItem(row, 0, QTableWidgetItem(formid))
            self.table.setItem(row, 1, QTableWidgetItem(edid))
            self.table.setItem(row, 2, QTableWidgetItem(original))
            self.table.setItem(row, 3, QTableWidgetItem(translated))
            self.table.setItem(row, 4, QTableWidgetItem(estado))
            
            self._row_data[row] = {
                "signature": item.get("signature", ""),
                "fields": item.get("fields", {"FULL": original})
            }

        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)
        self.update_stats()
        self.apply_filters()

    def get_row_data(self, row):
        """Obtiene los datos completos de una fila (incluyendo campos)"""
        return self._row_data.get(row, {})

    def export_to_xedit_complete(self):
        """Exporta todas las traducciones en formato xEdit"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_no_file"))
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar traducciones para xEdit",
            "Skyrim_Texts_Translated.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not path:
            return
        
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write("FormID|Signature|EDID|Field|Translated\n")
                
                exported_count = 0
                
                for row in range(self.table.rowCount()):
                    formid = self.safe_text(row, 0)
                    edid = self.safe_text(row, 1)
                    translated = self.safe_text(row, 3)
                    original = self.safe_text(row, 2)
                    
                    if translated == original or not translated:
                        continue
                    
                    row_data = self.get_row_data(row)
                    signature = row_data.get("signature", "")
                    fields = row_data.get("fields", {"FULL": original})
                    
                    for field, original_text in fields.items():
                        translated_text = translated
                        translated_text = translated_text.replace("|", "/")
                        translated_text = translated_text.replace("\n", "<br>")
                        translated_text = translated_text.replace("\r", "")
                        
                        f.write(f"{formid}|{signature}|{edid}|{field}|{translated_text}\n")
                        exported_count += 1
            
            QMessageBox.information(
                self,
                "Listo",
                f"✅ Archivo exportado correctamente.\n\n"
                f"📋 Campos exportados: {exported_count}\n\n"
                f"📁 Guarda este archivo en:\n"
                f"xEdit\\Edit Scripts\\Skyrim_Texts_Translated.txt\n\n"
                f"🔄 Luego ejecuta el script de importación en xEdit."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    def safe_text(self, row, column):
        item = self.table.item(row, column)
        if item is None:
            return ""
        return item.text().replace("\n", " ").replace("\r", " ").strip()

    def on_translation_changed(self, item):
        if item.column() != 3:
            return
        row = item.row()
        original = self.safe_text(row, 2)
        translated = self.safe_text(row, 3)
        estado = self.tr("status_translated") if self.is_translation_done(original, translated) else self.tr("status_pending")
        self.table.blockSignals(True)
        self.table.setItem(row, 4, QTableWidgetItem(estado))
        self.table.blockSignals(False)
        self.update_stats()
        self.apply_filters()

    def copy_original_to_translation(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, self.tr("Información"), self.tr("msg_select_rows"))
            return
        rows = set()
        for item in selected:
            rows.add(item.row())
        self.table.blockSignals(True)
        for row in rows:
            original = self.safe_text(row, 2)
            self.table.setItem(row, 3, QTableWidgetItem(original))
            self.refresh_row_status(row)
        self.table.blockSignals(False)
        self.update_stats()
        self.apply_filters()


    def is_translation_done(self, original, translated):
        translated = (translated or "").strip()
        original = (original or "").strip()
        if not translated:
            return False
        if self.same_text_is_translated:
            return True
        return translated != original

    def refresh_row_status(self, row):
        original = self.safe_text(row, 2)
        translated = self.safe_text(row, 3)
        status = self.tr("status_translated") if self.is_translation_done(original, translated) else self.tr("status_pending")
        self.table.setItem(row, 4, QTableWidgetItem(status))

    def refresh_all_statuses(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            self.refresh_row_status(row)
        self.table.blockSignals(False)
        self.update_stats()

    def update_stats(self):
        total = self.table.rowCount()
        translated = 0
        pending = 0
        for row in range(total):
            estado_item = self.table.item(row, 4)
            if not estado_item:
                continue
            estado = estado_item.text()
            if estado == self.tr("status_translated"):
                translated += 1
            else:
                pending += 1
        self.lbl_total.setText(self.tr("total").format(total))
        self.lbl_translated.setText(self.tr("translated").format(translated))
        self.lbl_pending.setText(self.tr("pending").format(pending))

    def row_matches_search(self, row):
        text = self.search_box.text().lower().strip()
        if text == "":
            return True
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item and text in item.text().lower():
                return True
        return False

    def row_matches_status_filter(self, row):
        if self.current_filter == self.tr("btn_all"):
            return True
        estado_item = self.table.item(row, 4)
        if not estado_item:
            return False
        estado = estado_item.text()
        if self.current_filter == self.tr("btn_pending"):
            return estado == self.tr("status_pending")
        if self.current_filter == self.tr("btn_translated"):
            return estado == self.tr("status_translated")
        return True

    def apply_filters(self):
        for row in range(self.table.rowCount()):
            visible = self.row_matches_search(row) and self.row_matches_status_filter(row)
            self.table.setRowHidden(row, not visible)

    def show_all(self):
        self.current_filter = self.tr("btn_all")
        self.apply_filters()

    def show_pending(self):
        self.current_filter = self.tr("btn_pending")
        self.apply_filters()

    def show_translated(self):
        self.current_filter = self.tr("btn_translated")
        self.apply_filters()

    def export_file(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_no_file"))
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("menu_export"),
            "FULL_Names_Translated.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write("FormID|EDID|FULL\n")
                for row in range(self.table.rowCount()):
                    formid = self.safe_text(row, 0)
                    edid = self.safe_text(row, 1)
                    translated = self.safe_text(row, 3)
                    translated = translated.replace("|", "/")
                    f.write(f"{formid}|{edid}|{translated}\n")
            QMessageBox.information(self, self.tr("Listo"), self.tr("msg_exported"))
        except Exception as e:
            QMessageBox.critical(self, self.tr("error_exporting"), str(e))

    def save_project(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_no_file"))
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("menu_save_project"),
            "skyrim_translation_project.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return

        try:
            data = {"app": "Skyrim AI Translator", "version": "0.6", "records": []}
            for row in range(self.table.rowCount()):
                record = {
                    "formid": self.safe_text(row, 0),
                    "edid": self.safe_text(row, 1),
                    "original": self.safe_text(row, 2),
                    "translated": self.safe_text(row, 3)
                }
                if row in self._row_data:
                    record["signature"] = self._row_data[row].get("signature", "")
                    record["fields"] = self._row_data[row].get("fields", {})
                data["records"].append(record)
                
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, self.tr("Listo"), self.tr("msg_project_saved"))
        except Exception as e:
            QMessageBox.critical(self, self.tr("error_saving_project"), str(e))

    def load_dictionary(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("menu_load_dictionary"),
            "",
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.dictionary = json.load(f)
            QMessageBox.information(self, self.tr("Diccionario"), self.tr("msg_dictionary_loaded").format(len(self.dictionary)))
        except Exception as e:
            QMessageBox.critical(self, self.tr("error_dictionary"), str(e))

    def apply_dictionary(self):
        if not self.dictionary:
            QMessageBox.warning(self, self.tr("msg_warning"), self.tr("msg_no_dictionary"))
            return

        cambios = 0
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            original = self.safe_text(row, 2)
            if original in self.dictionary:
                traduccion = self.dictionary[original]
                self.table.setItem(row, 3, QTableWidgetItem(traduccion))
                self.refresh_row_status(row)
                cambios += 1
        self.table.blockSignals(False)
        self.update_stats()
        QMessageBox.information(self, self.tr("Diccionario"), self.tr("msg_dictionary_applied").format(cambios))

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("menu_open_project"),
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "records" not in data:
                raise Exception("El proyecto no tiene una sección 'records'.")
            rows = []
            for r in data["records"]:
                row_data = {
                    "formid": r.get("formid", ""),
                    "edid": r.get("edid", ""),
                    "original": r.get("original", ""),
                    "translated": r.get("translated", ""),
                    "signature": r.get("signature", ""),
                    "fields": r.get("fields", {"FULL": r.get("original", "")})
                }
                rows.append(row_data)
            self.setup_table(rows)
            self.label_info.setText(
                self.tr("msg_project_loaded").format(
                    os.path.basename(path),
                    len(rows)
                )
            )
        except Exception as e:
            QMessageBox.critical(self, self.tr("error_loading_project"), str(e))

    def clear_cache(self):
        """Limpia toda la caché de traducciones"""
        confirm = QMessageBox.question(
            self,
            "Limpiar caché",
            "¿Estás seguro de que quieres eliminar TODA la caché de traducciones?\n\n"
            "Esto eliminará todas las traducciones guardadas para todos los idiomas.\n"
            "Los textos volverán a su estado original (Pendiente).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.translation_cache = {}
            self.save_translation_cache({})
            
            if self.table.rowCount() > 0:
                self.table.blockSignals(True)
                for row in range(self.table.rowCount()):
                    original = self.safe_text(row, 2)
                    self.table.setItem(row, 3, QTableWidgetItem(original))
                    self.table.setItem(row, 4, QTableWidgetItem(self.tr("status_pending")))
                self.table.blockSignals(False)
                self.update_stats()
                self.apply_filters()
            
            QMessageBox.information(
                self,
                "Caché limpiada",
                "La caché de traducciones ha sido eliminada correctamente.\n\n"
                "Todos los textos han vuelto a estado 'Pendiente'."
            )

    def closeEvent(self, event):
        auto_save = self.settings.get("auto_save", True)
        
        if auto_save and self.table.rowCount() > 0:
            self.save_auto_save()
        
        confirm_exit = self.settings.get("confirm_exit", True)
        if confirm_exit and self.table.rowCount() > 0:
            reply = QMessageBox.question(
                self,
                self.tr("Salir"),
                self.tr("msg_confirm_exit"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkyrimTranslator()
    window.show()
    sys.exit(app.exec())