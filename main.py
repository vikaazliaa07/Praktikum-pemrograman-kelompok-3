"""Titik masuk aplikasi: python main.py"""

from lab.cli import MenuCLI
from lab.sistem import SistemLab


def main():
    MenuCLI(SistemLab()).jalankan()


if __name__ == "__main__":
    main()
