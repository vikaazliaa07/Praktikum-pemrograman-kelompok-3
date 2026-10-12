# Refleksi Kelompok dan Rencana Perbaikan

> **DRAFT analisis teknis.** Poin-poin di bawah adalah kelemahan yang nyata
> pada kode ini, sebagai bahan awal. Sesuaikan dengan pengalaman kelompok
> (kendala saat pengembangan, temuan code review) dan tulis ulang dengan
> bahasa sendiri. Bagian "perubahan setelah code review" wajib diisi dari
> review yang sungguh diterima.

## 1. Kelemahan utama rancangan

- **Stok berbasis jumlah, bukan per unit.** Tidak bisa menjawab "unit
  Multimeter nomor berapa yang rusak" atau menelusuri riwayat satu unit.
- **Data turunan yang harus disinkronkan manual.** `transaksi_aktif` pada
  `Mahasiswa` dan `Alat` diubah hanya oleh `TransaksiService`; jika ada
  kode lain yang mengubahnya, aturan penghapusan dan batas transaksi bisa
  salah. Belum ada mekanisme yang memaksa ini.
- **Tidak ada persistensi.** Semua data hilang saat program ditutup
  (sesuai batasan tugas, tetapi menjadi kelemahan sebagai sistem nyata).
- **Unit rusak ringan tanpa jalur pemulihan** selain pemeliharaan; ini
  celah pada spesifikasi yang kami tutup dengan asumsi.

## 2. Bagian yang pertama diperbaiki bila menjadi sistem nyata

1. Persistensi (database) dan pemisahan akses data ke lapisan repository.
2. Tanggal pengembalian memakai tanggal sistem (saat ini bisa diisi manual
   demi demonstrasi keterlambatan).
3. Autentikasi dan peran pengguna (petugas vs mahasiswa).

## 3. Class dengan tanggung jawab berlebih?

- `MenuCLI` (~300 baris) mencampur alur menu, pembacaan input, dan format
  tampilan. Sebaiknya dipecah per menu, dan tampilan dipisah dari alur.
- `TransaksiService` menangani pembuatan, pengembalian, dan query
  (riwayat/pencarian). Masih wajar, tetapi query bisa dipisah bila
  bertambah.
- `AlatService` memegang CRUD, kategori, pencarian, dan pemeliharaan;
  pemeliharaan adalah kandidat untuk dipisah.

## 4. Ketepatan struktur data collection

| Data | Struktur | Penilaian |
|------|----------|-----------|
| Mahasiswa, alat, transaksi | `dict` berkunci NIM/kode/id | Tepat: akses O(1) berdasarkan kunci |
| Isi transaksi | `dict[kode -> item]` | Tepat: mencegah duplikat kode dalam satu transaksi |
| Transaksi aktif | `set[id]` | Tepat: cek keanggotaan dan hapus O(1) |
| Kategori | `list[str]` | Cukup; `set` lebih cocok untuk cek keanggotaan, tetapi list menjaga urutan tampil |
| Log | `list[dict]` | Tepat untuk data yang bertambah berurutan |
| Pencarian sebagian nama/kategori | pemindaian linear O(n) | Cukup untuk ratusan data; perlu index bila puluhan ribu |

## 5. Duplikasi kode

- Normalisasi kode (`strip().upper()`) muncul di beberapa tempat
  (`AlatService.ambil`, `TransaksiService.buat/kembalikan`).
- Pola "loop minta kode + jumlah sampai kosong" diulang di
  `buat_transaksi` dan `proses_pengembalian` pada `MenuCLI`.
- Pola pesan "Pilihan tidak valid" dan `sorted(...)` untuk daftar diulang
  di banyak method.

## 6. Membuat desain lebih scalable

- **Kategori/aturan baru:** aturan dipindah dari method service ke objek
  aturan terpisah (mis. daftar `AturanPeminjaman` yang dijalankan berurutan)
  agar aturan baru tidak mengubah `TransaksiService.buat()`.
- **Denda keterlambatan:** `PengembalianRecord.hari_terlambat` sudah tersedia
  sebagai titik masuk; tambahkan class penghitung denda tanpa mengubah
  alur pengembalian.
- **Jenis pengguna baru:** buat class induk `Pengguna` dan turunkan
  `Mahasiswa` (saat ini `Mahasiswa` class konkret dan `nim` dipakai sebagai
  kunci di banyak tempat, sehingga perubahan ini butuh refactoring cukup luas).
- **10.000 alat / 20.000 mahasiswa:** akses per kunci sudah efisien;
  `cari_berdasarkan_mahasiswa` dan pencarian sebagian nama masih linear.
- **Database:** perlu lapisan repository; saat ini service memegang dict
  secara langsung sehingga migrasi menyentuh semua service.

## 7. Perubahan setelah menerima code review (ISI SENDIRI)

| Temuan | Perubahan yang dilakukan |
|--------|--------------------------|
| [ISI] | [ISI] |
