"""Pengujian otomatis: 6 skenario wajib + aturan bisnis tambahan.
Jalankan dari folder utama:  python -m unittest discover -s tests -v
"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.mahasiswa_manager import MahasiswaManager
from managers.peralatan_manager import PeralatanManager
from managers.transaksi_manager import TransaksiManager


class DasarTes(unittest.TestCase):
    def setUp(self):
        self.mm = MahasiswaManager()
        self.pm = PeralatanManager()
        self.tm = TransaksiManager(self.mm, self.pm)
        # Skenario 1: beberapa mahasiswa dan beberapa jenis alat
        for nim, nama in (("K001", "Andi"), ("K002", "Bella")):
            self.mm.tambah_mahasiswa(nim, nama, "081234567890")
        for kode, nama, kat in (("AL1", "Kamera Digital", "perangkat multimedia"),
                                ("AL2", "Tripod", "perangkat multimedia"),
                                ("AL3", "Kabel LAN", "perangkat jaringan"),
                                ("AL4", "Laptop", "perangkat komputasi"),
                                ("AL5", "Multimeter", "alat ukur")):
            self.pm.tambah_alat(kode, nama, kat)


class TestSkenarioWajib(DasarTes):
    def test_skenario1_data_dan_kategori_baru(self):
        self.assertEqual(len(self.mm.daftar_mahasiswa), 2)
        self.assertEqual(len(self.pm.daftar_alat), 5)
        self.pm.tambah_alat("AL6", "Proyektor", "kategori baru sama sekali")  # tanpa ubah struktur
        self.assertIn("AL6", self.pm.daftar_alat)

    def test_skenario2_pinjam_beberapa_alat_satu_transaksi(self):
        trx = self.tm.buat_transaksi("K001", ["AL1", "AL2", "AL3"])
        self.assertEqual(len(trx.daftar_detail), 3)
        for kode in ("AL1", "AL2", "AL3"):
            self.assertTrue(self.pm.ambil_alat(kode).sedang_dipinjam)
            self.assertFalse(self.pm.ambil_alat(kode).cek_ketersediaan())
        self.assertTrue(self.pm.ambil_alat("AL4").cek_ketersediaan())
        self.assertEqual(self.mm.ambil_mahasiswa("K001").jumlah_transaksi_aktif, 1)
        self.assertEqual(trx.status, "dipinjam")
        self.assertEqual(trx.batas_kembali - trx.tanggal_pinjam, timedelta(days=7))

    def test_skenario3_alat_tidak_tersedia_ditolak(self):
        self.tm.buat_transaksi("K001", ["AL1"])
        with self.assertRaises(ValueError):
            self.tm.buat_transaksi("K002", ["AL2", "AL1"])   # AL1 sedang dipinjam
        # penolakan harus atomik: AL2 tidak boleh ikut terpinjam, tidak ada transaksi baru
        self.assertFalse(self.pm.ambil_alat("AL2").sedang_dipinjam)
        self.assertEqual(len(self.tm.daftar_transaksi), 1)
        self.assertEqual(self.mm.ambil_mahasiswa("K002").jumlah_transaksi_aktif, 0)

    def test_skenario4_pengembalian_sebagian(self):
        trx = self.tm.buat_transaksi("K001", ["AL1", "AL2", "AL3"])
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")
        self.assertEqual(trx.status, "sebagian dikembalikan")
        self.assertTrue(trx.masih_aktif())
        self.assertTrue(self.pm.ambil_alat("AL1").cek_ketersediaan())
        self.assertTrue(self.pm.ambil_alat("AL2").sedang_dipinjam)
        self.assertEqual(self.mm.ambil_mahasiswa("K001").jumlah_transaksi_aktif, 1)  # masih aktif
        self.tm.proses_pengembalian(trx.id_transaksi, "AL2", "baik")
        self.tm.proses_pengembalian(trx.id_transaksi, "AL3", "baik")
        self.assertEqual(trx.status, "selesai")
        self.assertEqual(self.mm.ambil_mahasiswa("K001").jumlah_transaksi_aktif, 0)

    def test_skenario5_kondisi_rusak_tidak_tersedia(self):
        trx = self.tm.buat_transaksi("K001", ["AL1", "AL2", "AL3"])
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "rusak berat")
        self.tm.proses_pengembalian(trx.id_transaksi, "AL2", "rusak ringan")
        self.tm.proses_pengembalian(trx.id_transaksi, "AL3", "baik")
        self.assertFalse(self.pm.ambil_alat("AL1").cek_ketersediaan())
        self.assertFalse(self.pm.ambil_alat("AL2").cek_ketersediaan())
        self.assertTrue(self.pm.ambil_alat("AL3").cek_ketersediaan())
        self.assertEqual({a.kode_alat for a in self.pm.tampilkan_alat_rusak()}, {"AL1", "AL2"})
        with self.assertRaises(ValueError):                    # tidak bisa dipinjam lagi
            self.tm.buat_transaksi("K002", ["AL1"])

    def test_skenario6_hapus_mahasiswa_aktif_ditolak(self):
        trx = self.tm.buat_transaksi("K001", ["AL1"])
        with self.assertRaises(ValueError):
            self.mm.hapus_mahasiswa("K001")
        self.assertIn("K001", self.mm.daftar_mahasiswa)
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")
        self.mm.hapus_mahasiswa("K001")                        # boleh setelah selesai
        self.assertNotIn("K001", self.mm.daftar_mahasiswa)


class TestAturanTambahan(DasarTes):
    def test_batas_dua_transaksi_aktif(self):
        t1 = self.tm.buat_transaksi("K001", ["AL1"])
        self.tm.buat_transaksi("K001", ["AL2"])
        with self.assertRaises(ValueError):
            self.tm.buat_transaksi("K001", ["AL3"])
        self.tm.proses_pengembalian(t1.id_transaksi, "AL1", "baik")
        self.tm.buat_transaksi("K001", ["AL3"])                # boleh lagi setelah satu selesai

    def test_hapus_alat_dipinjam_ditolak(self):
        trx = self.tm.buat_transaksi("K001", ["AL1"])
        with self.assertRaises(ValueError):
            self.pm.hapus_alat("AL1")
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")
        self.pm.hapus_alat("AL1")
        self.assertNotIn("AL1", self.pm.daftar_alat)

    def test_alat_tidak_bisa_dikembalikan_dua_kali(self):
        trx = self.tm.buat_transaksi("K001", ["AL1", "AL2"])
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")
        with self.assertRaises(ValueError):
            self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")

    def test_kondisi_tidak_valid_ditolak_tanpa_efek(self):
        trx = self.tm.buat_transaksi("K001", ["AL1"])
        with self.assertRaises(ValueError):
            self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "hancur")
        self.assertTrue(self.pm.ambil_alat("AL1").sedang_dipinjam)
        self.assertFalse(trx.daftar_detail[0].sudah_kembali)

    def test_keterlambatan(self):
        trx = self.tm.buat_transaksi("K001", ["AL1"], date.today() - timedelta(days=10))
        self.assertTrue(trx.terlambat())
        self.tm.proses_pengembalian(trx.id_transaksi, "AL1", "baik")
        self.assertFalse(trx.terlambat())

    def test_pencarian_fleksibel(self):
        self.assertEqual({a.kode_alat for a in self.pm.cari_alat("al1")}, {"AL1"})
        self.assertEqual({a.kode_alat for a in self.pm.cari_alat("kamera")}, {"AL1"})
        self.assertEqual({a.kode_alat for a in self.pm.cari_alat("jaringan")}, {"AL3"})

    def test_edit_dan_duplikat(self):
        self.mm.edit_mahasiswa("K001", nama="Andi Baru")
        self.assertEqual(self.mm.ambil_mahasiswa("K001").nama, "Andi Baru")
        with self.assertRaises(ValueError):
            self.mm.tambah_mahasiswa("K001", "Duplikat", "081234567890")
        with self.assertRaises(ValueError):
            self.pm.tambah_alat("AL1", "Duplikat", "x")

    def test_statistik_dan_riwayat(self):
        t1 = self.tm.buat_transaksi("K001", ["AL1", "AL2"])
        self.tm.proses_pengembalian(t1.id_transaksi, "AL1", "baik")
        self.tm.proses_pengembalian(t1.id_transaksi, "AL2", "baik")
        self.tm.buat_transaksi("K001", ["AL1"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.tm.tampilkan_statistik()
            self.tm.tampilkan_riwayat_mahasiswa("K001")
        teks = buf.getvalue()
        self.assertIn("Transaksi selesai: 1 | Transaksi aktif: 1", teks)
        self.assertIn("AL1 (Kamera Digital) (2x)", teks)
        self.assertIn("K001 (2x)", teks)


if __name__ == "__main__":
    unittest.main()
