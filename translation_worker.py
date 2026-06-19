import threading
import time
import re
from PyQt6.QtCore import QObject, pyqtSignal


class TranslationWorker(QObject, threading.Thread):
    progress = pyqtSignal(int, int)
    row_translated = pyqtSignal(int, str, str)  # row, original, translated_text
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    cache_updated = pyqtSignal(str, str, str)  # original, language, translated

    def __init__(self, rows, texts, provider, cache, dictionary, target_language, force_retranslate=False, cache_same_as_original=True):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.rows = rows
        self.texts = texts
        self.provider = provider
        self.cache = cache
        self.dictionary = dictionary
        self.target_language = target_language
        self.force_retranslate = force_retranslate
        self.cache_same_as_original = cache_same_as_original
        self.total = len(rows)
        self.current = 0
        self.translated_count = 0
        self._is_cancelled = False
        self.batch_size = 10
        self.batch_counter = 0

        self.protected_terms = {
            'PMS', 'DLC', 'FX', 'NPC', 'PC', 'UI', 'FPS', 'RPG', 'PVP', 'PVE', 'MMO',
            'ID', 'API', 'GUI', 'RAM', 'CPU', 'GPU', 'HDD', 'SSD', 'USB', 'HDMI',
            'URL', 'HTTP', 'HTTPS', 'FTP', 'SSH', 'SSL', 'TLS', 'DNS', 'IP', 'MAC',
            'BIOS', 'CMOS', 'PCI', 'AGP', 'SATA', 'IDE', 'SCSI', 'RAID', 'SAN',
            'NAS', 'LAN', 'WAN', 'VPN', 'RDP', 'VNC', 'SFTP', 'SMTP', 'POP3',
            'IMAP', 'AES', 'RSA', 'SHA', 'MD5', 'PUB', 'PRV', 'DEV', 'TEST',
            'REF', 'TMP', 'VAR', 'FUNC', 'PROC', 'EVAL', 'SYNC', 'ASYNC'
        }

    def is_only_protected_code(self, original):
        text = (original or '').strip()
        if not text:
            return False
        if text.lower() in {'def', 'tmp', 'ref', 'var'}:
            return True
        if text.upper() in self.protected_terms:
            return True
        if re.fullmatch(r'[A-Z0-9_\-]+', text) and any(t in text for t in self.protected_terms):
            return True
        return False

    def clean_translation(self, text, original):
        if not text:
            return original

        text = str(text).replace('\ufeff', '').strip()
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        text = re.sub(r'^["“”\'`]+|["“”\'`]+$', '', text).strip()

        markers = [
            r'Translation\s*\([^)]*\)\s*:', r'Translation\s*:', r'Traducci[oó]n\s*\([^)]*\)\s*:',
            r'Traducci[oó]n\s*:', r'Resultado\s*:', r'Result\s*:', r'Output\s*:',
            r'Salida\s*:', r'Response\s*:', r'Respuesta\s*(?:en\s+espa[nñ]ol)?\s*:',
            r'Correct translation\s*\([^)]*\)\s*:', r'Correction in Spanish\s*:'
        ]
        for marker in markers:
            matches = list(re.finditer(marker, text, flags=re.I))
            if matches:
                text = text[matches[-1].end():].strip()

        # Corta explicaciones típicas que el modelo añade después de la traducción.
        # Incluye casos como: (Remember...), Notes:, This translation keeps..., KEEP as is, etc.
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

        if self.target_language != 'Japanese':
            text = re.sub(r'[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]+', '', text)
            text = re.sub(r'[^\w\s.,;:!?¿¡()\-\'"/ÁÉÍÓÚÜÑáéíóúüñ]+', '', text, flags=re.UNICODE)

        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\s+([.,;:!?])', r'\1', text).strip()
        text = text.strip(' "“”`')
        return text if text else original

    def get_from_cache(self, original):
        if self.force_retranslate:
            return None
        lang_cache = self.cache.get(original)
        if isinstance(lang_cache, dict):
            return lang_cache.get(self.target_language)
        if self.target_language == 'Spanish' and isinstance(lang_cache, str):
            return lang_cache
        return None

    def run(self):
        try:
            for original, row in self.rows:
                if self._is_cancelled:
                    break
                if not original:
                    self.current += 1
                    continue

                translated = None

                if not self.force_retranslate and original in self.dictionary:
                    translated = self.clean_translation(self.dictionary[original], original)
                else:
                    cached = self.get_from_cache(original)
                    if cached:
                        translated = self.clean_translation(cached, original)

                if translated is None:
                    try:
                        if self.is_only_protected_code(original):
                            translated = original
                        else:
                            translated = self.provider.translate(original)
                            translated = self.clean_translation(translated, original)

                        if translated and (translated != original or self.cache_same_as_original):
                            self.cache_updated.emit(original, self.target_language, translated)
                    except Exception as e:
                        self.error.emit(f"Error traduciendo '{original}': {str(e)}")
                        translated = original

                self.row_translated.emit(row, original, translated)
                self.translated_count += 1
                self.current += 1

                self.batch_counter += 1
                if self.batch_counter >= self.batch_size:
                    self.progress.emit(self.current, self.total)
                    self.batch_counter = 0
                    time.sleep(0.005)

            self.progress.emit(self.total, self.total)
            self.finished.emit(self.translated_count)
        except Exception as e:
            self.error.emit(f"Error en TranslationWorker: {str(e)}")

    def cancel(self):
        self._is_cancelled = True
