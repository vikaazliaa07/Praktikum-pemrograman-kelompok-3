# Sistem Pengelolaan Peminjaman Peralatan Laboratorium

Proyek I - Praktikum Pemrograman Dasar. Aplikasi konsol berbasis Python (OOP) untuk mengelola
peminjaman alat laboratorium oleh mahasiswa. Data disimpan di `dict` dan `list` selama program
berjalan (tanpa database).

## Anggota Kelompok

| Nama | NIM | Akun GitHub |
|---|---|---|
| [isi] | [isi] | [isi] |

## Deskripsi Sistem

Aplikasi mencatat mahasiswa, alat, transaksi peminjaman (satu transaksi dapat berisi banyak alat),
dan pengembalian (boleh sebagian, dengan kondisi baik / rusak ringan / rusak berat).

Aturan bisnis dan lokasi penerapannya:

| Aturan | Diterapkan di |
|---|---|
| 1. Alat tidak tersedia tidak bisa dipinjam | `Peralatan.cek_ketersediaan()`, dicek di `TransaksiManager.buat_transaksi()` |
| 2. Maksimal 2 transaksi aktif per mahasiswa | `Mahasiswa.bisa_meminjam()` |
| 3. Isi transaksi dinamis | `Transaksi.daftar_detail` (List) |
| 4. Pengembalian sebagian | `Transaksi.kembalikan_alat()` dan `perbarui_status()` |
| 5. Alat rusak tidak tersedia | `Peralatan.terima_kembali(kondisi)` |
| 6. Data aktif tidak boleh dihapus | `MahasiswaManager.hapus_mahasiswa()`, `PeralatanManager.hapus_alat()` |

Tantangan yang dikerjakan: **A (Pencarian Fleksibel)** pada `PeralatanManager.cari_alat()` dan
**B (Statistik Peminjaman)** pada `TransaksiManager.tampilkan_statistik()`.

## Struktur Program

```
peminjaman_lab/
├── main.py                  # titik masuk
├── aplikasi.py              # AplikasiLab: menu interaktif
├── data_contoh.py           # data contoh untuk demo (menu 20)
├── models/
│   ├── mahasiswa.py         # Mahasiswa
│   ├── peralatan.py         # Peralatan
│   ├── transaksi.py         # Transaksi
│   └── detail_peminjaman.py # Detail_Peminjaman
├── managers/
│   ├── mahasiswa_manager.py # MahasiswaManager
│   ├── peralatan_manager.py # PeralatanManager
│   └── transaksi_manager.py # TransaksiManager
├── tests/test_skenario.py   # pengujian 6 skenario wajib + aturan tambahan
└── docs/                    # UML final (.drawio dan .png)
```

Struktur data utama: `MahasiswaManager.daftar_mahasiswa` (`Dict[nim, Mahasiswa]`),
`PeralatanManager.daftar_alat` (`Dict[kode, Peralatan]`), `TransaksiManager.daftar_transaksi`
(`Dict[id, Transaksi]`), dan `Transaksi.daftar_detail` (`List[Detail_Peminjaman]`).

## Cara Menjalankan

Membutuhkan Python 3.8+ (tanpa library tambahan).

```
python main.py
```

Untuk demo cepat, pilih menu **20** (Muat data contoh) lalu menu 11 (Buat peminjaman).

Menjalankan pengujian:

```
python -m unittest discover -s tests -v
```

## Pembagian Kontribusi

| Anggota | Kontribusi |
|---|---|
| [isi] | [isi sesuai riwayat commit] |
