"""Fungsi bantu validasi input yang dipakai lintas class."""

import re

from .exceptions import ValidasiError


def wajib_isi(nilai, nama_field):
    """Pastikan teks tidak kosong; kembalikan teks yang sudah di-strip."""
    if nilai is None or not str(nilai).strip():
        raise ValidasiError(f"{nama_field} tidak boleh kosong.")
    return str(nilai).strip()


def validasi_no_hp(no_hp):
    """Nomor HP: 8-15 digit, boleh diawali '+', spasi/strip diabaikan."""
    bersih = re.sub(r"[\s\-]", "", wajib_isi(no_hp, "Nomor HP"))
    if not re.fullmatch(r"\+?\d{8,15}", bersih):
        raise ValidasiError("Nomor HP harus berupa 8-15 digit angka.")
    return bersih


def bilangan_positif(nilai, nama_field):
    """Pastikan nilai adalah bilangan bulat > 0 (bool ditolak)."""
    if isinstance(nilai, bool) or not isinstance(nilai, int) or nilai <= 0:
        raise ValidasiError(f"{nama_field} harus berupa bilangan bulat > 0.")
    return nilai
