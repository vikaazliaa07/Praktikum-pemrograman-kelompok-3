"""Class Transaksi: satu transaksi peminjaman berisi banyak alat (List of Detail)."""
from datetime import date, timedelta

from models.detail_peminjaman import Detail_Peminjaman


class Transaksi:
    BATAS_HARI = 7  # batas pengembalian maksimal 7 hari

    def __init__(self, id_transaksi, mahasiswa, tanggal_pinjam=None):
        self.id_transaksi = id_transaksi
        self.mahasiswa = mahasiswa
        self.tanggal_pinjam = tanggal_pinjam or date.today()
        self.batas_kembali = self.tanggal_pinjam + timedelta(days=self.BATAS_HARI)
        self.status = "dipinjam"
        self.daftar_detail = []           # List[Detail_Peminjaman] (Aturan 3)

    def tambah_detail(self, alat):
        if any(d.peralatan.kode_alat == alat.kode_alat for d in self.daftar_detail):
            raise ValueError(f"Alat {alat.kode_alat} sudah ada di transaksi {self.id_transaksi}.")
        detail = Detail_Peminjaman(alat)
        self.daftar_detail.append(detail)
        return detail

    def kembalikan_alat(self, kode_alat, kondisi, tanggal=None):
        """Pengembalian sebagian: hanya alat yang disebut yang dikembalikan (Aturan 4)."""
        tanggal = tanggal or date.today()
        if tanggal < self.tanggal_pinjam:
            raise ValueError("Tanggal pengembalian tidak boleh sebelum tanggal peminjaman.")
        detail = next((d for d in self.daftar_detail
                       if d.peralatan.kode_alat == kode_alat and not d.sudah_kembali), None)
        if detail is None:
            raise ValueError(f"Alat {kode_alat} tidak ada di transaksi {self.id_transaksi} "
                             f"atau sudah dikembalikan.")
        kondisi_baku = detail.peralatan._validasi_kondisi(kondisi)
        detail.peralatan.terima_kembali(kondisi_baku)   # alat rusak -> tidak tersedia
        detail.catat_pengembalian(kondisi_baku, tanggal)
        self.perbarui_status()
        return detail

    def perbarui_status(self):
        status_lama = self.status
        total = len(self.daftar_detail)
        kembali = sum(1 for d in self.daftar_detail if d.sudah_kembali)
        if kembali == 0:
            self.status = "dipinjam"
        elif kembali < total:
            self.status = "sebagian dikembalikan"
        else:
            self.status = "selesai"
        # transaksi baru berhenti dihitung aktif setelah SEMUA alat kembali
        if self.status == "selesai" and status_lama != "selesai":
            self.mahasiswa.kurangi_transaksi_aktif()

    def masih_aktif(self):
        return self.status != "selesai"

    def terlambat(self, tanggal=None):
        tanggal = tanggal or date.today()
        return self.masih_aktif() and tanggal > self.batas_kembali

    def tampilkan_info(self):
        tanda = "  <-- TERLAMBAT" if self.terlambat() else ""
        print(f"  Transaksi {self.id_transaksi} | {self.mahasiswa.nim} - {self.mahasiswa.nama}\n"
              f"    Pinjam: {self.tanggal_pinjam.isoformat()} | Batas kembali: "
              f"{self.batas_kembali.isoformat()} | Status: {self.status}{tanda}")
        for detail in self.daftar_detail:
            detail.tampilkan_info()
