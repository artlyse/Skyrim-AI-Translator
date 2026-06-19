import threading
import time
import re
from PyQt6.QtCore import QObject, pyqtSignal


class TranslationWorker(QObject, threading.Thread):
    progress = pyqtSignal(int, int)  # current, total
    row_translated = pyqtSignal(int, str)  # row, translated_text
    finished = pyqtSignal(int)  # total_translated
    error = pyqtSignal(str)
    cache_updated = pyqtSignal(str, str, str)  # original, language, translated

    def __init__(self, rows, texts, provider, cache, dictionary, target_language):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        
        self.rows = rows
        self.texts = texts
        self.provider = provider
        self.cache = cache
        self.dictionary = dictionary
        self.target_language = target_language
        self.total = len(rows)
        self.current = 0
        self.translated_count = 0
        self._is_cancelled = False
        
        self.batch_size = 5
        self.batch_counter = 0

    def clean_translation(self, text, original):
        """Limpia la traducción según el idioma"""
        if not text:
            return original
        
        # Para japonés, NO eliminar caracteres nativos
        if self.target_language == "Japanese":
            # Solo limpiar espacios y caracteres de control
            text = re.sub(r'\s+', ' ', text).strip()
            # Eliminar prefijos comunes
            prefixes = [
                "Translation:", "Traducción:", "Resultado:", 
                "Result:", "Output:", "Salida:", "Response:", 
                "Respuesta:", "Translation", "Traducción"
            ]
            for prefix in prefixes:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
            
            # Verificar que no sea solo romaji
            # Si contiene caracteres latinos pero no japoneses, puede ser romaji
            japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')
            if not japanese_pattern.search(text):
                # Si no tiene caracteres japoneses, podría ser romaji - marcar como pendiente
                return original
            
            return text
        
        # Para otros idiomas, limpiar caracteres extraños
        clean_pattern = re.compile(r'[^\w\s.,;:!?¿¡()\-\'"]+', re.UNICODE)
        text = clean_pattern.sub('', text)
        
        prefixes = [
            "Translation:", "Traducción:", "Resultado:", 
            "Result:", "Output:", "Salida:", "Response:", 
            "Respuesta:", "Translation", "Traducción"
        ]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        if not text or text.strip() == "":
            return original
        
        return text

    def run(self):
        try:
            for row in self.rows:
                if self._is_cancelled:
                    break
                
                original = self.texts.get(row, "")
                
                if not original:
                    self.current += 1
                    continue
                
                translated = None
                
                if original in self.dictionary:
                    translated = self.dictionary[original]
                else:
                    if original in self.cache:
                        lang_cache = self.cache[original]
                        if isinstance(lang_cache, dict):
                            translated = lang_cache.get(self.target_language)
                
                if translated is None:
                    try:
                        translated = self.provider.translate(original)
                        translated = self.clean_translation(translated, original)
                        
                        if translated and translated != original:
                            self.cache_updated.emit(original, self.target_language, translated)
                    except Exception as e:
                        self.error.emit(f"Error traduciendo fila {row}: {str(e)}")
                        translated = original
                
                if translated is not None:
                    self.row_translated.emit(row, translated)
                    self.translated_count += 1
                
                self.current += 1
                
                self.batch_counter += 1
                if self.batch_counter >= self.batch_size:
                    self.progress.emit(self.current, self.total)
                    self.batch_counter = 0
                    time.sleep(0.01)
            
            self.progress.emit(self.total, self.total)
            self.finished.emit(self.translated_count)
            
        except Exception as e:
            self.error.emit(f"Error en TranslationWorker: {str(e)}")

    def cancel(self):
        self._is_cancelled = True
        self.finished.emit(self.translated_count)