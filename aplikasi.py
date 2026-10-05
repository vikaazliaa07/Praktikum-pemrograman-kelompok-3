"""AplikasiLab: menu interaktif yang meneruskan pilihan ke manager."""
from datetime import date, datetime

from data_contoh import isi_data_contoh
from managers.mahasiswa_manager import MahasiswaManager
from managers.peralatan_manager import PeralatanManager
from managers.transaksi_manager import TransaksiManager
from models.peralatan import KONDISI_VALID


class AplikasiLab:
    def __init__(self):
        self.mahasiswa_mgr = MahasiswaManager()
        self.alat_mgr = PeralatanManager()
        self.transaksi_mgr = TransaksiManager(self.mahasiswa_mgr, self.alat_mgr)
        self._aksi = {
            1: self._tambah_mahasiswa, 2: self._edit_mahasiswa, 3: self._hapus_mahasiswa,
            4: self._cari_mahasiswa, 5: self.mahasiswa_mgr.tampilkan_mahasiswa,
            6: self._tambah_alat, 7: self._edit_alat, 8: self._hapus_alat,
            9: self._cari_alat, 10: self.alat_mgr.tampilkan_semua_alat,
            11: self._buat_transaksi, 12: self.transaksi_mgr.tampilkan_transaksi,
            13: self._proses_pengembalian, 14: self._cari_transaksi,
            15: self.alat_mgr.tampilkan_alat_tersedia, 16: self.alat_mgr.tampilkan_alat_dipinjam,
            17: self.alat_mgr.tampilkan_alat_rusak, 18: self._riwayat_mahasiswa,
            19: self.transaksi_mgr.tampilkan_statistik, 20: self._muat_data_contoh,
        }

    # ---------- menu utama ----------
    def tampilkan_menu(self):
        print("\n" + "=" * 52)
        print("  SISTEM PEMINJAMAN PERALATAN LABORATORIUM")
        print("=" * 52)
        print(" MAHASISWA : 1 Tambah  2 Edit  3 Hapus  4 Cari  5 Tampilkan")
        print(" ALAT      : 6 Tambah  7 Edit  8 Hapus  9 Cari  10 Tampilkan semua")
        print(" TRANSAKSI : 11 Buat peminjaman   12 Tampilkan transaksi")
        print("             13 Proses pengembalian   14 Cari transaksi mahasiswa")
        print(" LAPORAN   : 15 Alat tersedia  16 Alat dipinjam  17 Alat rusak")
        print("             18 Riwayat mahasiswa  19 Statistik")
        print(" LAINNYA   : 20 Muat data contoh   0 Keluar")

    def proses_pilihan(self, pilihan):
        aksi = self._aksi.get(pilihan)
        if aksi is None:
            print("  [!] Pilihan tidak tersedia.")
            return
        try:
            aksi()
        except ValueError as e:
            print(f"  [GAGAL] {e}")

    def jalankan(self):
        while True:
            self.tampilkan_menu()
            teks = input("Pilih menu: ").strip()
            if not teks.isdigit():
                print("  [!] Masukkan angka menu.")
                continue
            pilihan = int(teks)
            if pilihan == 0:
                print("Terima kasih. Program selesai.")
                break
            self.proses_pilihan(pilihan)

    # ---------- helper input ----------
    @staticmethod
    def _input_tanggal(prompt):
        teks = input(f"{prompt} (YYYY-MM-DD, kosong = hari ini): ").strip()
        if not teks:
            return date.today()
        try:
            return datetime.strptime(teks, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Format tanggal harus YYYY-MM-DD.")

    @staticmethod
    def _input_kondisi():
        for i, k in enumerate(KONDISI_VALID, 1):
            print(f"    {i}. {k}")
        teks = input("  Kondisi alat (nomor): ").strip()
        if not teks.isdigit() or not 1 <= int(teks) <= len(KONDISI_VALID):
            raise ValueError("Pilihan kondisi tidak valid.")
        return KONDISI_VALID[int(teks) - 1]

    # ---------- aksi mahasiswa ----------
    def _tambah_mahasiswa(self):
        m = self.mahasiswa_mgr.tambah_mahasiswa(input("NIM: "), input("Nama: "), input("No HP: "))
        print(f"  Mahasiswa {m.nim} ditambahkan.")

    def _edit_mahasiswa(self):
        nim = input("NIM yang diedit: ")
        self.mahasiswa_mgr.ambil_mahasiswa(nim)
        self.mahasiswa_mgr.edit_mahasiswa(nim, input("Nama baru (kosong = tetap): "),
                                          input("No HP baru (kosong = tetap): "))
        print("  Data mahasiswa diperbarui.")

    def _hapus_mahasiswa(self):
        nim = input("NIM yang dihapus: ")
        self.mahasiswa_mgr.hapus_mahasiswa(nim)
        print("  Mahasiswa dihapus.")

    def _cari_mahasiswa(self):
        self.mahasiswa_mgr.tampilkan_mahasiswa(self.mahasiswa_mgr.cari_mahasiswa(input("Kata kunci (NIM/nama): ")))

    # ---------- aksi alat ----------
    def _tambah_alat(self):
        kode, nama = input("Kode alat: "), input("Nama alat: ")
        kategori = input("Kategori (boleh kategori baru): ")
        print("  Kondisi awal:")
        kondisi = self._input_kondisi()
        self.alat_mgr.tambah_alat(kode, nama, kategori, kondisi)
        print(f"  Alat {kode.strip()} ditambahkan.")

    def _edit_alat(self):
        kode = input("Kode alat yang diedit: ")
        self.alat_mgr.ambil_alat(kode)
        kondisi = None
        if input("Ubah kondisi? (y/n): ").strip().lower() == "y":
            kondisi = self._input_kondisi()
        self.alat_mgr.edit_alat(kode, input("Nama baru (kosong = tetap): "),
                                input("Kategori baru (kosong = tetap): "), kondisi)
        print("  Data alat diperbarui.")

    def _hapus_alat(self):
        self.alat_mgr.hapus_alat(input("Kode alat yang dihapus: "))
        print("  Alat dihapus.")

    def _cari_alat(self):
        self.alat_mgr.tampilkan_semua_alat(self.alat_mgr.cari_alat(input("Kata kunci (kode/nama/kategori): ")))

    # ---------- aksi transaksi ----------
    def _buat_transaksi(self):
        nim = input("NIM peminjam: ")
        print("  Alat yang tersedia:")
        self.alat_mgr.tampilkan_alat_tersedia()
        kode = input("Kode alat (pisahkan koma): ").split(",")
        tanggal = self._input_tanggal("Tanggal peminjaman")
        trx = self.transaksi_mgr.buat_transaksi(nim, kode, tanggal)
        print(f"  Transaksi {trx.id_transaksi} dibuat. Batas kembali: {trx.batas_kembali.isoformat()}")

    def _proses_pengembalian(self):
        id_trx = input("ID transaksi: ")
        self.transaksi_mgr.ambil_transaksi(id_trx).tampilkan_info()
        kode = input("Kode alat yang dikembalikan: ")
        kondisi = self._input_kondisi()
        tanggal = self._input_tanggal("Tanggal pengembalian")
        trx = self.transaksi_mgr.proses_pengembalian(id_trx, kode, kondisi, tanggal)
        print(f"  Alat {kode.strip()} dikembalikan. Status transaksi: {trx.status}")

    def _cari_transaksi(self):
        self.transaksi_mgr.cari_transaksi_mahasiswa(input("NIM mahasiswa: "))

    def _riwayat_mahasiswa(self):
        self.transaksi_mgr.tampilkan_riwayat_mahasiswa(input("NIM mahasiswa: "))

    def _muat_data_contoh(self):
        n_mhs, n_alat = isi_data_contoh(self.mahasiswa_mgr, self.alat_mgr)
        print(f"  Data contoh dimuat: {n_mhs} mahasiswa, {n_alat} alat.")
