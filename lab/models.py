"""Entitas domain: Mahasiswa, Alat, ItemPeminjaman, PengembalianRecord, Transaksi.

Prinsip: aturan yang hanya menyangkut satu objek (mis. perubahan stok alat)
ditempatkan di class objek itu sendiri, supaya stok tidak bisa diubah
sembarangan dari luar dan selalu konsisten.
"""

from datetime import timedelta
from enum import Enum

from .exceptions import AturanBisnisError


class KondisiAlat(Enum):
    BAIK = "baik"
    RUSAK_RINGAN = "rusak ringan"
    RUSAK_BERAT = "rusak berat"


class StatusTransaksi(Enum):
    DIPINJAM = "dipinjam"
    SEBAGIAN = "sebagian dikembalikan"
    SELESAI = "selesai"


class Mahasiswa:
    def __init__(self, nim, nama, no_hp):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        # id transaksi yang belum selesai; dikelola oleh TransaksiService
        self.transaksi_aktif = set()

    @property
    def jumlah_transaksi_aktif(self):
        return len(self.transaksi_aktif)

    @property
    def status_peminjaman(self):
        n = self.jumlah_transaksi_aktif
        return f"aktif ({n} transaksi)" if n else "tidak aktif"


class Alat:
    """Satu jenis alat beserta stok per kondisi.

    Invarian: total = tersedia + dipinjam + rusak_ringan + rusak_berat
    + pemeliharaan. Semua perubahan stok harus lewat method di class ini.
    """

    def __init__(self, kode, nama, kategori, jumlah_total):
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.tersedia = jumlah_total
        self.dipinjam = 0
        self.rusak_ringan = 0
        self.rusak_berat = 0
        self.pemeliharaan = 0
        # id transaksi aktif yang memuat alat ini; dikelola TransaksiService
        self.transaksi_aktif = set()

    # ---- informasi turunan ----
    @property
    def total(self):
        return (self.tersedia + self.dipinjam + self.rusak_ringan
                + self.rusak_berat + self.pemeliharaan)

    @property
    def jumlah_rusak(self):
        return self.rusak_ringan + self.rusak_berat

    @property
    def kondisi(self):
        bagian = []
        if self.rusak_ringan:
            bagian.append(f"{self.rusak_ringan} rusak ringan")
        if self.rusak_berat:
            bagian.append(f"{self.rusak_berat} rusak berat")
        if self.pemeliharaan:
            bagian.append(f"{self.pemeliharaan} dalam pemeliharaan")
        return ", ".join(bagian) if bagian else "baik"

    # ---- perubahan stok ----
    def pinjam(self, jumlah):
        if jumlah > self.tersedia:
            raise AturanBisnisError(
                f"Stok {self.nama} ({self.kode}) tidak cukup: diminta "
                f"{jumlah}, tersedia {self.tersedia}."
            )
        self.tersedia -= jumlah
        self.dipinjam += jumlah

    def terima_kembali(self, jumlah, kondisi):
        """Aturan 5: hanya kondisi BAIK yang kembali menjadi stok tersedia."""
        if jumlah > self.dipinjam:
            raise AturanBisnisError(
                f"Jumlah dikembalikan ({jumlah}) melebihi jumlah yang "
                f"sedang dipinjam ({self.dipinjam})."
            )
        self.dipinjam -= jumlah
        if kondisi is KondisiAlat.BAIK:
            self.tersedia += jumlah
        elif kondisi is KondisiAlat.RUSAK_RINGAN:
            self.rusak_ringan += jumlah
        else:
            self.rusak_berat += jumlah

    def mulai_pemeliharaan(self, jumlah, dari):
        """Pindahkan unit rusak ke pemeliharaan (Tantangan C)."""
        if dari is KondisiAlat.RUSAK_RINGAN:
            if jumlah > self.rusak_ringan:
                raise AturanBisnisError(
                    f"Unit rusak ringan hanya {self.rusak_ringan}.")
            self.rusak_ringan -= jumlah
        elif dari is KondisiAlat.RUSAK_BERAT:
            if jumlah > self.rusak_berat:
                raise AturanBisnisError(
                    f"Unit rusak berat hanya {self.rusak_berat}.")
            self.rusak_berat -= jumlah
        else:
            raise AturanBisnisError(
                "Hanya unit rusak yang dapat masuk pemeliharaan.")
        self.pemeliharaan += jumlah

    def selesai_pemeliharaan(self, jumlah):
        """Unit yang sudah diperbaiki kembali ke stok tersedia."""
        if jumlah > self.pemeliharaan:
            raise AturanBisnisError(
                f"Unit dalam pemeliharaan hanya {self.pemeliharaan}.")
        self.pemeliharaan -= jumlah
        self.tersedia += jumlah

    def ubah_total(self, total_baru):
        """Ubah jumlah total; selisih dibebankan ke stok tersedia."""
        selisih = total_baru - self.total
        if self.tersedia + selisih < 0:
            minimum = self.total - self.tersedia
            raise AturanBisnisError(
                f"Total tidak boleh kurang dari {minimum} "
                "(unit yang sedang dipinjam/rusak/dipelihara)."
            )
        self.tersedia += selisih


class ItemPeminjaman:
    """Satu baris alat di dalam transaksi."""

    def __init__(self, kode, nama_alat, jumlah):
        self.kode = kode
        self.nama_alat = nama_alat      # snapshot nama saat transaksi dibuat
        self.jumlah = jumlah
        self.jumlah_kembali = 0

    @property
    def sisa(self):
        return self.jumlah - self.jumlah_kembali


class PengembalianRecord:
    """Catatan satu kali pengembalian (alat, jumlah, kondisi, tanggal)."""

    def __init__(self, kode, nama_alat, jumlah, kondisi, tanggal, hari_terlambat):
        self.kode = kode
        self.nama_alat = nama_alat
        self.jumlah = jumlah
        self.kondisi = kondisi
        self.tanggal = tanggal
        self.hari_terlambat = hari_terlambat    # 0 jika tepat waktu

    @property
    def terlambat(self):
        return self.hari_terlambat > 0


class Transaksi:
    def __init__(self, id_transaksi, mahasiswa, tanggal_pinjam, lama_hari):
        self.id = id_transaksi
        self.nim = mahasiswa.nim
        self.nama_peminjam = mahasiswa.nama     # snapshot untuk riwayat
        self.tanggal_pinjam = tanggal_pinjam
        self.batas_kembali = tanggal_pinjam + timedelta(days=lama_hari)
        self.items = {}             # kode alat -> ItemPeminjaman
        self.pengembalian = []      # list PengembalianRecord

    def tambah_item(self, alat, jumlah):
        if alat.kode in self.items:
            self.items[alat.kode].jumlah += jumlah
        else:
            self.items[alat.kode] = ItemPeminjaman(alat.kode, alat.nama, jumlah)

    def catat_pengembalian(self, kode, jumlah, kondisi, tanggal):
        item = self.items[kode]
        item.jumlah_kembali += jumlah
        terlambat = max(0, (tanggal - self.batas_kembali).days)
        record = PengembalianRecord(
            kode, item.nama_alat, jumlah, kondisi, tanggal, terlambat)
        self.pengembalian.append(record)
        return record

    @property
    def total_unit(self):
        return sum(i.jumlah for i in self.items.values())

    @property
    def total_sisa(self):
        return sum(i.sisa for i in self.items.values())

    @property
    def status(self):
        if self.total_sisa == 0:
            return StatusTransaksi.SELESAI
        if self.total_sisa < self.total_unit:
            return StatusTransaksi.SEBAGIAN
        return StatusTransaksi.DIPINJAM

    @property
    def aktif(self):
        return self.status is not StatusTransaksi.SELESAI

    def hari_terlambat(self, per_tanggal):
        """Hari keterlambatan untuk transaksi yang belum selesai."""
        if not self.aktif:
            return 0
        return max(0, (per_tanggal - self.batas_kembali).days)
