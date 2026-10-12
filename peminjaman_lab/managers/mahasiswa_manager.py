"""MahasiswaManager: CRUD data mahasiswa (Dict nim -> Mahasiswa)."""
from models.mahasiswa import Mahasiswa


class MahasiswaManager:
    def __init__(self):
        self.daftar_mahasiswa = {}

    @staticmethod
    def _validasi_hp(no_hp):
        isi = no_hp.strip()
        if not isi.lstrip("+").isdigit() or not 8 <= len(isi.lstrip("+")) <= 15:
            raise ValueError("Nomor HP harus berupa angka (8-15 digit).")
        return isi

    def tambah_mahasiswa(self, nim, nama, no_hp):
        nim, nama = nim.strip(), nama.strip()
        if not nim or not nama:
            raise ValueError("NIM dan nama tidak boleh kosong.")
        if nim in self.daftar_mahasiswa:
            raise ValueError(f"NIM {nim} sudah terdaftar.")
        mhs = Mahasiswa(nim, nama, self._validasi_hp(no_hp))
        self.daftar_mahasiswa[nim] = mhs
        return mhs

    def edit_mahasiswa(self, nim, nama=None, no_hp=None):
        mhs = self.ambil_mahasiswa(nim)
        if nama is not None and nama.strip():
            mhs.nama = nama.strip()
        if no_hp is not None and no_hp.strip():
            mhs.no_hp = self._validasi_hp(no_hp)
        return mhs

    def hapus_mahasiswa(self, nim):
        mhs = self.ambil_mahasiswa(nim)
        if mhs.punya_transaksi_aktif():          # Aturan 6
            raise ValueError(f"Mahasiswa {nim} masih memiliki transaksi aktif; tidak dapat dihapus.")
        del self.daftar_mahasiswa[nim.strip()]

    def cari_mahasiswa(self, keyword):
        kw = keyword.strip().lower()
        return [m for m in self.daftar_mahasiswa.values()
                if kw in m.nim.lower() or kw in m.nama.lower()]

    def ambil_mahasiswa(self, nim):
        mhs = self.daftar_mahasiswa.get(nim.strip())
        if mhs is None:
            raise ValueError(f"Mahasiswa dengan NIM {nim} tidak ditemukan.")
        return mhs

    def tampilkan_mahasiswa(self, daftar=None):
        daftar = list(self.daftar_mahasiswa.values()) if daftar is None else daftar
        if not daftar:
            print("  (tidak ada data mahasiswa)")
        for m in daftar:
            m.tampilkan_info()
