class Record:
    def __init__(self, formid, edid, original, translated=""):
        self.formid = formid
        self.edid = edid
        self.original = original
        self.translated = translated or original

    @property
    def status(self):
        return "Traducido" if self.original != self.translated else "Pendiente"