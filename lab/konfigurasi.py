"""Konstanta aturan bisnis.

Aturan yang bisa berubah (batas hari, batas transaksi aktif) dikumpulkan di
sini supaya perubahan aturan tidak perlu mengubah logika di class lain.
"""

MAKS_HARI_PINJAM = 7          # batas waktu pengembalian maksimal (hari)
MAKS_TRANSAKSI_AKTIF = 2      # maksimal transaksi aktif per mahasiswa

KATEGORI_AWAL = (
    "perangkat komputasi",
    "perangkat jaringan",
    "perangkat multimedia",
)
