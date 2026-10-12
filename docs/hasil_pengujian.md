# Dokumen Hasil Pengujian

Pengujian otomatis: `python -m unittest -v` (32 tes, seluruhnya **OK** pada
saat dokumen ini dibuat). Jalankan ulang di komputer kelompok dan lampirkan
tangkapan layar Anda sendiri sebagai bukti.

## Ringkasan skenario wajib

| Skenario | Langkah | Hasil yang diharapkan | Tes otomatis | Status |
|----------|---------|-----------------------|--------------|--------|
| 1 | Tambah beberapa mahasiswa dan alat berbagai kategori | Data tersimpan; duplikat NIM/kode ditolak; input tidak valid ditolak; kategori baru bisa ditambah | `Skenario1_DataAwal` (5 tes) | PASS |
| 2 | Satu mahasiswa meminjam beberapa alat dalam satu transaksi | Transaksi berisi semua alat; stok tersedia turun, dipinjam naik; batas kembali = +7 hari; maks 2 transaksi aktif; lama > 7 hari ditolak | `Skenario2_Peminjaman` (4 tes) | PASS |
| 3 | Meminjam alat yang tidak tersedia | Transaksi ditolak; stok tidak berubah, termasuk saat hanya sebagian item yang bermasalah (atomik) | `Skenario3_AlatTidakTersedia` (5 tes) | PASS |
| 4 | Pengembalian sebagian | Status "sebagian dikembalikan"; transaksi tetap aktif; stok alat yang kembali naik; alat yang belum kembali tetap tercatat dipinjam | `Skenario4_PengembalianSebagian` (5 tes) | PASS |
| 5 | Alat kembali rusak ringan/berat | Tidak masuk stok tersedia; baik langsung tersedia; total stok tetap konsisten | `Skenario5_KondisiAlat` (4 tes) | PASS |
| 6 | Hapus mahasiswa/alat yang masih punya transaksi aktif | Operasi ditolak; setelah transaksi selesai boleh dihapus dan riwayat tetap terbaca | `Skenario6_Penghapusan` (4 tes) | PASS |
| Tantangan A-D | Pencarian, statistik, pemeliharaan, log | Sesuai spesifikasi | `Tantangan_A..D` (5 tes) | PASS |

## Output pengujian otomatis

```
test_edit_mahasiswa_dan_alat ... ok
test_kategori_baru_tanpa_ubah_kode ... ok
test_nim_dan_kode_duplikat_ditolak ... ok
test_tambah_mahasiswa_dan_alat_berbagai_kategori ... ok
test_validasi_input ... ok
test_batas_dua_transaksi_aktif ... ok
test_lama_pinjam_lebih_dari_7_hari_ditolak ... ok
test_pinjam_beberapa_alat_dalam_satu_transaksi ... ok
test_transaksi_kosong_ditolak ... ok
test_alat_yang_sedang_habis_dipinjam_orang_lain ... ok
test_gagal_sebagian_tidak_mengubah_stok_sama_sekali ... ok
test_id_transaksi_tidak_loncat_saat_gagal ... ok
test_kode_alat_tidak_ada ... ok
test_pinjam_melebihi_stok_ditolak ... ok
test_alat_bukan_bagian_transaksi_ditolak ... ok
test_kembali_melebihi_sisa_ditolak_atomik ... ok
test_kembali_sebagian ... ok
test_selesai_setelah_semua_kembali ... ok
test_transaksi_selesai_tidak_bisa_diproses_lagi ... ok
test_baik_kembali_tersedia ... ok
test_keterlambatan_tercatat ... ok
test_pengembalian_campuran_satu_alat ... ok
test_rusak_ringan_dan_berat_tidak_tersedia ... ok
test_alat_dalam_transaksi_aktif_tidak_bisa_dihapus ... ok
test_alat_tanpa_transaksi_bisa_dihapus ... ok
test_boleh_dihapus_setelah_transaksi_selesai_riwayat_tetap ... ok
test_mahasiswa_dengan_transaksi_aktif_tidak_bisa_dihapus ... ok
test_cari_kode_nama_kategori ... ok
test_statistik ... ok
test_pemeliharaan_melebihi_jumlah_rusak_ditolak ... ok
test_rusak_berat_ke_pemeliharaan_lalu_tersedia ... ok
test_log_tersimpan_dalam_list ... ok

----------------------------------------------------------------------
Ran 32 tests in 0.002s

OK
```

## Pengujian manual melalui menu (cuplikan)

Data contoh (menu 14), lalu:

1. Menu 3: M001 meminjam 1 Laptop, 1 Kamera Digital, 2 Kabel LAN -> `T001` dibuat, batas kembali +7 hari.
2. Menu 3: M002 meminjam 3 Kamera Digital (tersedia 2) -> `[GAGAL] Alat tidak tersedia -> Kamera Digital (MLT01): diminta 3, tersedia 2`.
3. Menu 5: `T001`, Kamera Digital 1 unit *rusak berat*, Kabel LAN 1 unit *baik*, tanggal 2026-09-30 -> status `SEBAGIAN DIKEMBALIKAN`, keterlambatan 2 hari tercatat.
4. Menu 1 -> hapus M001 -> `[GAGAL] ... masih memiliki transaksi aktif (T001)`.
5. Menu 9 (alat rusak): Kamera Digital muncul dengan "1 rusak berat", tersedia tetap 2 dari 3.

## Keterbatasan pengujian

- Belum ada uji beban (skala 10.000 alat / 20.000 mahasiswa).
- Lapisan `MenuCLI` diuji manual, tidak otomatis.
- Data tidak persisten; tidak ada uji penyimpanan.
