from PyQt6.QtCore import QThread, pyqtSignal


class TranslationWorker(QThread):
    progress = pyqtSignal(int, int)
    row_translated = pyqtSignal(int, str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, rows, originals, provider):
        super().__init__()

        self.rows = rows
        self.originals = originals
        self.provider = provider
        self.cancelled = False

    def run(self):
        translated_count = 0
        total = len(self.rows)

        try:
            for index, row in enumerate(self.rows):
                if self.cancelled:
                    break

                original = self.originals.get(row, "")

                if original:
                    translated = self.provider.translate(original)
                    self.row_translated.emit(row, translated)
                    translated_count += 1

                self.progress.emit(index + 1, total)

            self.finished.emit(translated_count)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self.cancelled = True