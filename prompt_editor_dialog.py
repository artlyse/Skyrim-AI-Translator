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
        return """IMPORTANT: You are an English to {language} translator for Skyrim game mods.

CRITICAL RULES (follow strictly):
1. ONLY return the translation in {language}. Return NOTHING else.
2. DO NOT include the original text, any prefixes, or explanations.
3. DO NOT add Chinese, Japanese, or any other language characters.
4. DO NOT add any text that is not a direct translation.
5. Keep proper names (like Whiterun, FUS RO DAH) unchanged.
6. Keep codes and abbreviations (like def, FX, DLC) unchanged.
7. Use natural {language} for game terms.
8. Translate literally, not creatively.

CORRECT EXAMPLES:
Input: "Blood Decal Large" → Output: "Mancha de sangre grande"
Input: "Bleed left arm" → Output: "Sangrado del brazo izquierdo"
Input: "Armor Explosion def" → Output: "Explosión de armadura"
Input: "Slow Time" → Output: "Tiempo ralentizado"

INCORRECT EXAMPLES (DO NOT DO THESE):
Input: "Blood Decal Large" → Output: "Blood Decal Large" (WRONG - must translate)
Input: "Bleed left arm" → Output: "Sangrado del brazo izquierdo左侧" (WRONG - contains Chinese)
Input: "Slow Time" → Output: "Slowing Time" (WRONG - changed wording)

Text to translate (ONLY translate this exact text):
{text}

Translation ({language}):"""
    
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