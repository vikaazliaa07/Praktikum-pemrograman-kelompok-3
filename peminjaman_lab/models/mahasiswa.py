"""Class Mahasiswa: data mahasiswa dan jumlah transaksi aktifnya."""


class Mahasiswa:
    MAKS_TRANSAKSI_AKTIF = 2  # Aturan 2

    def __init__(self, nim, nama, no_hp):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        self.jumlah_transaksi_aktif = 0

    def tampilkan_info(self):
        status = "aktif meminjam" if self.punya_transaksi_aktif() else "tidak meminjam"
        print(f"  NIM: {self.nim} | Nama: {self.nama} | HP: {self.no_hp} "
              f"| Transaksi aktif: {self.jumlah_transaksi_aktif} ({status})")

    def bisa_meminjam(self):
        """True bila belum mencapai batas transaksi aktif."""
        return self.jumlah_transaksi_aktif < self.MAKS_TRANSAKSI_AKTIF

    def punya_transaksi_aktif(self):
        return self.jumlah_transaksi_aktif > 0

    def tambah_transaksi_aktif(self):
        self.jumlah_transaksi_aktif += 1

    def kurangi_transaksi_aktif(self):
        if self.jumlah_transaksi_aktif > 0:
            self.jumlah_transaksi_aktif -= 1
