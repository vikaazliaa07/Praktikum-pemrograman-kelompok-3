"""Class Detail_Peminjaman: satu alat dalam satu transaksi + data pengembaliannya."""


class Detail_Peminjaman:
    def __init__(self, peralatan):
        self.peralatan = peralatan
        self.sudah_kembali = False
        self.kondisi_kembali = None
        self.tanggal_kembali = None

    def catat_pengembalian(self, kondisi, tanggal):
        if self.sudah_kembali:
            raise ValueError(f"Alat {self.peralatan.kode_alat} sudah dikembalikan sebelumnya.")
        self.sudah_kembali = True
        self.kondisi_kembali = kondisi
        self.tanggal_kembali = tanggal

    def tampilkan_info(self):
        alat = self.peralatan
        if self.sudah_kembali:
            ket = f"dikembalikan {self.tanggal_kembali.isoformat()} (kondisi: {self.kondisi_kembali})"
        else:
            ket = "belum dikembalikan"
        print(f"      - [{alat.kode_alat}] {alat.nama_alat}: {ket}")
