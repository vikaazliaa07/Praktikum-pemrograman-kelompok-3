"""TransaksiManager: membuat transaksi, memproses pengembalian, riwayat, statistik."""
from collections import Counter

from models.transaksi import Transaksi


class TransaksiManager:
    def __init__(self, mahasiswa_mgr, alat_mgr):
        self.daftar_transaksi = {}
        self.mahasiswa_mgr = mahasiswa_mgr
        self.alat_mgr = alat_mgr
        self._counter = 0

    def _id_baru(self):
        self._counter += 1
        return f"T{self._counter:03d}"

    def ambil_transaksi(self, id_transaksi):
        trx = self.daftar_transaksi.get(id_transaksi.strip().upper())
        if trx is None:
            raise ValueError(f"Transaksi {id_transaksi} tidak ditemukan.")
        return trx

    def buat_transaksi(self, nim, daftar_kode_alat, tanggal=None):
        """Semua validasi dilakukan DULU; data baru diubah hanya jika seluruhnya lolos."""
        mhs = self.mahasiswa_mgr.ambil_mahasiswa(nim)
        if not mhs.bisa_meminjam():                                     # Aturan 2
            raise ValueError(f"Mahasiswa {mhs.nim} sudah memiliki "
                             f"{mhs.MAKS_TRANSAKSI_AKTIF} transaksi aktif.")
        kode_unik = []
        for kode in (k.strip() for k in daftar_kode_alat):
            if kode and kode not in kode_unik:
                kode_unik.append(kode)
        if not kode_unik:
            raise ValueError("Pilih minimal satu alat.")

        daftar_alat, masalah = [], []
        for kode in kode_unik:
            try:
                alat = self.alat_mgr.ambil_alat(kode)
            except ValueError as e:
                masalah.append(str(e))
                continue
            if not alat.cek_ketersediaan():                              # Aturan 1
                masalah.append(f"Alat {kode} ({alat.nama_alat}) tidak tersedia: {alat.status_teks()}.")
            else:
                daftar_alat.append(alat)
        if masalah:
            raise ValueError("Transaksi ditolak. " + " ".join(masalah))

        trx = Transaksi(self._id_baru(), mhs, tanggal)
        for alat in daftar_alat:
            trx.tambah_detail(alat)
            alat.pinjam()
        mhs.tambah_transaksi_aktif()
        self.daftar_transaksi[trx.id_transaksi] = trx
        return trx

    def proses_pengembalian(self, id_transaksi, kode_alat, kondisi, tanggal=None):
        trx = self.ambil_transaksi(id_transaksi)
        trx.kembalikan_alat(kode_alat.strip(), kondisi, tanggal)
        return trx

    def cari_transaksi_mahasiswa(self, nim):
        hasil = [t for t in self.daftar_transaksi.values() if t.mahasiswa.nim == nim.strip()]
        if not hasil:
            print("  (tidak ada transaksi untuk mahasiswa tersebut)")
        for t in hasil:
            t.tampilkan_info()
        return hasil

    def tampilkan_riwayat_mahasiswa(self, nim):
        mhs = self.mahasiswa_mgr.ambil_mahasiswa(nim)
        print(f"  Riwayat peminjaman {mhs.nim} - {mhs.nama}:")
        return self.cari_transaksi_mahasiswa(nim)

    def tampilkan_transaksi(self):
        if not self.daftar_transaksi:
            print("  (belum ada transaksi)")
        for t in self.daftar_transaksi.values():
            t.tampilkan_info()

    def tampilkan_statistik(self):
        """Tantangan B: statistik peminjaman."""
        trxs = list(self.daftar_transaksi.values())
        selesai = sum(1 for t in trxs if not t.masih_aktif())
        print(f"  Transaksi selesai: {selesai} | Transaksi aktif: {len(trxs) - selesai}")
        if not trxs:
            return
        hitung_alat = Counter(d.peralatan.kode_alat for t in trxs for d in t.daftar_detail)
        hitung_mhs = Counter(t.mahasiswa.nim for t in trxs)

        def nama_alat(kode):
            alat = self.alat_mgr.daftar_alat.get(kode)
            return f"{kode} ({alat.nama_alat})" if alat else kode

        for judul, hitung, nama in (("Alat paling sering dipinjam", hitung_alat, nama_alat),
                                    ("Mahasiswa paling sering meminjam", hitung_mhs, lambda k: k)):
            tertinggi = max(hitung.values())
            pemenang = [nama(k) for k, v in hitung.items() if v == tertinggi]
            print(f"  {judul}: {', '.join(pemenang)} ({tertinggi}x)")
