"""Logika transaksi peminjaman dan pengembalian.

Kedua operasi utama (buat & kembalikan) bersifat atomik: seluruh input
divalidasi lebih dulu, baru stok diubah. Jika ada satu error, tidak ada
perubahan apa pun pada data.
"""

from datetime import date

from .exceptions import (AturanBisnisError, DataTidakDitemukanError,
                         ValidasiError)
from .konfigurasi import MAKS_HARI_PINJAM, MAKS_TRANSAKSI_AKTIF
from .models import KondisiAlat, Transaksi
from .validasi import bilangan_positif, wajib_isi


def _gabung_jumlah(pasangan, nama_field="Jumlah"):
    """Gabungkan [(kode, jumlah), ...] menjadi {KODE: total}."""
    hasil = {}
    for kode, jumlah in pasangan:
        kode = wajib_isi(kode, "Kode alat").upper()
        bilangan_positif(jumlah, nama_field)
        hasil[kode] = hasil.get(kode, 0) + jumlah
    return hasil


class TransaksiService:
    def __init__(self, mahasiswa_service, alat_service, log):
        self._mhs = mahasiswa_service
        self._alat = alat_service
        self._log = log
        self._data = {}         # id transaksi -> Transaksi
        self._per_nim = {}      # nim -> [id transaksi] (index untuk riwayat)
        self._counter = 0

    # ---------- buat transaksi ----------
    def buat(self, nim, daftar_item, lama_hari=MAKS_HARI_PINJAM, tanggal=None):
        """daftar_item: list of (kode_alat, jumlah)."""
        tanggal = tanggal or date.today()
        mhs = self._mhs.ambil(nim)

        if (isinstance(lama_hari, bool) or not isinstance(lama_hari, int)
                or not 1 <= lama_hari <= MAKS_HARI_PINJAM):
            raise ValidasiError(
                f"Lama peminjaman harus 1-{MAKS_HARI_PINJAM} hari.")
        if not daftar_item:
            raise ValidasiError("Transaksi harus berisi minimal satu alat.")

        # Aturan 2
        if mhs.jumlah_transaksi_aktif >= MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"Mahasiswa {mhs.nim} sudah memiliki {mhs.jumlah_transaksi_aktif} "
                f"transaksi aktif (maksimal {MAKS_TRANSAKSI_AKTIF}).")

        # Aturan 1: validasi semua item sebelum stok diubah
        kebutuhan = _gabung_jumlah(daftar_item)
        masalah = []
        for kode, jumlah in kebutuhan.items():
            alat = self._alat.ambil(kode)       # error jika kode tidak ada
            if jumlah > alat.tersedia:
                masalah.append(
                    f"{alat.nama} ({alat.kode}): diminta {jumlah}, "
                    f"tersedia {alat.tersedia}")
        if masalah:
            raise AturanBisnisError(
                "Alat tidak tersedia -> " + "; ".join(masalah))

        # semua valid -> terapkan perubahan
        self._counter += 1
        id_trx = f"T{self._counter:03d}"
        trx = Transaksi(id_trx, mhs, tanggal, lama_hari)
        for kode, jumlah in kebutuhan.items():
            alat = self._alat.ambil(kode)
            alat.pinjam(jumlah)
            alat.transaksi_aktif.add(id_trx)
            trx.tambah_item(alat, jumlah)
        mhs.transaksi_aktif.add(id_trx)
        self._data[id_trx] = trx
        self._per_nim.setdefault(mhs.nim, []).append(id_trx)

        self._log.catat(f"Transaksi {id_trx} dibuat oleh {mhs.nim}")
        for item in trx.items.values():
            self._log.catat(
                f"{item.jumlah} unit {item.nama_alat} dipinjam ({id_trx})")
        return trx

    # ---------- pengembalian ----------
    def kembalikan(self, id_transaksi, daftar_pengembalian, tanggal=None):
        """daftar_pengembalian: list of (kode_alat, jumlah, KondisiAlat)."""
        tanggal = tanggal or date.today()
        trx = self.ambil(id_transaksi)
        if not trx.aktif:
            raise AturanBisnisError(f"Transaksi {trx.id} sudah selesai.")
        if not daftar_pengembalian:
            raise ValidasiError("Tidak ada alat yang dikembalikan.")
        if tanggal < trx.tanggal_pinjam:
            raise ValidasiError(
                "Tanggal pengembalian tidak boleh sebelum tanggal peminjaman.")

        # validasi semua baris sebelum mengubah apa pun
        total_per_kode = {}
        for kode, jumlah, kondisi in daftar_pengembalian:
            kode = wajib_isi(kode, "Kode alat").upper()
            bilangan_positif(jumlah, "Jumlah")
            if not isinstance(kondisi, KondisiAlat):
                raise ValidasiError("Kondisi alat tidak valid.")
            if kode not in trx.items:
                raise ValidasiError(
                    f"Alat {kode} tidak termasuk dalam transaksi {trx.id}.")
            total_per_kode[kode] = total_per_kode.get(kode, 0) + jumlah
        for kode, jumlah in total_per_kode.items():
            sisa = trx.items[kode].sisa
            if jumlah > sisa:
                raise AturanBisnisError(
                    f"{trx.items[kode].nama_alat} ({kode}): dikembalikan "
                    f"{jumlah}, tetapi sisa yang dipinjam hanya {sisa}.")

        # terapkan
        hasil = []
        for kode, jumlah, kondisi in daftar_pengembalian:
            kode = kode.strip().upper()
            self._alat.ambil(kode).terima_kembali(jumlah, kondisi)
            rec = trx.catat_pengembalian(kode, jumlah, kondisi, tanggal)
            hasil.append(rec)
            catatan = f" (terlambat {rec.hari_terlambat} hari)" if rec.terlambat else ""
            self._log.catat(
                f"{jumlah} unit {rec.nama_alat} dikembalikan dalam kondisi "
                f"{kondisi.value} ({trx.id}){catatan}")

        if not trx.aktif:
            self._selesaikan(trx)
        return hasil

    def _selesaikan(self, trx):
        """Lepas keterkaitan 'aktif' antara transaksi, mahasiswa, dan alat."""
        try:
            self._mhs.ambil(trx.nim).transaksi_aktif.discard(trx.id)
        except DataTidakDitemukanError:
            pass
        for kode in trx.items:
            try:
                self._alat.ambil(kode).transaksi_aktif.discard(trx.id)
            except DataTidakDitemukanError:
                pass
        self._log.catat(f"Transaksi {trx.id} selesai")

    # ---------- query ----------
    def ambil(self, id_transaksi):
        try:
            return self._data[str(id_transaksi).strip().upper()]
        except KeyError:
            raise DataTidakDitemukanError(
                f"Transaksi {id_transaksi} tidak ditemukan.") from None

    def semua(self):
        return [self._data[k] for k in sorted(self._data)]

    def aktif(self):
        return [t for t in self.semua() if t.aktif]

    def selesai(self):
        return [t for t in self.semua() if not t.aktif]

    def riwayat(self, nim):
        """Semua transaksi (aktif dan selesai) milik satu NIM."""
        return [self._data[i] for i in self._per_nim.get(str(nim).strip(), [])]

    def cari_berdasarkan_mahasiswa(self, kata_kunci):
        """Cari transaksi berdasarkan sebagian NIM atau nama peminjam."""
        kunci = wajib_isi(kata_kunci, "Kata kunci").lower()
        return [t for t in self.semua()
                if kunci in t.nim.lower() or kunci in t.nama_peminjam.lower()]
