"""Exception khusus aplikasi.

Semua error yang berasal dari aturan/validasi diturunkan dari LabError
sehingga lapisan menu cukup menangkap satu jenis exception.
"""


class LabError(Exception):
    """Base class untuk semua error aplikasi."""


class ValidasiError(LabError):
    """Input tidak valid (kosong, format salah, jumlah <= 0, dst)."""


class DataTidakDitemukanError(LabError):
    """Data yang dicari tidak ada."""


class DataDuplikatError(LabError):
    """Data dengan kunci yang sama sudah ada."""


class AturanBisnisError(LabError):
    """Operasi melanggar aturan bisnis (stok habis, batas transaksi, dst)."""
