"""Log aktivitas (Tantangan D). Disimpan sebagai list of dict."""

from datetime import datetime


class ActivityLog:
    def __init__(self):
        # setiap entri: {"waktu": datetime, "pesan": str}
        self._entri = []

    def catat(self, pesan, waktu=None):
        self._entri.append({"waktu": waktu or datetime.now(), "pesan": pesan})

    def semua(self):
        return list(self._entri)

    @staticmethod
    def format_entri(entri):
        return f"[{entri['waktu']:%Y-%m-%d %H:%M}] {entri['pesan']}"
