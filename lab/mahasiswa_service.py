"""Pengelolaan data mahasiswa (CRUD)."""

from .exceptions import (AturanBisnisError, DataDuplikatError,
                         DataTidakDitemukanError)
from .models import Mahasiswa
from .validasi import validasi_no_hp, wajib_isi


class MahasiswaService:
    def __init__(self, log):
        self._data = {}         # nim -> Mahasiswa
        self._log = log

    def tambah(self, nim, nama, no_hp):
        nim = wajib_isi(nim, "NIM")
        nama = wajib_isi(nama, "Nama")
        no_hp = validasi_no_hp(no_hp)
        if nim in self._data:
            raise DataDuplikatError(f"NIM {nim} sudah terdaftar.")
        mhs = Mahasiswa(nim, nama, no_hp)
        self._data[nim] = mhs
        self._log.catat(f"Mahasiswa {nim} ditambahkan")
        return mhs

    def ambil(self, nim):
        try:
            return self._data[str(nim).strip()]
        except KeyError:
            raise DataTidakDitemukanError(
                f"Mahasiswa dengan NIM {nim} tidak ditemukan.") from None

    def edit(self, nim, nama=None, no_hp=None):
        """NIM adalah kunci sehingga tidak dapat diubah."""
        mhs = self.ambil(nim)
        nama_baru = wajib_isi(nama, "Nama") if nama is not None else mhs.nama
        hp_baru = validasi_no_hp(no_hp) if no_hp is not None else mhs.no_hp
        mhs.nama, mhs.no_hp = nama_baru, hp_baru
        self._log.catat(f"Mahasiswa {mhs.nim} diubah")
        return mhs

    def hapus(self, nim):
        """Aturan 6: tidak boleh dihapus jika masih punya transaksi aktif."""
        mhs = self.ambil(nim)
        if mhs.transaksi_aktif:
            daftar = ", ".join(sorted(mhs.transaksi_aktif))
            raise AturanBisnisError(
                f"Mahasiswa {mhs.nim} tidak dapat dihapus: masih memiliki "
                f"transaksi aktif ({daftar}).")
        del self._data[mhs.nim]
        self._log.catat(f"Mahasiswa {mhs.nim} dihapus")

    def cari(self, kata_kunci):
        """Cari berdasarkan sebagian NIM atau sebagian nama."""
        kunci = wajib_isi(kata_kunci, "Kata kunci").lower()
        return [m for m in self.semua()
                if kunci in m.nim.lower() or kunci in m.nama.lower()]

    def semua(self):
        return sorted(self._data.values(), key=lambda m: m.nim)
