"""Data contoh untuk demo (dipanggil dari menu)."""
from datetime import date, timedelta


def isi_data_contoh(mahasiswa_mgr, alat_mgr):
    """Menambah data contoh; data yang kodenya sudah ada dilewati."""
    mahasiswa = [("K001", "Andi Pratama", "081234567890"),
                 ("K002", "Bella Safitri", "081298765432"),
                 ("K003", "Citra Dewi", "085711223344")]
    alat = [("AL001", "Laptop Asus", "perangkat komputasi"),
            ("AL002", "Laptop Lenovo", "perangkat komputasi"),
            ("AL003", "Router Mikrotik", "perangkat jaringan"),
            ("AL004", "Kabel LAN 5m", "perangkat jaringan"),
            ("AL005", "Kamera Digital", "perangkat multimedia"),
            ("AL006", "Tripod", "perangkat multimedia"),
            ("AL007", "Multimeter", "alat ukur")]
    n_mhs = n_alat = 0
    for data in mahasiswa:
        try:
            mahasiswa_mgr.tambah_mahasiswa(*data)
            n_mhs += 1
        except ValueError:
            pass
    for data in alat:
        try:
            alat_mgr.tambah_alat(*data)
            n_alat += 1
        except ValueError:
            pass
    return n_mhs, n_alat
