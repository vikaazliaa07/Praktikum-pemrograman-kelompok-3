"""Class Peralatan: satu objek mewakili satu unit alat fisik (kode unik)."""

KONDISI_VALID = ("baik", "rusak ringan", "rusak berat")


class Peralatan:
    def __init__(self, kode_alat, nama_alat, kategori, kondisi="baik"):
        self.kode_alat = kode_alat
        self.nama_alat = nama_alat
        self.kategori = kategori          # String bebas -> kategori baru tanpa ubah struktur
        self.kondisi = self._validasi_kondisi(kondisi)
        self.sedang_dipinjam = False

    @staticmethod
    def _validasi_kondisi(kondisi):
        nilai = str(kondisi).strip().lower()
        if nilai not in KONDISI_VALID:
            raise ValueError(f"Kondisi harus salah satu dari: {', '.join(KONDISI_VALID)}.")
        return nilai

    def cek_ketersediaan(self):
        """Tersedia hanya bila kondisi baik DAN tidak sedang dipinjam (Aturan 1 & 5)."""
        return self.kondisi == "baik" and not self.sedang_dipinjam

    def status_teks(self):
        if self.sedang_dipinjam:
            return "dipinjam"
        return "tersedia" if self.kondisi == "baik" else self.kondisi

    def pinjam(self):
        if not self.cek_ketersediaan():
            raise ValueError(f"Alat {self.kode_alat} ({self.nama_alat}) tidak tersedia: {self.status_teks()}.")
        self.sedang_dipinjam = True

    def terima_kembali(self, kondisi):
        """Dipanggil saat alat dikembalikan; alat rusak otomatis tidak tersedia."""
        if not self.sedang_dipinjam:
            raise ValueError(f"Alat {self.kode_alat} tidak sedang dipinjam.")
        self.kondisi = self._validasi_kondisi(kondisi)
        self.sedang_dipinjam = False

    def ubah_kondisi(self, kondisi):
        if self.sedang_dipinjam:
            raise ValueError(f"Kondisi alat {self.kode_alat} tidak dapat diubah saat sedang dipinjam.")
        self.kondisi = self._validasi_kondisi(kondisi)

    def tampilkan_info(self):
        print(f"  [{self.kode_alat}] {self.nama_alat} | kategori: {self.kategori} "
              f"| kondisi: {self.kondisi} | status: {self.status_teks()}")
