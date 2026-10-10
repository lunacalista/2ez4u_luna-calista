"""Tes M3. Jalankan dari root repo:  python tests/test_m3.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.m1_pesanan import Pesanan
from backend.m3_laporan import (Pencacah, insertion_sort, merge_sort,
                                linear_search, binary_search, bangun_indeks_oid,
                                kunci_oid, kunci_harga, kunci_selesai,
                                ambil_awal, BELUM_SELESAI)


def acak(n, nilai_maks, benih=12345):
    """Pembangkit acak sederhana (LCG), hasilnya selalu sama."""
    out = []
    x = benih
    for _ in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        out.append(x % nilai_maks)
    return out


def pasangan(n, nilai_maks, benih=12345):
    """(kunci, urutan_masuk): kunci sering kembar supaya stabilitas teruji."""
    k = acak(n, nilai_maks, benih)
    out = []
    for i in range(n):
        out.append((k[i], i))
    return out


def kunci_pertama(t):
    return t[0]


def terurut_stabil(hasil):
    """Terurut menurut kunci; yang kuncinya sama tetap menurut urutan masuk."""
    for i in range(1, len(hasil)):
        a, b = hasil[i - 1], hasil[i]
        if a[0] > b[0]:
            return False
        if a[0] == b[0] and a[1] > b[1]:
            return False
    return True


def tegak(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def pesanan(i, harga, selesai=None):
    return Pesanan("O-%06d" % i, "x", "r", "m", harga, 3, 0, selesai, "DONE")


# ---------------- sorting ----------------
def uji_insertion_sama_dengan_pdf():
    """10 baris pertama di PDF, kunci harga: 24 perbandingan, 25 pemindahan."""
    harga = (12000, 11000, 13000, 25000, 20000, 19000, 14000, 27000, 11000, 24000)
    A = []
    for i in range(len(harga)):
        A.append(pesanan(i + 1, harga[i]))
    p = Pencacah()
    insertion_sort(A, kunci_harga, p)
    assert p.perbandingan == 24 and p.pemindahan == 25
    assert A[0].oid == "O-000002" and A[1].oid == "O-000009"   # bukti stabil
    assert A[0].harga == A[1].harga == 11000


def uji_merge_sama_dengan_pdf():
    """4.000 baris yang sudah terurut menurut oid: 23.728 dan 47.904."""
    B = []
    for i in range(4000):
        B.append("O-%06d" % (i + 1))
    p = Pencacah()
    merge_sort(B, lambda s: s, p)
    assert p.perbandingan == 23728 and p.pemindahan == 47904


def uji_kedua_sort_benar_dan_stabil():
    data_uji = (
        pasangan(500, 20),                  # acak, banyak duplikat
        pasangan(300, 1),                   # semua kunci sama
        [(i, i) for i in range(200)],       # sudah terurut
        [(200 - i, i) for i in range(200)], # terbalik
        [],                                 # kosong
        [(5, 0)],                           # satu elemen
    )
    for data in data_uji:
        a = ambil_awal(data, len(data))
        b = merge_sort(data, kunci_pertama)
        insertion_sort(a, kunci_pertama)
        assert terurut_stabil(a) and terurut_stabil(b)
        assert a == b                       # identik baris per baris
        assert len(a) == len(data)          # tidak ada data hilang di ujung


def uji_merge_tidak_mengubah_input():
    data = pasangan(50, 10)
    salinan = ambil_awal(data, 50)
    merge_sort(data, kunci_pertama)
    assert data == salinan


def uji_pola_perbandingan():
    """n dilipatduakan: insertion ~4x, merge ~2x."""
    p1, p2, m1, m2 = Pencacah(), Pencacah(), Pencacah(), Pencacah()
    d1 = pasangan(1000, 10 ** 6)
    d2 = pasangan(2000, 10 ** 6)
    insertion_sort(ambil_awal(d1, 1000), kunci_pertama, p1)
    insertion_sort(ambil_awal(d2, 2000), kunci_pertama, p2)
    merge_sort(d1, kunci_pertama, m1)
    merge_sort(d2, kunci_pertama, m2)
    assert 3.5 < p2.perbandingan / p1.perbandingan < 4.5
    assert 1.9 < m2.perbandingan / m1.perbandingan < 2.3
    assert m2.perbandingan * 20 < p2.perbandingan


def uji_insertion_hampir_terurut():
    p = Pencacah()
    data = [(i, i) for i in range(1000)]
    data[500], data[501] = data[501], data[500]
    insertion_sort(data, kunci_pertama, p)
    assert p.perbandingan < 1100            # mendekati O(n)


def uji_insertion_menolak_data_besar():
    besar = [0] * 20001
    assert tegak(ValueError, insertion_sort, besar, lambda x: x)
    ok = [0] * 20000                        # tepat di batas masih diterima
    insertion_sort(ok, lambda x: x)


def uji_kunci_selesai():
    A = [pesanan(1, 1, 500), pesanan(2, 1, None), pesanan(3, 1, 100)]
    hasil = merge_sort(A, kunci_selesai)
    assert hasil[0].oid == "O-000003" and hasil[1].oid == "O-000001"
    assert hasil[2].oid == "O-000002" and kunci_selesai(hasil[2]) == BELUM_SELESAI


# ---------------- searching ----------------
def uji_linear_search():
    A = [10, 20, 30, 40]
    p = Pencacah()
    assert linear_search(A, 30, pencacah=p) == 2 and p.perbandingan == 3
    p.reset()
    assert linear_search(A, 99, pencacah=p) == -1 and p.perbandingan == 4
    assert linear_search([], 1) == -1
    B = [pesanan(5, 1), pesanan(7, 1)]
    assert linear_search(B, "O-000007", kunci_oid) == 1


def uji_binary_search_empat_kasus():
    A = [2, 4, 6, 8, 10, 12, 14]
    assert binary_search(A, 8) == 3         # tengah
    assert binary_search(A, 2) == 0         # kiri
    assert binary_search(A, 14) == 6        # kanan
    assert binary_search(A, 7) == -1        # tidak ada
    assert binary_search(A, 1) == -1 and binary_search(A, 99) == -1
    assert binary_search([], 5) == -1       # larik kosong
    assert binary_search([5], 5) == 0 and binary_search([5], 6) == -1


def uji_binary_vs_linear():
    n = 100000
    A = []
    for i in range(n):
        A.append("O-%06d" % (i + 1))
    target = A[n - 2]
    pl, pb = Pencacah(), Pencacah()
    assert linear_search(A, target, pencacah=pl) == n - 2
    assert binary_search(A, target, pencacah=pb) == n - 2
    assert pb.perbandingan <= 18
    assert pl.perbandingan > pb.perbandingan * 1000


def uji_indeks_oid_untuk_binary():
    # laporan terurut menurut selesai; oid acak urutannya
    A = [pesanan(3, 1, 10), pesanan(1, 1, 20), pesanan(2, 1, 30)]
    indeks = bangun_indeks_oid(A)
    assert binary_search(indeks, "O-000002", kunci_oid) == 1
    assert binary_search(indeks, "O-000009", kunci_oid) == -1


if __name__ == "__main__":
    tes = [uji_insertion_sama_dengan_pdf, uji_merge_sama_dengan_pdf,
           uji_kedua_sort_benar_dan_stabil, uji_merge_tidak_mengubah_input,
           uji_pola_perbandingan, uji_insertion_hampir_terurut,
           uji_insertion_menolak_data_besar, uji_kunci_selesai,
           uji_linear_search, uji_binary_search_empat_kasus,
           uji_binary_vs_linear, uji_indeks_oid_untuk_binary]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print("\nSemua tes M3 lulus.")