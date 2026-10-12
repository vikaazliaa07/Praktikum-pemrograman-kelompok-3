"""Statistik peminjaman (Tantangan B). Hanya membaca data transaksi."""

from collections import Counter


class StatistikService:
    def __init__(self, transaksi_service):
        self._trx = transaksi_service

    def alat_terpopuler(self, n=5):
        """[(kode, nama, total_unit_dipinjam)] terurut dari yang terbanyak."""
        jumlah, nama = Counter(), {}
        for t in self._trx.semua():
            for item in t.items.values():
                jumlah[item.kode] += item.jumlah
                nama[item.kode] = item.nama_alat
        urut = sorted(jumlah.items(), key=lambda kv: (-kv[1], kv[0]))
        return [(kode, nama[kode], total) for kode, total in urut[:n]]

    def mahasiswa_teraktif(self, n=5):
        """[(nim, nama, jumlah_transaksi)] terurut dari yang terbanyak."""
        jumlah, nama = Counter(), {}
        for t in self._trx.semua():
            jumlah[t.nim] += 1
            nama[t.nim] = t.nama_peminjam
        urut = sorted(jumlah.items(), key=lambda kv: (-kv[1], kv[0]))
        return [(nim, nama[nim], total) for nim, total in urut[:n]]

    def jumlah_selesai(self):
        return len(self._trx.selesai())

    def jumlah_aktif(self):
        return len(self._trx.aktif())
