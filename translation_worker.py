from PyQt6.QtCore import QThread, pyqtSignal


class TranslationWorker(QThread):
    progress = pyqtSignal(int, int)
    row_translated = pyqtSignal(int, str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    cache_updated = pyqtSignal(dict)  # Nueva señal para actualizar el caché

    def __init__(self, rows, originals, provider, cache=None):
        super().__init__()

        self.rows = rows
        self.originals = originals
        self.provider = provider
        self.cache = cache if cache is not None else {}  # Si no hay caché, usar dict vacío
        self.cancelled = False

    def run(self):
        translated_count = 0
        total = len(self.rows)
        cache_modified = False  # Para saber si hubo cambios en el caché

        try:
            for index, row in enumerate(self.rows):
                if self.cancelled:
                    break

                original = self.originals.get(row, "")

                if original:
                    # Verificar si ya está en caché
                    if original in self.cache:
                        translated = self.cache[original]
                    else:
                        # Traducir y guardar en caché
                        translated = self.provider.translate(original)
                        self.cache[original] = translated
                        cache_modified = True
                        
                        # Emitir señal para guardar el caché actualizado
                        self.cache_updated.emit(self.cache)

                    self.row_translated.emit(row, translated)
                    translated_count += 1

                self.progress.emit(index + 1, total)

            # Si hubo cambios en el caché, guardar una última vez
            if cache_modified:
                self.cache_updated.emit(self.cache)

            self.finished.emit(translated_count)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self.cancelled = True