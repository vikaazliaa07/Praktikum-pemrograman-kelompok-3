"""Data contoh untuk demo/presentasi (tidak dimuat otomatis)."""


def muat_data_contoh(sistem):
    sistem.mahasiswa.tambah("M001", "Andi Pratama", "081234567890")
    sistem.mahasiswa.tambah("M002", "Budi Santoso", "081298765432")
    sistem.mahasiswa.tambah("M003", "Citra Lestari", "085611223344")

    sistem.alat.tambah("KMP01", "Laptop", "perangkat komputasi", 5)
    sistem.alat.tambah("JRG01", "Kabel LAN", "perangkat jaringan", 10)
    sistem.alat.tambah("JRG02", "Router", "perangkat jaringan", 2)
    sistem.alat.tambah("MLT01", "Kamera Digital", "perangkat multimedia", 3)
    sistem.alat.tambah("MLT02", "Tripod", "perangkat multimedia", 3)
