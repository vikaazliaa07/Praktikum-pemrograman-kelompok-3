# Sistem Pengelolaan Peminjaman Peralatan Laboratorium

Aplikasi Python (CLI, berbasis OOP) untuk mengelola peminjaman peralatan
laboratorium universitas. Data disimpan di memori memakai `dict`, `list`,
dan `set` (tanpa database).

## Anggota Kelompok

| No | Nama | NIM | Akun GitHub |
|----|------|-----|-------------|
| 1  | [ISI] | [ISI] | [ISI] |
| 2  | [ISI] | [ISI] | [ISI] |
| 3  | [ISI] | [ISI] | [ISI] |

## Deskripsi Sistem

Sistem menggantikan pencatatan manual peminjaman alat lab. Fitur utama:

- CRUD mahasiswa dan alat, pencarian, dan penambahan kategori alat baru
  (kategori adalah data, bukan class).
- Satu transaksi dapat memuat banyak alat dengan jumlah berbeda.
- Pengembalian sebagian, dengan pencatatan kondisi (baik / rusak ringan /
  rusak berat) dan tanggal; keterlambatan otomatis tercatat.
- Aturan bisnis: stok cukup, maksimal 2 transaksi aktif per mahasiswa,
  lama pinjam maksimal 7 hari, alat rusak tidak masuk stok tersedia,
  mahasiswa/alat tidak dapat dihapus selama masih ada transaksi aktif.
- Tantangan yang dikerjakan: **A** pencarian fleksibel, **B** statistik,
  **C** pemeliharaan alat, **D** log aktivitas.

## Struktur Program

```
main.py                  titik masuk aplikasi
lab/
  models.py              Mahasiswa, Alat, Transaksi, ItemPeminjaman,
                         PengembalianRecord, enum KondisiAlat & StatusTransaksi
  mahasiswa_service.py   CRUD + pencarian mahasiswa
  alat_service.py        CRUD alat, kategori, pencarian, pemeliharaan
  transaksi_service.py   buat transaksi, pengembalian, riwayat
  statistik_service.py   statistik peminjaman
  log.py                 ActivityLog
  sistem.py              SistemLab: merakit semua service
  cli.py                 MenuCLI: satu-satunya bagian yang memakai input/print
  konfigurasi.py         batas aturan bisnis (7 hari, 2 transaksi aktif)
  exceptions.py          LabError dan turunannya
  validasi.py            fungsi validasi input
  data_contoh.py         data contoh untuk demo
tests/test_skenario.py   pengujian otomatis (skenario 1-6 + tantangan)
docs/                    UML, keputusan desain, hasil pengujian, refleksi
```

Struktur data utama:

| Data | Struktur |
|------|----------|
| Mahasiswa | `dict[nim -> Mahasiswa]` di `MahasiswaService` |
| Alat | `dict[kode -> Alat]` di `AlatService` |
| Kategori | `list[str]` di `AlatService` |
| Transaksi | `dict[id -> Transaksi]` + index `dict[nim -> list[id]]` |
| Isi transaksi | `dict[kode alat -> ItemPeminjaman]` di `Transaksi` |
| Transaksi aktif | `set[id]` di `Mahasiswa` dan `Alat` |
| Log | `list[dict]` di `ActivityLog` |

## Cara Menjalankan

Membutuhkan Python 3.10+ (tanpa library tambahan).

```bash
python main.py                  # jalankan aplikasi
python -m unittest -v           # jalankan pengujian otomatis
```

Tips demo: pilih menu **14** untuk memuat data contoh.

## Pembagian Kontribusi

Isi sesuai kontribusi nyata masing-masing anggota (harus cocok dengan
histori commit GitHub).

| Anggota | Kontribusi |
|---------|------------|
| [ISI] | [ISI] |
| [ISI] | [ISI] |
| [ISI] | [ISI] |

## Dokumentasi

- `docs/uml_class_diagram.drawio` : UML Class Diagram (buka di draw.io)
- `docs/keputusan_desain.md`
- `docs/hasil_pengujian.md`
- `docs/hasil_code_review.md` (template)
- `docs/refleksi.md`
