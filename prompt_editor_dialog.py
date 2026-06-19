import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QMessageBox
)


class PromptEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Editor de Prompt - Instrucciones para IA")
        self.resize(700, 500)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Instrucciones
        info_label = QLabel(
            "📝 Edita las instrucciones que se enviarán a la IA para las traducciones.\n"
            "Variables disponibles:\n"
            "  {language} - Idioma de destino\n"
            "  {text} - Texto a traducir\n\n"
            "⚠️ IMPORTANTE: Asegúrate de que la IA solo devuelva la traducción en el idioma destino,\n"
            "sin caracteres chinos, japoneses u otros caracteres extraños."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Editor de texto
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("Escribe aquí el prompt para la IA...")
        layout.addWidget(self.prompt_editor)
        
        # Cargar prompt actual
        self.load_prompt()
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_reset = QPushButton("🔄 Restaurar predeterminado")
        btn_save = QPushButton("💾 Guardar prompt")
        btn_close = QPushButton("❌ Cerrar")
        
        btn_reset.clicked.connect(self.reset_prompt)
        btn_save.clicked.connect(self.save_prompt)
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_prompt_path(self):
        return os.path.join("config", "prompt_template.txt")
    
    def get_default_prompt(self):
        """Prompt mejorado que evita caracteres chinos"""
        return """You are a strict Skyrim mod text translator from English to {language}.

RETURN ONLY THE FINAL TRANSLATION.
Do not explain anything.
Do not add notes.
Do not add parentheses explaining why something was kept.
Do not write phrases like: Note, Remember, Please note, no translation required, keep as is, output, result, translation.

Rules:
1. Translate the meaning naturally into {language}.
2. Keep technical codes, IDs, acronyms and suffixes unchanged when needed: MC, DLC, FX, NPC, L, R, def.
3. Do not keep the whole phrase in English just because it contains a code.
4. Do not add context or extra words that are not part of the original text.
5. If a word truly should stay unchanged, return only that word/text, without explanation.
6. Use normal Spanish game terminology when {language} is Spanish.

Examples:
Blood Decal Large -> Mancha de sangre grande
Bleed left arm -> Sangrado del brazo izquierdo
Armor Explosion def -> Explosión de armadura def
MC_Gore Troll -> MC_Gore Trol
Slow Time -> Ralentizar tiempo

Text:
{text}

Final translation in {language}:"""

    def load_prompt(self):
        """Carga el prompt desde archivo o usa el predeterminado"""
        prompt_path = self.get_prompt_path()
        
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt = f.read().strip()
                    if prompt:
                        self.prompt_editor.setText(prompt)
                        return
        except Exception:
            pass
        
        # Si no existe o está vacío, usar predeterminado
        self.prompt_editor.setText(self.get_default_prompt())
    
    def save_prompt(self):
        """Guarda el prompt en archivo"""
        prompt_text = self.prompt_editor.toPlainText().strip()
        
        if not prompt_text:
            QMessageBox.warning(
                self,
                "Prompt vacío",
                "El prompt no puede estar vacío. Se restaurará el predeterminado."
            )
            self.prompt_editor.setText(self.get_default_prompt())
            return
        
        try:
            os.makedirs("config", exist_ok=True)
            
            with open(self.get_prompt_path(), "w", encoding="utf-8") as f:
                f.write(prompt_text)
            
            QMessageBox.information(
                self,
                "Prompt guardado",
                "El prompt se ha guardado correctamente.\n\n"
                "Las próximas traducciones usarán este prompt."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar el prompt:\n{str(e)}"
            )
    
    def reset_prompt(self):
        """Restaura el prompt predeterminado"""
        confirm = QMessageBox.question(
            self,
            "Restaurar prompt",
            "¿Estás seguro de que quieres restaurar el prompt predeterminado?\n"
            "Perderás cualquier personalización.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.prompt_editor.setText(self.get_default_prompt())
            
            # Guardar automáticamente
            try:
                os.makedirs("config", exist_ok=True)
                with open(self.get_prompt_path(), "w", encoding="utf-8") as f:
                    f.write(self.get_default_prompt())
                
                QMessageBox.information(
                    self,
                    "Prompt restaurado",
                    "El prompt predeterminado ha sido restaurado."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo restaurar el prompt:\n{str(e)}"
                )