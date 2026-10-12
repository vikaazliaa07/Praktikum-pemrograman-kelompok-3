"""Pengujian otomatis. Jalankan: python -m unittest -v"""

import unittest
from datetime import date

from lab.exceptions import (AturanBisnisError, DataDuplikatError,
                            DataTidakDitemukanError, ValidasiError)
from lab.models import KondisiAlat, StatusTransaksi
from lab.sistem import SistemLab

TGL = date(2026, 8, 10)


def siapkan():
    s = SistemLab()
    s.mahasiswa.tambah("M001", "Andi", "081234567890")
    s.mahasiswa.tambah("M002", "Budi", "081298765432")
    s.alat.tambah("KMR", "Kamera Digital", "perangkat multimedia", 2)
    s.alat.tambah("TRP", "Tripod", "perangkat multimedia", 3)
    s.alat.tambah("LAN", "Kabel LAN", "perangkat jaringan", 5)
    return s


class Skenario1_DataAwal(unittest.TestCase):
    def test_tambah_mahasiswa_dan_alat_berbagai_kategori(self):
        s = siapkan()
        self.assertEqual(len(s.mahasiswa.semua()), 2)
        self.assertEqual(len(s.alat.semua()), 3)
        kategori = {a.kategori for a in s.alat.semua()}
        self.assertEqual(len(kategori), 2)

    def test_nim_dan_kode_duplikat_ditolak(self):
        s = siapkan()
        with self.assertRaises(DataDuplikatError):
            s.mahasiswa.tambah("M001", "Lain", "081111111111")
        with self.assertRaises(DataDuplikatError):
            s.alat.tambah("kmr", "Kamera 2", "perangkat multimedia", 1)

    def test_validasi_input(self):
        s = siapkan()
        with self.assertRaises(ValidasiError):
            s.mahasiswa.tambah("", "X", "081234567890")
        with self.assertRaises(ValidasiError):
            s.mahasiswa.tambah("M009", "X", "abc")
        with self.assertRaises(ValidasiError):
            s.alat.tambah("X1", "X", "kategori-tak-ada", 1)
        with self.assertRaises(ValidasiError):
            s.alat.tambah("X1", "X", "perangkat jaringan", 0)

    def test_kategori_baru_tanpa_ubah_kode(self):
        s = siapkan()
        s.alat.tambah_kategori("perangkat pengukuran")
        a = s.alat.tambah("MLT", "Multimeter", "perangkat pengukuran", 4)
        self.assertEqual(a.kategori, "perangkat pengukuran")

    def test_edit_mahasiswa_dan_alat(self):
        s = siapkan()
        s.mahasiswa.edit("M001", nama="Andi P.")
        self.assertEqual(s.mahasiswa.ambil("M001").nama, "Andi P.")
        s.alat.edit("TRP", jumlah_total=5)
        self.assertEqual(s.alat.ambil("TRP").tersedia, 5)


class Skenario2_Peminjaman(unittest.TestCase):
    def test_pinjam_beberapa_alat_dalam_satu_transaksi(self):
        s = siapkan()
        trx = s.transaksi.buat(
            "M001", [("KMR", 1), ("TRP", 1), ("LAN", 2)], 7, TGL)
        self.assertEqual(len(trx.items), 3)
        self.assertEqual(trx.status, StatusTransaksi.DIPINJAM)
        self.assertEqual(s.alat.ambil("KMR").tersedia, 1)
        self.assertEqual(s.alat.ambil("KMR").dipinjam, 1)
        self.assertEqual(s.alat.ambil("LAN").tersedia, 3)
        self.assertEqual(s.mahasiswa.ambil("M001").jumlah_transaksi_aktif, 1)
        self.assertEqual((trx.batas_kembali - trx.tanggal_pinjam).days, 7)

    def test_lama_pinjam_lebih_dari_7_hari_ditolak(self):
        s = siapkan()
        with self.assertRaises(ValidasiError):
            s.transaksi.buat("M001", [("KMR", 1)], 8, TGL)
        with self.assertRaises(ValidasiError):
            s.transaksi.buat("M001", [("KMR", 1)], 0, TGL)

    def test_batas_dua_transaksi_aktif(self):
        s = siapkan()
        s.transaksi.buat("M001", [("LAN", 1)], 7, TGL)
        s.transaksi.buat("M001", [("LAN", 1)], 7, TGL)
        with self.assertRaises(AturanBisnisError):
            s.transaksi.buat("M001", [("LAN", 1)], 7, TGL)
        self.assertEqual(s.alat.ambil("LAN").tersedia, 3)   # tidak berubah

    def test_transaksi_kosong_ditolak(self):
        s = siapkan()
        with self.assertRaises(ValidasiError):
            s.transaksi.buat("M001", [], 7, TGL)


class Skenario3_AlatTidakTersedia(unittest.TestCase):
    def test_pinjam_melebihi_stok_ditolak(self):
        s = siapkan()
        with self.assertRaises(AturanBisnisError):
            s.transaksi.buat("M001", [("KMR", 3)], 7, TGL)
        self.assertEqual(s.alat.ambil("KMR").tersedia, 2)
        self.assertEqual(s.transaksi.semua(), [])

    def test_gagal_sebagian_tidak_mengubah_stok_sama_sekali(self):
        s = siapkan()
        with self.assertRaises(AturanBisnisError):
            s.transaksi.buat("M001", [("TRP", 1), ("KMR", 5)], 7, TGL)
        self.assertEqual(s.alat.ambil("TRP").tersedia, 3)   # atomik
        self.assertEqual(s.transaksi.semua(), [])

    def test_alat_yang_sedang_habis_dipinjam_orang_lain(self):
        s = siapkan()
        s.transaksi.buat("M001", [("KMR", 2)], 7, TGL)
        with self.assertRaises(AturanBisnisError):
            s.transaksi.buat("M002", [("KMR", 1)], 7, TGL)

    def test_kode_alat_tidak_ada(self):
        s = siapkan()
        with self.assertRaises(DataTidakDitemukanError):
            s.transaksi.buat("M001", [("ZZZ", 1)], 7, TGL)

    def test_id_transaksi_tidak_loncat_saat_gagal(self):
        s = siapkan()
        with self.assertRaises(AturanBisnisError):
            s.transaksi.buat("M001", [("KMR", 9)], 7, TGL)
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        self.assertEqual(trx.id, "T001")


class Skenario4_PengembalianSebagian(unittest.TestCase):
    def test_kembali_sebagian(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1), ("TRP", 2)], 7, TGL)
        s.transaksi.kembalikan(
            trx.id, [("TRP", 1, KondisiAlat.BAIK)], date(2026, 8, 12))
        self.assertEqual(trx.status, StatusTransaksi.SEBAGIAN)
        self.assertTrue(trx.aktif)
        self.assertEqual(s.alat.ambil("TRP").tersedia, 2)
        self.assertEqual(s.alat.ambil("TRP").dipinjam, 1)
        self.assertEqual(s.alat.ambil("KMR").dipinjam, 1)   # belum kembali
        self.assertEqual(trx.items["TRP"].sisa, 1)
        # masih dihitung transaksi aktif
        self.assertEqual(s.mahasiswa.ambil("M001").jumlah_transaksi_aktif, 1)
        self.assertIn("KMR", [a.kode for a in s.alat.sedang_dipinjam()])

    def test_selesai_setelah_semua_kembali(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1), ("TRP", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)
        s.transaksi.kembalikan(trx.id, [("TRP", 1, KondisiAlat.BAIK)], TGL)
        self.assertEqual(trx.status, StatusTransaksi.SELESAI)
        self.assertEqual(s.mahasiswa.ambil("M001").jumlah_transaksi_aktif, 0)
        self.assertEqual(s.alat.ambil("KMR").transaksi_aktif, set())

    def test_kembali_melebihi_sisa_ditolak_atomik(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1), ("TRP", 1)], 7, TGL)
        with self.assertRaises(AturanBisnisError):
            s.transaksi.kembalikan(
                trx.id, [("TRP", 1, KondisiAlat.BAIK),
                         ("KMR", 2, KondisiAlat.BAIK)], TGL)
        self.assertEqual(s.alat.ambil("TRP").dipinjam, 1)   # tidak berubah
        self.assertEqual(trx.pengembalian, [])

    def test_alat_bukan_bagian_transaksi_ditolak(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        with self.assertRaises(ValidasiError):
            s.transaksi.kembalikan(trx.id, [("LAN", 1, KondisiAlat.BAIK)], TGL)

    def test_transaksi_selesai_tidak_bisa_diproses_lagi(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)
        with self.assertRaises(AturanBisnisError):
            s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)


class Skenario5_KondisiAlat(unittest.TestCase):
    def test_baik_kembali_tersedia(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)
        self.assertEqual(s.alat.ambil("KMR").tersedia, 2)

    def test_rusak_ringan_dan_berat_tidak_tersedia(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1), ("TRP", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [
            ("KMR", 1, KondisiAlat.RUSAK_BERAT),
            ("TRP", 1, KondisiAlat.RUSAK_RINGAN)], TGL)
        kmr, trp = s.alat.ambil("KMR"), s.alat.ambil("TRP")
        self.assertEqual(kmr.tersedia, 1)       # 2 unit, 1 rusak berat
        self.assertEqual(kmr.rusak_berat, 1)
        self.assertEqual(trp.tersedia, 2)       # 3 unit, 1 rusak ringan
        self.assertEqual(trp.rusak_ringan, 1)
        self.assertEqual(kmr.total, 2)          # invarian stok terjaga
        kode_rusak = {a.kode for a in s.alat.rusak()}
        self.assertEqual(kode_rusak, {"KMR", "TRP"})

    def test_pengembalian_campuran_satu_alat(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("LAN", 3)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [
            ("LAN", 1, KondisiAlat.BAIK),
            ("LAN", 1, KondisiAlat.RUSAK_BERAT),
            ("LAN", 1, KondisiAlat.RUSAK_RINGAN)], TGL)
        lan = s.alat.ambil("LAN")
        self.assertEqual((lan.tersedia, lan.rusak_berat, lan.rusak_ringan,
                          lan.dipinjam), (3, 1, 1, 0))

    def test_keterlambatan_tercatat(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1), ("TRP", 1)], 7, TGL)
        rec = s.transaksi.kembalikan(
            trx.id, [("KMR", 1, KondisiAlat.BAIK)], date(2026, 8, 20))[0]
        self.assertTrue(rec.terlambat)
        self.assertEqual(rec.hari_terlambat, 3)     # batas 17 Agustus
        self.assertEqual(trx.hari_terlambat(date(2026, 8, 20)), 3)
        rec2 = s.transaksi.kembalikan(
            trx.id, [("TRP", 1, KondisiAlat.BAIK)], date(2026, 8, 17))[0]
        self.assertFalse(rec2.terlambat)


class Skenario6_Penghapusan(unittest.TestCase):
    def test_mahasiswa_dengan_transaksi_aktif_tidak_bisa_dihapus(self):
        s = siapkan()
        s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        with self.assertRaises(AturanBisnisError):
            s.mahasiswa.hapus("M001")
        self.assertIsNotNone(s.mahasiswa.ambil("M001"))

    def test_alat_dalam_transaksi_aktif_tidak_bisa_dihapus(self):
        s = siapkan()
        s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        with self.assertRaises(AturanBisnisError):
            s.alat.hapus("KMR")

    def test_boleh_dihapus_setelah_transaksi_selesai_riwayat_tetap(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)
        s.mahasiswa.hapus("M001")
        s.alat.hapus("KMR")
        riwayat = s.transaksi.riwayat("M001")
        self.assertEqual(len(riwayat), 1)
        self.assertEqual(riwayat[0].nama_peminjam, "Andi")
        self.assertEqual(riwayat[0].items["KMR"].nama_alat, "Kamera Digital")

    def test_alat_tanpa_transaksi_bisa_dihapus(self):
        s = siapkan()
        s.alat.hapus("LAN")
        with self.assertRaises(DataTidakDitemukanError):
            s.alat.ambil("LAN")


class Tantangan_A_Pencarian(unittest.TestCase):
    def test_cari_kode_nama_kategori(self):
        s = siapkan()
        self.assertEqual([a.kode for a in s.alat.cari(kode="kmr")], ["KMR"])
        self.assertEqual([a.kode for a in s.alat.cari(nama="pod")], ["TRP"])
        self.assertEqual(
            {a.kode for a in s.alat.cari(kategori="multimedia")},
            {"KMR", "TRP"})
        self.assertEqual(
            [a.kode for a in s.alat.cari(nama="kamera", kategori="multimedia")],
            ["KMR"])
        with self.assertRaises(ValidasiError):
            s.alat.cari()


class Tantangan_B_Statistik(unittest.TestCase):
    def test_statistik(self):
        s = siapkan()
        t1 = s.transaksi.buat("M001", [("KMR", 1), ("LAN", 2)], 7, TGL)
        s.transaksi.buat("M001", [("LAN", 1)], 7, TGL)
        s.transaksi.kembalikan(
            t1.id, [("KMR", 1, KondisiAlat.BAIK),
                    ("LAN", 2, KondisiAlat.BAIK)], TGL)
        s.transaksi.buat("M002", [("LAN", 1)], 7, TGL)
        st = s.statistik
        self.assertEqual(st.jumlah_selesai(), 1)
        self.assertEqual(st.jumlah_aktif(), 2)
        self.assertEqual(st.alat_terpopuler()[0], ("LAN", "Kabel LAN", 4))
        self.assertEqual(st.mahasiswa_teraktif()[0], ("M001", "Andi", 2))


class Tantangan_C_Pemeliharaan(unittest.TestCase):
    def test_rusak_berat_ke_pemeliharaan_lalu_tersedia(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 1)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.RUSAK_BERAT)], TGL)
        kmr = s.alat.ambil("KMR")
        s.alat.mulai_pemeliharaan("KMR", 1, KondisiAlat.RUSAK_BERAT)
        self.assertEqual((kmr.rusak_berat, kmr.pemeliharaan, kmr.tersedia),
                         (0, 1, 1))
        s.alat.selesai_pemeliharaan("KMR", 1)
        self.assertEqual((kmr.pemeliharaan, kmr.tersedia), (0, 2))
        self.assertEqual(kmr.total, 2)

    def test_pemeliharaan_melebihi_jumlah_rusak_ditolak(self):
        s = siapkan()
        with self.assertRaises(AturanBisnisError):
            s.alat.mulai_pemeliharaan("KMR", 1, KondisiAlat.RUSAK_BERAT)


class Tantangan_D_Log(unittest.TestCase):
    def test_log_tersimpan_dalam_list(self):
        s = siapkan()
        trx = s.transaksi.buat("M001", [("KMR", 2)], 7, TGL)
        s.transaksi.kembalikan(trx.id, [("KMR", 1, KondisiAlat.BAIK)], TGL)
        pesan = [e["pesan"] for e in s.log.semua()]
        self.assertIn("Mahasiswa M001 ditambahkan", pesan)
        self.assertIn(f"Transaksi {trx.id} dibuat oleh M001", pesan)
        self.assertTrue(any("2 unit Kamera Digital dipinjam" in p for p in pesan))
        self.assertTrue(any("1 unit Kamera Digital dikembalikan" in p for p in pesan))


if __name__ == "__main__":
    unittest.main()
