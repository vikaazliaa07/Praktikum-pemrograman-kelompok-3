"""PeralatanManager: CRUD data alat + pencarian + daftar tersedia/dipinjam/rusak."""
from models.peralatan import Peralatan


class PeralatanManager:
    def __init__(self):
        self.daftar_alat = {}

    def tambah_alat(self, kode, nama, kategori, kondisi="baik"):
        kode, nama, kategori = kode.strip(), nama.strip(), kategori.strip().lower()
        if not kode or not nama or not kategori:
            raise ValueError("Kode, nama, dan kategori tidak boleh kosong.")
        if kode in self.daftar_alat:
            raise ValueError(f"Kode alat {kode} sudah terdaftar.")
        alat = Peralatan(kode, nama, kategori, kondisi)
        self.daftar_alat[kode] = alat
        return alat

    def edit_alat(self, kode, nama=None, kategori=None, kondisi=None):
        alat = self.ambil_alat(kode)
        if nama is not None and nama.strip():
            alat.nama_alat = nama.strip()
        if kategori is not None and kategori.strip():
            alat.kategori = kategori.strip().lower()
        if kondisi is not None and kondisi.strip():
            alat.ubah_kondisi(kondisi)
        return alat

    def hapus_alat(self, kode):
        alat = self.ambil_alat(kode)
        if alat.sedang_dipinjam:                 # Aturan 6
            raise ValueError(f"Alat {kode} masih tercatat di transaksi aktif; tidak dapat dihapus.")
        del self.daftar_alat[kode.strip()]

    def cari_alat(self, keyword):
        """Pencarian fleksibel (Tantangan A): kode, sebagian nama, atau kategori."""
        kw = keyword.strip().lower()
        return [a for a in self.daftar_alat.values()
                if kw in a.kode_alat.lower() or kw in a.nama_alat.lower() or kw in a.kategori.lower()]

    def ambil_alat(self, kode):
        alat = self.daftar_alat.get(kode.strip())
        if alat is None:
            raise ValueError(f"Alat dengan kode {kode} tidak ditemukan.")
        return alat

    @staticmethod
    def _cetak(daftar, kosong):
        if not daftar:
            print(f"  ({kosong})")
        for a in daftar:
            a.tampilkan_info()
        return daftar

    def tampilkan_semua_alat(self, daftar=None):
        daftar = list(self.daftar_alat.values()) if daftar is None else daftar
        return self._cetak(daftar, "tidak ada data alat")

    def tampilkan_alat_tersedia(self):
        return self._cetak([a for a in self.daftar_alat.values() if a.cek_ketersediaan()],
                           "tidak ada alat tersedia")

    def tampilkan_alat_dipinjam(self):
        return self._cetak([a for a in self.daftar_alat.values() if a.sedang_dipinjam],
                           "tidak ada alat yang sedang dipinjam")

    def tampilkan_alat_rusak(self):
        return self._cetak([a for a in self.daftar_alat.values() if a.kondisi != "baik"],
                           "tidak ada alat rusak")
