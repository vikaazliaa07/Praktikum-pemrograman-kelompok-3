"""Antarmuka menu interaktif (satu-satunya bagian yang memakai input/print)."""

from datetime import date, datetime

from .data_contoh import muat_data_contoh
from .exceptions import LabError
from .konfigurasi import MAKS_HARI_PINJAM
from .models import KondisiAlat

PILIHAN_KONDISI = {
    "1": KondisiAlat.BAIK,
    "2": KondisiAlat.RUSAK_RINGAN,
    "3": KondisiAlat.RUSAK_BERAT,
}


# ---------------------------------------------------------------- input
def tanya(pesan):
    return input(f"{pesan}: ").strip()


def tanya_int(pesan, default=None):
    """Minta bilangan bulat; kembalikan None jika kosong dan tanpa default."""
    while True:
        teks = tanya(pesan)
        if not teks:
            return default
        try:
            return int(teks)
        except ValueError:
            print("  Masukkan angka bulat.")


def tanya_tanggal(pesan):
    """Format YYYY-MM-DD; kosong = hari ini."""
    while True:
        teks = tanya(f"{pesan} (YYYY-MM-DD, kosong = hari ini)")
        if not teks:
            return date.today()
        try:
            return datetime.strptime(teks, "%Y-%m-%d").date()
        except ValueError:
            print("  Format tanggal salah.")


def tanya_kondisi():
    while True:
        print("  Kondisi: 1) baik  2) rusak ringan  3) rusak berat")
        pilihan = tanya("  Pilih kondisi")
        if pilihan in PILIHAN_KONDISI:
            return PILIHAN_KONDISI[pilihan]
        print("  Pilihan tidak valid.")


# --------------------------------------------------------------- tampilan
def garis(panjang=78):
    print("-" * panjang)


def tampil_mahasiswa(daftar):
    if not daftar:
        print("(tidak ada data)")
        return
    garis()
    print(f"{'NIM':<12}{'Nama':<28}{'No. HP':<16}Status peminjaman")
    garis()
    for m in daftar:
        print(f"{m.nim:<12}{m.nama:<28}{m.no_hp:<16}{m.status_peminjaman}")


def tampil_alat(daftar, rinci_stok=True):
    if not daftar:
        print("(tidak ada data)")
        return
    garis(96)
    print(f"{'Kode':<8}{'Nama':<20}{'Kategori':<22}{'Tersedia':>9}"
          f"{'Dipinjam':>9}{'Rusak':>7}{'Pelihara':>9}  Kondisi")
    garis(96)
    for a in daftar:
        print(f"{a.kode:<8}{a.nama:<20}{a.kategori:<22}{a.tersedia:>9}"
              f"{a.dipinjam:>9}{a.jumlah_rusak:>7}{a.pemeliharaan:>9}  {a.kondisi}")


def tampil_transaksi(trx, per_tanggal=None):
    per_tanggal = per_tanggal or date.today()
    garis()
    print(f"{trx.id} | {trx.nim} - {trx.nama_peminjam} | "
          f"status: {trx.status.value.upper()}")
    print(f"  Dipinjam: {trx.tanggal_pinjam}   Batas kembali: {trx.batas_kembali}")
    telat = trx.hari_terlambat(per_tanggal)
    if telat:
        print(f"  !! TERLAMBAT {telat} hari (per {per_tanggal})")
    for item in trx.items.values():
        print(f"  - {item.kode:<7}{item.nama_alat:<20} dipinjam {item.jumlah}, "
              f"kembali {item.jumlah_kembali}, sisa {item.sisa}")
    for r in trx.pengembalian:
        tanda = f" [terlambat {r.hari_terlambat} hari]" if r.terlambat else ""
        print(f"    * {r.tanggal}: {r.jumlah} unit {r.nama_alat} kembali "
              f"({r.kondisi.value}){tanda}")


def tampil_daftar_transaksi(daftar):
    if not daftar:
        print("(tidak ada transaksi)")
    for t in daftar:
        tampil_transaksi(t)


# ------------------------------------------------------------------- menu
class MenuCLI:
    def __init__(self, sistem):
        self.s = sistem

    def jalankan(self):
        aksi = {
            "1": self.menu_mahasiswa,
            "2": self.menu_alat,
            "3": self.buat_transaksi,
            "4": self.lihat_transaksi,
            "5": self.proses_pengembalian,
            "6": self.cari_transaksi_mahasiswa,
            "7": lambda: tampil_alat(self.s.alat.tersedia()),
            "8": lambda: tampil_alat(self.s.alat.sedang_dipinjam()),
            "9": lambda: tampil_alat(self.s.alat.rusak()),
            "10": self.riwayat_mahasiswa,
            "11": self.menu_pemeliharaan,
            "12": self.tampil_statistik,
            "13": self.tampil_log,
            "14": self.muat_contoh,
        }
        while True:
            print("\n===== SISTEM PEMINJAMAN PERALATAN LABORATORIUM =====")
            print(" 1. Kelola data mahasiswa")
            print(" 2. Kelola data alat")
            print(" 3. Buat transaksi peminjaman")
            print(" 4. Tampilkan transaksi")
            print(" 5. Proses pengembalian alat")
            print(" 6. Cari transaksi berdasarkan mahasiswa")
            print(" 7. Tampilkan alat yang tersedia")
            print(" 8. Tampilkan alat yang sedang dipinjam")
            print(" 9. Tampilkan alat yang rusak")
            print("10. Tampilkan riwayat peminjaman mahasiswa")
            print("11. Pemeliharaan alat rusak")
            print("12. Statistik peminjaman")
            print("13. Log aktivitas")
            print("14. Muat data contoh")
            print(" 0. Keluar")
            try:
                pilihan = tanya("Pilih menu")
            except EOFError:
                print("\nInput berakhir. Keluar.")
                return
            if pilihan == "0":
                print("Terima kasih.")
                return
            if pilihan not in aksi:
                print("Pilihan tidak valid.")
                continue
            self._jalankan_aman(aksi[pilihan])

    @staticmethod
    def _jalankan_aman(fungsi):
        try:
            fungsi()
        except LabError as err:
            print(f"[GAGAL] {err}")

    # ---------------- mahasiswa ----------------
    def menu_mahasiswa(self):
        print("\n-- Kelola Mahasiswa --")
        print("1) Tambah  2) Edit  3) Hapus  4) Cari  5) Tampilkan semua")
        pilihan = tanya("Pilih")
        if pilihan == "1":
            m = self.s.mahasiswa.tambah(
                tanya("NIM"), tanya("Nama"), tanya("Nomor HP"))
            print(f"Mahasiswa {m.nim} - {m.nama} ditambahkan.")
        elif pilihan == "2":
            nim = tanya("NIM yang diubah")
            m = self.s.mahasiswa.ambil(nim)
            nama = tanya(f"Nama baru [{m.nama}] (kosong = tetap)")
            hp = tanya(f"No. HP baru [{m.no_hp}] (kosong = tetap)")
            self.s.mahasiswa.edit(nim, nama or None, hp or None)
            print("Data mahasiswa diperbarui.")
        elif pilihan == "3":
            self.s.mahasiswa.hapus(tanya("NIM yang dihapus"))
            print("Mahasiswa dihapus.")
        elif pilihan == "4":
            tampil_mahasiswa(self.s.mahasiswa.cari(tanya("Kata kunci (NIM/nama)")))
        elif pilihan == "5":
            tampil_mahasiswa(self.s.mahasiswa.semua())
        else:
            print("Pilihan tidak valid.")

    # ---------------- alat ----------------
    def menu_alat(self):
        print("\n-- Kelola Alat --")
        print("1) Tambah  2) Edit  3) Hapus  4) Cari  5) Tampilkan semua  "
              "6) Tambah kategori")
        pilihan = tanya("Pilih")
        if pilihan == "1":
            print("Kategori tersedia:", ", ".join(self.s.alat.daftar_kategori()))
            a = self.s.alat.tambah(
                tanya("Kode alat"), tanya("Nama alat"), tanya("Kategori"),
                tanya_int("Jumlah unit"))
            print(f"Alat {a.kode} - {a.nama} ditambahkan.")
        elif pilihan == "2":
            kode = tanya("Kode alat yang diubah")
            a = self.s.alat.ambil(kode)
            nama = tanya(f"Nama baru [{a.nama}] (kosong = tetap)")
            kat = tanya(f"Kategori baru [{a.kategori}] (kosong = tetap)")
            total = tanya_int(f"Jumlah total baru [{a.total}] (kosong = tetap)")
            self.s.alat.edit(kode, nama or None, kat or None, total)
            print("Data alat diperbarui.")
        elif pilihan == "3":
            self.s.alat.hapus(tanya("Kode alat yang dihapus"))
            print("Alat dihapus.")
        elif pilihan == "4":
            print("Isi kriteria yang diperlukan (kosongkan yang tidak dipakai).")
            tampil_alat(self.s.alat.cari(
                kode=tanya("Kode (sebagian)"),
                nama=tanya("Nama (sebagian)"),
                kategori=tanya("Kategori (sebagian)")))
        elif pilihan == "5":
            tampil_alat(self.s.alat.semua())
        elif pilihan == "6":
            print("Kategori saat ini:", ", ".join(self.s.alat.daftar_kategori()))
            nama = self.s.alat.tambah_kategori(tanya("Nama kategori baru"))
            print(f"Kategori '{nama}' ditambahkan.")
        else:
            print("Pilihan tidak valid.")

    # ---------------- transaksi ----------------
    def buat_transaksi(self):
        print("\n-- Buat Transaksi Peminjaman --")
        nim = tanya("NIM mahasiswa")
        mhs = self.s.mahasiswa.ambil(nim)
        print(f"Peminjam: {mhs.nama} ({mhs.status_peminjaman})")
        print("Alat tersedia saat ini:")
        tampil_alat(self.s.alat.tersedia())
        daftar = []
        print("Tambahkan alat (kosongkan kode untuk selesai).")
        while True:
            kode = tanya("Kode alat")
            if not kode:
                break
            jumlah = tanya_int("Jumlah unit", default=1)
            daftar.append((kode, jumlah))
        lama = tanya_int(f"Lama pinjam dalam hari (1-{MAKS_HARI_PINJAM}, "
                         f"kosong = {MAKS_HARI_PINJAM})", default=MAKS_HARI_PINJAM)
        trx = self.s.transaksi.buat(nim, daftar, lama)
        print(f"Transaksi {trx.id} berhasil dibuat.")
        tampil_transaksi(trx)

    def lihat_transaksi(self):
        print("\n-- Tampilkan Transaksi --")
        print("1) Semua  2) Hanya aktif  3) Hanya selesai  4) Berdasarkan ID")
        pilihan = tanya("Pilih")
        if pilihan == "1":
            tampil_daftar_transaksi(self.s.transaksi.semua())
        elif pilihan == "2":
            tampil_daftar_transaksi(self.s.transaksi.aktif())
        elif pilihan == "3":
            tampil_daftar_transaksi(self.s.transaksi.selesai())
        elif pilihan == "4":
            tampil_transaksi(self.s.transaksi.ambil(tanya("ID transaksi")))
        else:
            print("Pilihan tidak valid.")

    def proses_pengembalian(self):
        print("\n-- Proses Pengembalian Alat --")
        id_trx = tanya("ID transaksi")
        trx = self.s.transaksi.ambil(id_trx)
        tampil_transaksi(trx)
        daftar = []
        print("Isi alat yang dikembalikan (kosongkan kode untuk selesai).")
        while True:
            kode = tanya("Kode alat")
            if not kode:
                break
            jumlah = tanya_int("Jumlah unit dikembalikan", default=1)
            kondisi = tanya_kondisi()
            daftar.append((kode, jumlah, kondisi))
        tanggal = tanya_tanggal("Tanggal pengembalian")
        hasil = self.s.transaksi.kembalikan(id_trx, daftar, tanggal)
        for r in hasil:
            tanda = f" - TERLAMBAT {r.hari_terlambat} hari" if r.terlambat else ""
            print(f"Dicatat: {r.jumlah} unit {r.nama_alat} ({r.kondisi.value}){tanda}")
        tampil_transaksi(trx, tanggal)

    def cari_transaksi_mahasiswa(self):
        print("\n-- Cari Transaksi Berdasarkan Mahasiswa --")
        tampil_daftar_transaksi(
            self.s.transaksi.cari_berdasarkan_mahasiswa(
                tanya("NIM atau nama mahasiswa")))

    def riwayat_mahasiswa(self):
        print("\n-- Riwayat Peminjaman Mahasiswa --")
        nim = tanya("NIM mahasiswa")
        riwayat = self.s.transaksi.riwayat(nim)
        print(f"Riwayat {nim}: {len(riwayat)} transaksi")
        tampil_daftar_transaksi(riwayat)

    # ---------------- pemeliharaan (Tantangan C) ----------------
    def menu_pemeliharaan(self):
        print("\n-- Pemeliharaan Alat --")
        print("1) Kirim unit rusak ke pemeliharaan  "
              "2) Tandai selesai diperbaiki  3) Lihat daftar pemeliharaan")
        pilihan = tanya("Pilih")
        if pilihan == "1":
            tampil_alat(self.s.alat.rusak())
            kode = tanya("Kode alat")
            print("  Asal unit: 2) rusak ringan  3) rusak berat")
            asal = tanya("  Pilih asal")
            if asal not in ("2", "3"):
                print("Pilihan tidak valid.")
                return
            self.s.alat.mulai_pemeliharaan(
                kode, tanya_int("Jumlah unit"), PILIHAN_KONDISI[asal])
            print("Unit dipindahkan ke pemeliharaan.")
        elif pilihan == "2":
            tampil_alat(self.s.alat.dalam_pemeliharaan())
            self.s.alat.selesai_pemeliharaan(
                tanya("Kode alat"), tanya_int("Jumlah unit selesai diperbaiki"))
            print("Unit kembali ke stok tersedia.")
        elif pilihan == "3":
            tampil_alat(self.s.alat.dalam_pemeliharaan())
        else:
            print("Pilihan tidak valid.")

    # ---------------- statistik (Tantangan B) ----------------
    def tampil_statistik(self):
        st = self.s.statistik
        print("\n-- Statistik Peminjaman --")
        print(f"Transaksi selesai : {st.jumlah_selesai()}")
        print(f"Transaksi aktif   : {st.jumlah_aktif()}")
        print("Alat paling sering dipinjam (total unit):")
        for kode, nama, total in st.alat_terpopuler() or []:
            print(f"  {kode:<8}{nama:<20}{total} unit")
        print("Mahasiswa paling sering meminjam (jumlah transaksi):")
        for nim, nama, total in st.mahasiswa_teraktif() or []:
            print(f"  {nim:<8}{nama:<20}{total} transaksi")

    # ---------------- log (Tantangan D) ----------------
    def tampil_log(self):
        print("\n-- Log Aktivitas --")
        entri = self.s.log.semua()
        if not entri:
            print("(log kosong)")
        for e in entri:
            print(self.s.log.format_entri(e))

    def muat_contoh(self):
        muat_data_contoh(self.s)
        print("Data contoh dimuat (3 mahasiswa, 5 jenis alat).")
