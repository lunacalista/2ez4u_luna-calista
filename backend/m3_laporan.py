"""M3: Sort & Search (laporan harian + pencarian pesanan).

Empat algoritma, masing-masing melaporkan jumlah perbandingan lewat Pencacah:
  insertion_sort  O(n^2)     stabil, di tempat
  merge_sort      O(n log n) stabil
  linear_search   O(n)       tidak butuh data terurut
  binary_search   O(log n)   butuh data terurut menurut kunci yang dicari

Aturan: tanpa dict, set, sorted, .sort(), heapq, bisect, collections.*.
Larik yang dipakai adalah list Python biasa (larik primitif).
"""

import time

BATAS_INSERTION = 20000          # lebih besar dari ini ditolak, pakai merge sort
BELUM_SELESAI = 10 ** 12         # kunci untuk pesanan tanpa waktu selesai


class Pencacah:
    """Pencacah sederhana yang dititipkan ke algoritma.

    perbandingan : berapa kali dua kunci dibandingkan
    pemindahan   : berapa kali elemen ditulis ke larik (geser/tempatkan/gabung)
    """
    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0

    def reset(self):
        self.perbandingan = 0
        self.pemindahan = 0


# ------------------------------------------------------------------
# Fungsi kunci untuk objek Pesanan (M1)
# ------------------------------------------------------------------
def kunci_oid(p):
    return p.oid


def kunci_harga(p):
    return p.harga


def kunci_selesai(p):
    """Waktu selesai; pesanan yang belum selesai ditaruh paling akhir."""
    if p.t_selesai is None:
        return BELUM_SELESAI
    return p.t_selesai


# ------------------------------------------------------------------
# Pembantu data
# ------------------------------------------------------------------
def array_ke_list(arr):
    """Array M1 (atau apa pun yang punya len dan get) -> list biasa."""
    hasil = []
    for i in range(len(arr)):
        hasil.append(arr.get(i))
    return hasil


def ambil_awal(A, n):
    """Salinan n elemen pertama, supaya larik asli tidak ikut terurut."""
    if n > len(A):
        n = len(A)
    hasil = []
    for i in range(n):
        hasil.append(A[i])
    return hasil


# ------------------------------------------------------------------
# Sorting
# ------------------------------------------------------------------
def insertion_sort(A, kunci, pencacah=None, batas=BATAS_INSERTION):
    """Mengurutkan A DI TEMPAT, stabil, O(n^2).

    Stabil karena menggeser hanya bila kunci kiri LEBIH BESAR (>), bukan >=.
    pemindahan = jumlah geseran + satu penempatan untuk tiap elemen.
    Menolak data lebih dari `batas` (ValueError) supaya aplikasi tidak membeku.
    """
    if pencacah is None:
        pencacah = Pencacah()
    n = len(A)
    if n > batas:
        batas_teks = format(batas, ",").replace(",", ".")
        raise ValueError(
            f"DITOLAK: batasnya {batas_teks} baris, pakai merge sort untuk data penuh")

    K = []
    for i in range(n):
        K.append(kunci(A[i]))

    for i in range(1, n):
        item = A[i]
        k = K[i]
        j = i - 1
        while j >= 0:
            pencacah.perbandingan += 1
            if K[j] > k:
                A[j + 1] = A[j]
                K[j + 1] = K[j]
                pencacah.pemindahan += 1
                j -= 1
            else:
                break
        A[j + 1] = item
        K[j + 1] = k
        pencacah.pemindahan += 1
    return A


def _gabung(A, K, tA, tK, lo, mid, hi, pencacah):
    """Menggabungkan A[lo:mid] dan A[mid:hi] yang masing-masing sudah terurut."""
    i = lo
    j = mid
    t = lo
    while i < mid and j < hi:
        pencacah.perbandingan += 1
        if K[i] <= K[j]:              # <= : kiri didahulukan, menjaga stabilitas
            tA[t] = A[i]
            tK[t] = K[i]
            i += 1
        else:
            tA[t] = A[j]
            tK[t] = K[j]
            j += 1
        t += 1
        pencacah.pemindahan += 1
    while i < mid:                    # sisa bagian kiri
        tA[t] = A[i]
        tK[t] = K[i]
        i += 1
        t += 1
        pencacah.pemindahan += 1
    while j < hi:                     # sisa bagian kanan
        tA[t] = A[j]
        tK[t] = K[j]
        j += 1
        t += 1
        pencacah.pemindahan += 1
    for x in range(lo, hi):           # salin balik
        A[x] = tA[x]
        K[x] = tK[x]


def _urut(A, K, tA, tK, lo, hi, pencacah):
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    _urut(A, K, tA, tK, lo, mid, pencacah)
    _urut(A, K, tA, tK, mid, hi, pencacah)
    _gabung(A, K, tA, tK, lo, mid, hi, pencacah)


def merge_sort(A, kunci, pencacah=None):
    """Mengembalikan larik BARU yang terurut, stabil, O(n log n)."""
    if pencacah is None:
        pencacah = Pencacah()
    n = len(A)
    hasil = []
    K = []
    for i in range(n):
        hasil.append(A[i])
        K.append(kunci(A[i]))
    tA = [None] * n
    tK = [None] * n
    _urut(hasil, K, tA, tK, 0, n, pencacah)
    return hasil


# ------------------------------------------------------------------
# Searching
# ------------------------------------------------------------------
def linear_search(A, target, kunci=None, pencacah=None):
    """Menelusuri satu per satu. Mengembalikan indeks, atau -1 bila tidak ada.

    Tidak menuntut data terurut. Kasus terburuk menyentuh seluruh n elemen.
    """
    if pencacah is None:
        pencacah = Pencacah()
    for i in range(len(A)):
        pencacah.perbandingan += 1
        nilai = A[i] if kunci is None else kunci(A[i])
        if nilai == target:
            return i
    return -1


def binary_search(A, target, kunci=None, pencacah=None):
    """Membuang separuh sisa tiap langkah. A HARUS terurut menurut kunci ini.

    Satu langkah (satu elemen tengah diperiksa) dihitung satu perbandingan.
    Mengembalikan indeks, atau -1 bila tidak ada.
    """
    if pencacah is None:
        pencacah = Pencacah()
    lo = 0
    hi = len(A) - 1
    while lo <= hi:                   # <=, bukan <
        mid = (lo + hi) // 2
        nilai = A[mid] if kunci is None else kunci(A[mid])
        pencacah.perbandingan += 1
        if nilai == target:
            return mid
        if nilai < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def bangun_indeks_oid(A, pencacah=None):
    """Daftar terpisah yang terurut menurut oid (ongkos sekali bayar).

    Laporan harian terurut menurut waktu selesai, jadi mencari oid di sana
    tidak sah untuk binary search.
    """
    return merge_sort(A, kunci_oid, pencacah)


# ------------------------------------------------------------------
# Benchmark M3: insertion vs merge sort, linear vs binary search
# Pakai:  python backend/m3_laporan.py [data/pesanan.csv]
# Mencetak tabel n vs perbandingan (untuk README dan grafiknya).
# Insertion sort dibatasi sampai 8.000 baris agar tidak terlalu lama.
# ------------------------------------------------------------------
def _ukur(fungsi, *args):
    t0 = time.perf_counter()
    hasil = fungsi(*args)
    return hasil, (time.perf_counter() - t0) * 1000


def benchmark(path="data/pesanan.csv"):
    try:
        from backend.m1_pesanan import baca_csv     # dari root repo
    except ImportError:
        from m1_pesanan import baca_csv             # langsung dari backend/

    data = array_ke_list(baca_csv(path))
    print(f"Data dimuat: {len(data)} baris\n")

    print("SORT, kunci = harga")
    print(f"{'n':>8}{'insertion cmp':>16}{'insertion ms':>14}"
          f"{'merge cmp':>14}{'merge ms':>12}")
    print("-" * 64)
    for n in (1000, 2000, 4000, 8000):
        pi = Pencacah()
        _, ms_i = _ukur(insertion_sort, ambil_awal(data, n), kunci_harga, pi)
        pm = Pencacah()
        _, ms_m = _ukur(merge_sort, ambil_awal(data, n), kunci_harga, pm)
        print(f"{n:>8}{pi.perbandingan:>16}{ms_i:>14.2f}"
              f"{pm.perbandingan:>14}{ms_m:>12.2f}")

    pm = Pencacah()
    _, ms = _ukur(merge_sort, data, kunci_harga, pm)
    print(f"\nMerge sort data penuh ({len(data)} baris, harga): "
          f"{pm.perbandingan} perbandingan, {ms:.2f} ms")

    target = data[len(data) - 2].oid
    pl = Pencacah()
    idx_l, ms_l = _ukur(linear_search, data, target, kunci_oid, pl)
    p_bangun = Pencacah()
    indeks, ms_bangun = _ukur(bangun_indeks_oid, data, p_bangun)
    pb = Pencacah()
    idx_b, ms_b = _ukur(binary_search, indeks, target, kunci_oid, pb)

    print(f"\nSEARCH oid {target}")
    print(f"  linear : indeks {idx_l} | {pl.perbandingan} perbandingan | {ms_l:.4f} ms")
    print(f"  binary : baris  {idx_b} | {pb.perbandingan} perbandingan | {ms_b:.4f} ms")
    print(f"  (ongkos sekali bayar: bangun daftar terurut oid dengan merge sort, "
          f"{ms_bangun:.2f} ms)")


if __name__ == "__main__":
    import sys
    benchmark(sys.argv[1] if len(sys.argv) > 1 else "data/pesanan.csv")