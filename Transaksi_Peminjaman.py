class Transaksi_Peminjaman:
    def __init__(self, id_transaksi, mahasiswa, tanggal_pinjam, batas_kembali):
        self.id_transaksi = id_transaksi
        self.mahasiswa = mahasiswa
        self.tanggal_pinjam = tanggal_pinjam
        self.batas_kembali = batas_kembali
        self.status = "Aktif"
        self.detail = []

    def tambah_detail(self, detail_peminjaman):
        self.detail.append(detail_peminjaman)
        print("Detail peminjaman berhasil ditambahkan.")

    def kembalikan_alat(self, kode_alat, kondisi, tanggal):
        for detail in self.detail:
            if detail.peralatan.kode_alat == kode_alat:
                detail.catat_pengembalian(kondisi, tanggal)
                print(f"Alat {kode_alat} berhasil dikembalikan.")
                self.perbarui_status()
                return

        print(f"Alat dengan kode {kode_alat} tidak ditemukan.")

    def perbarui_status(self):
        if not self.detail:
            self.status = "Aktif"
        elif all(detail.sudah_kembali for detail in self.detail):
            self.status = "Selesai"
        else:
            self.status = "Aktif"

    def masih_aktif(self):
        return self.status == "Aktif"

    def terlambat(self, tanggal=None):
        if tanggal is None:
            tanggal = date.today()

        return tanggal > self.batas_kembali and self.status == "Aktif"

    def tampilkan_info(self):
        print("ID Transaksi :", self.id_transaksi)
        print("Mahasiswa    :", self.mahasiswa)
        print("Tanggal Pinjam:", self.tanggal_pinjam)
        print("Batas Kembali:", self.batas_kembali)
        print("Status       :", self.status)
        print("Jumlah Alat  :", len(self.detail))
