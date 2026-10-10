"""Benchmark M1: Array vs LinkList pada data CSV.

Pakai:  python benchmark_m1.py [data/pesanan.csv]
Hasilnya bisa disalin ke tabel di README.
"""
import sys

from backend.m1_pesanan import Pesanan, muat_ke_struktur, ukur


def pesanan_baru(prioritas):
    return Pesanan("O-BARU", "Pelanggan Baru", "kafe-teknik", "roti-bakar",
                   12000, prioritas, 0, None, "ANTRE")


def rata_rata(fn, ulang=5):
    total = 0.0
    for _ in range(ulang):
        _, ms = ukur(fn)
        total += ms
    return total / ulang


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/pesanan.csv"
    arr, ll, ms_a, ms_l = muat_ke_struktur(path)
    n = len(arr)
    print(f"Data dimuat: {n} baris | load Array {ms_a:.2f} ms | "
          f"load LinkList {ms_l:.2f} ms\n")

    kasus = (
        ("Lihat tengah", lambda s: s.lihat_pesanan(len(s) // 2)),
        ("Tambah REGULER", lambda s: s.tambah_reguler(pesanan_baru(3))),
        ("Tambah PRIORITAS", lambda s: s.tambah_prioritas(pesanan_baru(2))),
        ("Tambah VIP", lambda s: s.tambah_vip(pesanan_baru(1))),
        ("Hapus tengah", lambda s: s.hapus_pesanan(len(s) // 2)),
    )

    print(f"{'Operasi':<18}{'Array (ms)':>12}{'LinkList (ms)':>16}")
    print("-" * 46)
    for nama, op in kasus:
        t_arr = rata_rata(lambda: op(arr))
        t_ll = rata_rata(lambda: op(ll))
        print(f"{nama:<18}{t_arr:>12.4f}{t_ll:>16.4f}")


if __name__ == "__main__":
    main()