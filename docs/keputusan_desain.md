# Dokumen Keputusan Desain

> **Catatan penggunaan.** Bagian A berisi alasan teknis atas struktur class
> pada kode. Bagian B **harus diisi kelompok sendiri** berdasarkan diskusi
> yang benar-benar terjadi (tugas mensyaratkan perbandingan rancangan
> individu). Jangan diisi dengan proses yang tidak terjadi.

## A. Alasan Struktur Class

### Pembagian tanggung jawab

| Lapisan | Class | Tanggung jawab |
|---------|-------|----------------|
| Entitas | `Mahasiswa`, `Alat`, `Transaksi`, `ItemPeminjaman`, `PengembalianRecord` | Menyimpan data dan menjaga aturan yang hanya menyangkut dirinya (mis. invarian stok di `Alat`) |
| Service | `MahasiswaService`, `AlatService`, `TransaksiService`, `StatistikService` | Koleksi data (dict) + aturan yang melibatkan banyak objek (batas transaksi aktif, validasi atomik) |
| Pendukung | `ActivityLog`, `SistemLab` | Log aktivitas; perakit service |
| UI | `MenuCLI` | Satu-satunya class yang memakai `input()`/`print()` |

Alasan: logika bisnis tidak bergantung pada tampilan, sehingga dapat diuji
tanpa menu (lihat `tests/`) dan UI bisa diganti (web/GUI) tanpa menyentuh
aturan bisnis.

### Kerja sama antarclass (contoh alur "buat transaksi")

1. `MenuCLI` membaca input, memanggil `TransaksiService.buat()`.
2. `TransaksiService` mengambil `Mahasiswa` (via `MahasiswaService`), cek
   Aturan 2, lalu mengambil setiap `Alat` (via `AlatService`) dan cek stok
   (Aturan 1). **Semua validasi selesai sebelum stok diubah.**
3. Jika lolos: `Alat.pinjam()` mengubah stok, `Transaksi` dibuat dengan
   `ItemPeminjaman` per alat, id transaksi dicatat ke `Mahasiswa` dan `Alat`.
4. `ActivityLog.catat()` merekam aktivitas.

### Keputusan utama

| # | Keputusan | Alasan | Konsekuensi/risiko |
|---|-----------|--------|--------------------|
| 1 | `Alat` = satu **jenis** alat dengan stok per kondisi (tersedia, dipinjam, rusak ringan, rusak berat, pemeliharaan), bukan satu objek per unit | Contoh log pada tugas ("dua unit Multimeter dipinjam") dan Aturan 5 ("jumlah alat tersedia") bekerja pada jumlah unit | Riwayat per unit fisik tidak ada; hanya jumlah. Atribut "kondisi alat" menjadi properti turunan |
| 2 | Kategori disimpan sebagai `list[str]`, bukan subclass | Syarat: kategori baru tanpa mengubah struktur utama | Kategori tidak bisa punya atribut/aturan khusus |
| 3 | Isi transaksi = `dict[kode -> ItemPeminjaman]` | Aturan 3: jumlah/jenis alat dinamis, tanpa variabel per alat | - |
| 4 | Status transaksi **dihitung** dari item, tidak disimpan | Mencegah status tidak sinkron dengan data item | Dihitung ulang tiap akses (murah pada skala ini) |
| 5 | `Mahasiswa.transaksi_aktif` dan `Alat.transaksi_aktif` berupa `set` id transaksi | Cek Aturan 2 dan Aturan 6 jadi O(1) dan tidak memerlukan referensi silang antar service | Data turunan yang harus disinkronkan; hanya `TransaksiService` yang boleh mengubahnya |
| 6 | Transaksi menyimpan **snapshot** nama peminjam dan nama alat | Riwayat tetap terbaca meski mahasiswa/alat sudah dihapus setelah transaksi selesai | Duplikasi data kecil |
| 7 | Pembuatan transaksi dan pengembalian bersifat **atomik** | Kegagalan di item ke-3 tidak boleh meninggalkan stok item 1-2 sudah berkurang | Validasi dan penerapan dipisah dalam dua fase |
| 8 | Batas aturan di `konfigurasi.py` | Aturan baru/berubah cukup diubah di satu tempat | - |

### Alternatif yang dipertimbangkan dan tidak dipilih

| Alternatif | Alasan tidak dipilih |
|------------|----------------------|
| Satu objek `Alat` per unit fisik | Mengharuskan pengelompokan tambahan untuk "n unit jenis X"; lebih banyak objek. Layak dipertimbangkan bila riwayat per unit dibutuhkan |
| Hierarki class per kategori (`PerangkatKomputasi(Alat)`, dst.) | Kategori baru mengharuskan menambah class; bertentangan dengan syarat |
| Satu class besar `Lab` yang mengerjakan semuanya | Tanggung jawab bercampur, sulit diuji |
| Lapisan Repository terpisah untuk setiap koleksi | Terlalu berat untuk lingkup tugas; namun ini langkah pertama bila nanti migrasi ke database |
| Menghitung transaksi aktif dengan memindai semua transaksi | O(jumlah transaksi) setiap pengecekan |

### Asumsi terhadap soal yang ambigu

- **Alat rusak ringan** tidak dapat dipinjam (Aturan 5) tetapi soal tidak
  menyebut cara memulihkannya. Diasumsikan pemeliharaan (Tantangan C)
  berlaku untuk rusak ringan **dan** rusak berat.
- **Penghapusan alat** (Aturan 6) diterapkan harfiah: alat ditolak dihapus
  selama transaksi yang memuatnya belum selesai, walaupun item alat itu
  sendiri sudah dikembalikan.
- **Tanggal pengembalian** dapat diisi manual di menu agar keterlambatan
  dapat didemonstrasikan; pada sistem nyata sebaiknya memakai tanggal sistem.
- **Statistik "alat paling sering dipinjam"** dihitung dari total unit,
  bukan jumlah transaksi.

## B. Keputusan Kelompok (ISI SENDIRI)

| Pertanyaan | Jawaban kelompok |
|------------|------------------|
| Rancangan siapa yang menjadi dasar solusi? | [ISI] |
| Bagian apa yang diambil/dimodifikasi dari rancangan anggota lain? | [ISI] |
| Alasan memilih struktur class akhir | [ISI] |
| Alternatif desain yang sempat dipertimbangkan tetapi tidak dipilih | [ISI] |
| Perubahan dari UML awal ke program akhir | [ISI] |
