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
        
        self.rows = rows  # Lista de (original, row) para textos únicos
        self.texts = texts  # {original: original} para búsqueda rápida
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
        
        # Lista de siglas y abreviaturas que NO deben traducirse
        self.protected_terms = [
            'PMS', 'DLC', 'FX', 'NPC', 'PC', 'UI', 'FPS', 'RPG', 
            'PVP', 'PVE', 'MMO', 'ID', 'API', 'GUI', 'RAM', 'CPU',
            'GPU', 'HDD', 'SSD', 'USB', 'HDMI', 'URL', 'HTTP',
            'HTTPS', 'FTP', 'SSH', 'SSL', 'TLS', 'DNS', 'IP',
            'MAC', 'BIOS', 'CMOS', 'PCI', 'AGP', 'SATA', 'IDE',
            'SCSI', 'RAID', 'SAN', 'NAS', 'LAN', 'WAN', 'VPN',
            'RDP', 'VNC', 'SSH', 'SFTP', 'FTP', 'SMTP', 'POP3',
            'IMAP', 'SSL', 'TLS', 'AES', 'RSA', 'SHA', 'MD5',
            'PUB', 'PRV', 'DEV', 'TEST', 'REF', 'TMP', 'VAR',
            'FUNC', 'PROC', 'EVAL', 'SYNC', 'ASYNC', 'DEF'
        ]

    def clean_translation(self, text, original):
        """Limpia la traducción según el idioma y protege siglas"""
        if not text:
            return original
        
        # Verificar si el texto original contiene siglas protegidas
        # Si el texto original es una sigla o contiene siglas, mantenerlo intacto
        for term in self.protected_terms:
            if term in original:
                # Si el texto original contiene la sigla, devolver el original
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
            japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')
            if not japanese_pattern.search(text):
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
        
        # Si la traducción está vacía o es igual al original con cambios mínimos, devolver original
        if not text or text.strip() == "":
            return original
        
        # Verificar si la traducción contiene caracteres extraños
        if any(ord(c) > 0xFFFF for c in text):
            return original
        
        return text

    def run(self):
        try:
            for original, row in self.rows:
                if self._is_cancelled:
                    break
                
                if not original:
                    self.current += 1
                    continue
                
                translated = None
                
                # 1. Verificar en diccionario (prioridad máxima)
                if original in self.dictionary:
                    translated = self.dictionary[original]
                else:
                    # 2. Verificar en caché multidioma
                    if original in self.cache:
                        lang_cache = self.cache[original]
                        if isinstance(lang_cache, dict):
                            translated = lang_cache.get(self.target_language)
                
                # 3. Si no está en caché ni diccionario, traducir con IA
                if translated is None:
                    try:
                        # Verificar si el texto contiene siglas protegidas
                        is_protected = False
                        for term in self.protected_terms:
                            if term in original:
                                is_protected = True
                                break
                        
                        if is_protected:
                            # Si contiene siglas, no traducir
                            translated = original
                        else:
                            translated = self.provider.translate(original)
                            translated = self.clean_translation(translated, original)
                            
                            # Guardar en caché multidioma
                            if translated and translated != original:
                                self.cache_updated.emit(original, self.target_language, translated)
                            else:
                                translated = original
                    except Exception as e:
                        self.error.emit(f"Error traduciendo '{original}': {str(e)}")
                        translated = original
                
                # Emitir señal de fila traducida
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