"""Perakit (composition root): membuat semua service dan menghubungkannya."""

from .alat_service import AlatService
from .log import ActivityLog
from .mahasiswa_service import MahasiswaService
from .statistik_service import StatistikService
from .transaksi_service import TransaksiService


class SistemLab:
    def __init__(self):
        self.log = ActivityLog()
        self.mahasiswa = MahasiswaService(self.log)
        self.alat = AlatService(self.log)
        self.transaksi = TransaksiService(self.mahasiswa, self.alat, self.log)
        self.statistik = StatistikService(self.transaksi)
