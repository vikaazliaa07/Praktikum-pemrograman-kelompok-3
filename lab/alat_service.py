"""Pengelolaan data alat, kategori, pencarian, dan pemeliharaan."""

from .exceptions import (AturanBisnisError, DataDuplikatError,
                         DataTidakDitemukanError, ValidasiError)
from .konfigurasi import KATEGORI_AWAL
from .models import Alat
from .validasi import bilangan_positif, wajib_isi


class AlatService:
    def __init__(self, log):
        self._data = {}                      # kode -> Alat
        self._kategori = list(KATEGORI_AWAL)  # kategori = data, bukan class
        self._log = log

    # ---------- kategori ----------
    def daftar_kategori(self):
        return list(self._kategori)

    def tambah_kategori(self, nama):
        """Kategori baru cukup ditambahkan sebagai data; kode lain tidak berubah."""
        nama = wajib_isi(nama, "Nama kategori").lower()
        if nama in self._kategori:
            raise DataDuplikatError(f"Kategori '{nama}' sudah ada.")
        self._kategori.append(nama)
        self._log.catat(f"Kategori '{nama}' ditambahkan")
        return nama

    def _validasi_kategori(self, kategori):
        kategori = wajib_isi(kategori, "Kategori").lower()
        if kategori not in self._kategori:
            raise ValidasiError(
                f"Kategori '{kategori}' belum terdaftar. "
                f"Pilihan: {', '.join(self._kategori)}.")
        return kategori

    # ---------- CRUD ----------
    def tambah(self, kode, nama, kategori, jumlah):
        kode = wajib_isi(kode, "Kode alat").upper()
        nama = wajib_isi(nama, "Nama alat")
        kategori = self._validasi_kategori(kategori)
        bilangan_positif(jumlah, "Jumlah")
        if kode in self._data:
            raise DataDuplikatError(f"Kode alat {kode} sudah terdaftar.")
        alat = Alat(kode, nama, kategori, jumlah)
        self._data[kode] = alat
        self._log.catat(f"Alat {kode} ({nama}) ditambahkan, {jumlah} unit")
        return alat

    def ambil(self, kode):
        try:
            return self._data[str(kode).strip().upper()]
        except KeyError:
            raise DataTidakDitemukanError(
                f"Alat dengan kode {kode} tidak ditemukan.") from None

    def edit(self, kode, nama=None, kategori=None, jumlah_total=None):
        alat = self.ambil(kode)
        nama_baru = wajib_isi(nama, "Nama alat") if nama is not None else alat.nama
        kategori_baru = (self._validasi_kategori(kategori)
                         if kategori is not None else alat.kategori)
        if jumlah_total is not None:
            bilangan_positif(jumlah_total, "Jumlah total")
            alat.ubah_total(jumlah_total)
        alat.nama, alat.kategori = nama_baru, kategori_baru
        self._log.catat(f"Alat {alat.kode} diubah")
        return alat

    def hapus(self, kode):
        """Aturan 6: tidak boleh dihapus jika tercatat di transaksi aktif."""
        alat = self.ambil(kode)
        if alat.transaksi_aktif:
            daftar = ", ".join(sorted(alat.transaksi_aktif))
            raise AturanBisnisError(
                f"Alat {alat.kode} tidak dapat dihapus: masih tercatat pada "
                f"transaksi aktif ({daftar}).")
        del self._data[alat.kode]
        self._log.catat(f"Alat {alat.kode} dihapus")

    # ---------- pencarian (Tantangan A) ----------
    def cari(self, kode=None, nama=None, kategori=None):
        """Filter opsional; semua filter yang diisi harus cocok (AND).

        kode/nama: pencocokan sebagian, tidak peka huruf besar-kecil.
        kategori: pencocokan sebagian pada nama kategori.
        """
        filters = {
            "kode": (kode or "").strip().lower(),
            "nama": (nama or "").strip().lower(),
            "kategori": (kategori or "").strip().lower(),
        }
        if not any(filters.values()):
            raise ValidasiError("Isi minimal satu kriteria pencarian.")
        hasil = []
        for a in self.semua():
            if (filters["kode"] in a.kode.lower()
                    and filters["nama"] in a.nama.lower()
                    and filters["kategori"] in a.kategori.lower()):
                hasil.append(a)
        return hasil

    # ---------- daftar/laporan ----------
    def semua(self):
        return sorted(self._data.values(), key=lambda a: a.kode)

    def tersedia(self):
        return [a for a in self.semua() if a.tersedia > 0]

    def sedang_dipinjam(self):
        return [a for a in self.semua() if a.dipinjam > 0]

    def rusak(self):
        """Alat yang punya unit rusak, termasuk yang sedang dipelihara."""
        return [a for a in self.semua()
                if a.jumlah_rusak + a.pemeliharaan > 0]

    def dalam_pemeliharaan(self):
        return [a for a in self.semua() if a.pemeliharaan > 0]

    # ---------- pemeliharaan (Tantangan C) ----------
    def mulai_pemeliharaan(self, kode, jumlah, dari):
        alat = self.ambil(kode)
        bilangan_positif(jumlah, "Jumlah")
        alat.mulai_pemeliharaan(jumlah, dari)
        self._log.catat(
            f"{jumlah} unit {alat.nama} ({dari.value}) masuk pemeliharaan")

    def selesai_pemeliharaan(self, kode, jumlah):
        alat = self.ambil(kode)
        bilangan_positif(jumlah, "Jumlah")
        alat.selesai_pemeliharaan(jumlah)
        self._log.catat(
            f"{jumlah} unit {alat.nama} selesai diperbaiki dan kembali tersedia")
