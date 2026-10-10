"""Benchmark M3: insertion vs merge sort, linear vs binary search.

Pakai:  python benchmark_m3.py [data/pesanan.csv]
Mencetak tabel n vs perbandingan (untuk README dan grafiknya).
Insertion sort dibatasi sampai 8.000 baris agar tidak terlalu lama.
"""
import sys

from backend.m1_pesanan import baca_csv, ukur
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort,
                                linear_search, binary_search, bangun_indeks_oid,
                                array_ke_list, ambil_awal,
                                kunci_oid, kunci_harga)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/pesanan.csv"
    data = array_ke_list(baca_csv(path))
    print(f"Data dimuat: {len(data)} baris\n")

    # --- tabel n vs perbandingan, kunci harga ---
    print("SORT, kunci = harga")
    print(f"{'n':>8}{'insertion cmp':>16}{'insertion ms':>14}"
          f"{'merge cmp':>14}{'merge ms':>12}")
    print("-" * 64)
    for n in (1000, 2000, 4000, 8000):
        a = ambil_awal(data, n)
        pi = Pencacah()
        _, ms_i = ukur(insertion_sort, a, kunci_harga, pi)
        pm = Pencacah()
        _, ms_m = ukur(merge_sort, ambil_awal(data, n), kunci_harga, pm)
        print(f"{n:>8}{pi.perbandingan:>16}{ms_i:>14.2f}"
              f"{pm.perbandingan:>14}{ms_m:>12.2f}")

    # --- merge sort data penuh ---
    pm = Pencacah()
    _, ms = ukur(merge_sort, data, kunci_harga, pm)
    print(f"\nMerge sort data penuh ({len(data)} baris, harga): "
          f"{pm.perbandingan} perbandingan, {ms:.2f} ms")

    # --- search ---
    target = data[len(data) - 2].oid
    pl = Pencacah()
    idx_l, ms_l = ukur(linear_search, data, target, kunci_oid, pl)

    p_bangun = Pencacah()
    indeks, ms_bangun = ukur(bangun_indeks_oid, data, p_bangun)
    pb = Pencacah()
    idx_b, ms_b = ukur(binary_search, indeks, target, kunci_oid, pb)

    print(f"\nSEARCH oid {target}")
    print(f"  linear : indeks {idx_l} | {pl.perbandingan} perbandingan | {ms_l:.4f} ms")
    print(f"  binary : baris  {idx_b} | {pb.perbandingan} perbandingan | {ms_b:.4f} ms")
    print(f"  (ongkos sekali bayar: bangun daftar terurut oid dengan merge sort, "
          f"{ms_bangun:.2f} ms)")


if __name__ == "__main__":
    main()