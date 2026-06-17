import sys
import json
import os
import pandas as pd

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QMessageBox, QLabel, QLineEdit, QProgressBar
)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QAction

from settings_dialog import SettingsDialog
from ai_manager_dialog import AIManagerDialog
from providers.local_provider import MockProvider, OllamaProvider
from translation_worker import TranslationWorker


SUPPORTED_ENCODINGS = [
    "utf-8-sig",
    "utf-8",
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


class SkyrimTranslator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skyrim AI Translator v0.6")
        self.resize(1400, 800)

        # MENÚ SUPERIOR
        menubar = self.menuBar()

        self.archivo_menu = menubar.addMenu("Archivo")
        self.herramientas_menu = menubar.addMenu("Herramientas")
        self.ia_menu = menubar.addMenu("IA")
        self.ayuda_menu = menubar.addMenu("Ayuda")
        
        # Opciones del menú IA
        self.action_ai_settings = QAction("Configuración IA", self)
        self.ia_menu.addAction(self.action_ai_settings)
        self.action_ai_settings.triggered.connect(self.open_ai_settings)

        self.action_ai_manager = QAction("Descargar / Configurar IA", self)
        self.ia_menu.addAction(self.action_ai_manager)
        self.action_ai_manager.triggered.connect(self.open_ai_manager)

        # TABLA Y ESTADO
        self.table = QTableWidget()
        self.current_encoding = "utf-8"
        self.current_filter = "Todos"
        self.dictionary = {}

        # INFO
        self.label_info = QLabel("Ningún archivo cargado")

        self.lbl_total = QLabel("Total: 0")
        self.lbl_translated = QLabel("Traducidos: 0")
        self.lbl_pending = QLabel("Pendientes: 0")

        # BUSCADOR
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Buscar por FormID, EDID, texto original o traducción..."
        )
        self.search_box.textChanged.connect(self.apply_filters)

        # BOTONES PRINCIPALES
        btn_open = QPushButton("Abrir TXT de xEdit")
        btn_export = QPushButton("Exportar TXT traducido")
        btn_save_project = QPushButton("Guardar proyecto")
        btn_open_project = QPushButton("Abrir proyecto")
        btn_copy_original = QPushButton("Copiar Original → Traducción")
        btn_load_dictionary = QPushButton("Cargar Diccionario")
        btn_apply_dictionary = QPushButton("Aplicar Diccionario")
        btn_translate_selected = QPushButton("Traducir Selección IA")
        btn_translate_visible = QPushButton("Traducir Visibles IA")
        btn_translate_all = QPushButton("Traducir Todo IA")
        
        # BOTONES FILTRO
        btn_all = QPushButton("Todos")
        btn_pending = QPushButton("Pendientes")
        btn_translated = QPushButton("Traducidos")

        # EVENTOS
        btn_open.clicked.connect(self.open_file)
        btn_export.clicked.connect(self.export_file)
        btn_save_project.clicked.connect(self.save_project)
        btn_open_project.clicked.connect(self.open_project)
        btn_copy_original.clicked.connect(self.copy_original_to_translation)
        btn_load_dictionary.clicked.connect(self.load_dictionary)
        btn_apply_dictionary.clicked.connect(self.apply_dictionary)
        btn_translate_selected.clicked.connect(self.translate_selected_ai)
        btn_translate_visible.clicked.connect(self.translate_visible_ai)
        btn_translate_all.clicked.connect(self.translate_all_ai)
        btn_all.clicked.connect(self.show_all)
        btn_pending.clicked.connect(self.show_pending)
        btn_translated.clicked.connect(self.show_translated)

        # LAYOUT BOTONES
        buttons = QHBoxLayout()
        buttons.addWidget(btn_open)
        buttons.addWidget(btn_export)
        buttons.addWidget(btn_save_project)
        buttons.addWidget(btn_open_project)
        buttons.addWidget(btn_copy_original)
        buttons.addWidget(btn_load_dictionary)
        buttons.addWidget(btn_apply_dictionary)
        buttons.addWidget(btn_translate_selected)
        buttons.addWidget(btn_translate_visible)
        buttons.addWidget(btn_translate_all)

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

        btn_cancel_translation = QPushButton("Cancelar traducción")
        btn_cancel_translation.clicked.connect(self.cancel_translation)
        btn_cancel_translation.setVisible(False)

        self.btn_cancel_translation = btn_cancel_translation
        self.translation_worker = None

        # LAYOUT GENERAL
        layout = QVBoxLayout()
        layout.addLayout(buttons)
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

        self.table.itemChanged.connect(self.on_translation_changed)

    def open_ai_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_ai_manager(self):
        dialog = AIManagerDialog(self)
        dialog.exec()

    def load_ai_settings(self):
        path = os.path.join("config", "settings.json")

        if not os.path.exists(path):
            return {
                "provider": "mock",
                "model": "mock-free"
            }

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_ai_provider(self):
        settings = self.load_ai_settings()
        provider = settings.get("provider", "mock")

        if provider == "ollama":
            return OllamaProvider(settings)

        return MockProvider()

    def translate_rows_ai(self, rows):
        if not rows:
            QMessageBox.warning(
                self,
                "Aviso",
                "No hay filas para traducir."
            )
            return

        try:
            provider = self.get_ai_provider()

            originals = {}

            for row in rows:
                original = self.safe_text(row, 2)

                if original:
                    originals[row] = original

            if not originals:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "No hay textos válidos para traducir."
                )
                return

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(originals))

            self.btn_cancel_translation.setVisible(True)

            self.translation_worker = TranslationWorker(
                list(originals.keys()),
                originals,
                provider
            )

            self.translation_worker.progress.connect(
                self.on_translation_progress
            )

            self.translation_worker.row_translated.connect(
                self.on_row_translated
            )

            self.translation_worker.finished.connect(
                self.on_translation_finished
            )

            self.translation_worker.error.connect(
                self.on_translation_error
            )

            self.translation_worker.start()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error IA",
                str(e)
            )

    def on_translation_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def on_row_translated(self, row, translated):
        self.table.blockSignals(True)

        self.table.setItem(
            row,
            3,
            QTableWidgetItem(translated)
        )

        self.table.setItem(
            row,
            4,
            QTableWidgetItem("Traducido")
        )

        self.table.blockSignals(False)

        self.update_stats()

    def on_translation_finished(self, translated_count):
        self.progress_bar.setVisible(False)
        self.btn_cancel_translation.setVisible(False)

        self.update_stats()
        self.apply_filters()

        QMessageBox.information(
            self,
            "Traducción finalizada",
            f"Se tradujeron {translated_count} registro(s)."
        )

    def on_translation_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.btn_cancel_translation.setVisible(False)

        QMessageBox.critical(
            self,
            "Error IA",
            error_message
        )

    def cancel_translation(self):
        if self.translation_worker:
            self.translation_worker.cancel()

            QMessageBox.information(
                self,
                "Cancelando",
                "La traducción se cancelará al terminar el registro actual."
            )

    def translate_selected_ai(self):
        selected = self.table.selectedItems()

        if not selected:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecciona una o varias filas."
            )
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
            "Confirmar",
            f"Vas a traducir {len(rows)} registros. Esto puede tardar bastante.\n\n¿Continuar?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.translate_rows_ai(rows)

    def read_file_with_multiple_encodings(self, path):
        last_error = None

        for enc in SUPPORTED_ENCODINGS:
            try:
                df = pd.read_csv(
                    path,
                    sep="|",
                    dtype=str,
                    encoding=enc,
                    keep_default_na=False
                )

                self.current_encoding = enc
                return df

            except Exception as e:
                last_error = e

        raise Exception(
            "No se pudo leer el archivo con las codificaciones soportadas.\n\n"
            f"Último error:\n{last_error}"
        )

    def setup_table(self, rows):
        self.table.blockSignals(True)

        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "FormID",
            "EDID",
            "Original",
            "Traducción",
            "Estado"
        ])

        self.table.setRowCount(len(rows))

        for row, item in enumerate(rows):
            formid = item["formid"]
            edid = item["edid"]
            original = item["original"]
            translated = item["translated"]

            estado = "Traducido" if original != translated else "Pendiente"

            self.table.setItem(row, 0, QTableWidgetItem(formid))
            self.table.setItem(row, 1, QTableWidgetItem(edid))
            self.table.setItem(row, 2, QTableWidgetItem(original))
            self.table.setItem(row, 3, QTableWidgetItem(translated))
            self.table.setItem(row, 4, QTableWidgetItem(estado))

        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

        self.update_stats()
        self.apply_filters()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo exportado desde xEdit",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )

        if not path:
            return

        try:
            df = self.read_file_with_multiple_encodings(path)

            required_columns = ["FormID", "EDID", "FULL"]

            for col in required_columns:
                if col not in df.columns:
                    raise Exception(
                        "El archivo no tiene el formato correcto.\n\n"
                        "Debe tener esta cabecera:\n"
                        "FormID|EDID|FULL"
                    )

            rows = []

            for _, r in df.iterrows():
                rows.append({
                    "formid": str(r["FormID"]),
                    "edid": str(r["EDID"]),
                    "original": str(r["FULL"]),
                    "translated": str(r["FULL"])
                })

            self.setup_table(rows)

            self.label_info.setText(
                f"Archivo cargado: {path} | Registros: {len(rows)} | Encoding: {self.current_encoding}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al abrir archivo", str(e))

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

        estado = "Traducido" if original != translated else "Pendiente"

        self.table.blockSignals(True)
        self.table.setItem(row, 4, QTableWidgetItem(estado))
        self.table.blockSignals(False)

        self.update_stats()
        self.apply_filters()

    def copy_original_to_translation(self):
        selected = self.table.selectedItems()

        if not selected:
            QMessageBox.information(
                self,
                "Información",
                "Selecciona una o varias filas."
            )
            return

        rows = set()

        for item in selected:
            rows.add(item.row())

        self.table.blockSignals(True)

        for row in rows:
            original = self.safe_text(row, 2)

            self.table.setItem(row, 3, QTableWidgetItem(original))
            self.table.setItem(row, 4, QTableWidgetItem("Traducido"))

        self.table.blockSignals(False)

        self.update_stats()
        self.apply_filters()

    def update_stats(self):
        total = self.table.rowCount()
        translated = 0
        pending = 0

        for row in range(total):
            estado_item = self.table.item(row, 4)

            if not estado_item:
                continue

            estado = estado_item.text()

            if estado == "Traducido":
                translated += 1
            else:
                pending += 1

        self.lbl_total.setText(f"Total: {total}")
        self.lbl_translated.setText(f"Traducidos: {translated}")
        self.lbl_pending.setText(f"Pendientes: {pending}")

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
        if self.current_filter == "Todos":
            return True

        estado_item = self.table.item(row, 4)

        if not estado_item:
            return False

        estado = estado_item.text()

        if self.current_filter == "Pendientes":
            return estado == "Pendiente"

        if self.current_filter == "Traducidos":
            return estado == "Traducido"

        return True

    def apply_filters(self):
        for row in range(self.table.rowCount()):
            visible = (
                self.row_matches_search(row)
                and self.row_matches_status_filter(row)
            )

            self.table.setRowHidden(row, not visible)

    def show_all(self):
        self.current_filter = "Todos"
        self.apply_filters()

    def show_pending(self):
        self.current_filter = "Pendientes"
        self.apply_filters()

    def show_translated(self):
        self.current_filter = "Traducidos"
        self.apply_filters()

    def export_file(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Primero abre un archivo.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo traducido",
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

            QMessageBox.information(
                self,
                "Listo",
                "Archivo exportado correctamente."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    def save_project(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Primero abre un archivo.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar proyecto",
            "skyrim_translation_project.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if not path:
            return

        try:
            data = {
                "app": "Skyrim AI Translator",
                "version": "0.6",
                "records": []
            }

            for row in range(self.table.rowCount()):
                data["records"].append({
                    "formid": self.safe_text(row, 0),
                    "edid": self.safe_text(row, 1),
                    "original": self.safe_text(row, 2),
                    "translated": self.safe_text(row, 3)
                })

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            QMessageBox.information(
                self,
                "Listo",
                "Proyecto guardado correctamente."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al guardar proyecto", str(e))

    def load_dictionary(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar diccionario",
            "",
            "JSON Files (*.json)"
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.dictionary = json.load(f)

            QMessageBox.information(
                self,
                "Diccionario",
                f"Se cargaron {len(self.dictionary)} entradas."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def apply_dictionary(self):
        if not self.dictionary:
            QMessageBox.warning(
                self,
                "Aviso",
                "Primero carga un diccionario."
            )
            return

        cambios = 0

        self.table.blockSignals(True)

        for row in range(self.table.rowCount()):
            original = self.safe_text(row, 2)

            if original in self.dictionary:
                traduccion = self.dictionary[original]

                self.table.setItem(row, 3, QTableWidgetItem(traduccion))
                self.table.setItem(row, 4, QTableWidgetItem("Traducido"))

                cambios += 1

        self.table.blockSignals(False)

        self.update_stats()

        QMessageBox.information(
            self,
            "Diccionario",
            f"{cambios} registros actualizados."
        )

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir proyecto",
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
                rows.append({
                    "formid": r.get("formid", ""),
                    "edid": r.get("edid", ""),
                    "original": r.get("original", ""),
                    "translated": r.get("translated", "")
                })

            self.setup_table(rows)

            self.label_info.setText(
                f"Proyecto cargado: {path} | Registros: {len(rows)}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al abrir proyecto", str(e))


def apply_dark_theme(app):
    app.setStyleSheet("""
    QMainWindow {
        background-color: #1e1e1e;
    }

    QWidget {
        background-color: #1e1e1e;
        color: #e6e6e6;
        font-size: 13px;
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
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    window = SkyrimTranslator()
    window.show()

    sys.exit(app.exec())