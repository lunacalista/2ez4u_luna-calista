"""M3: Sort & Search (laporan harian + pencarian pesanan).

Empat algoritma, masing-masing melaporkan jumlah perbandingan lewat Pencacah:
  insertion_sort  O(n^2)     stabil, di tempat
  merge_sort      O(n log n) stabil
  linear_search   O(n)       tidak butuh data terurut
  binary_search   O(log n)   butuh data terurut menurut kunci yang dicari

Aturan: tanpa dict, set, sorted, .sort(), heapq, bisect, collections.*.
Larik yang dipakai adalah list Python biasa (larik primitif). Data dari M1
(Array berisi Pesanan) diubah dulu lewat array_ke_list().
"""

try:
    from backend.m1_pesanan import Pesanan, ukur    # dari root repo
except ImportError:
    from m1_pesanan import Pesanan, ukur            # langsung dari backend/

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


# Fungsi kunci untuk objek Pesanan (M1)
def kunci_oid(p):
    return p.oid


def kunci_harga(p):
    return p.harga


def kunci_selesai(p):
    """Waktu selesai; pesanan yang belum selesai (None) ditaruh paling akhir."""
    if p.t_selesai is None:
        return BELUM_SELESAI
    return p.t_selesai


def ambil_kunci(nama):
    """Nama kunci dari menu UI ("oid" / "harga" / "selesai") -> fungsi kunci."""
    if nama == "oid":
        return kunci_oid
    if nama == "harga":
        return kunci_harga
    if nama == "selesai":
        return kunci_selesai
    raise ValueError("Kunci tidak dikenal: " + str(nama))


# Pembantu data
def array_ke_list(arr):
    """Array M1 (atau apa pun yang punya len dan get) -> list biasa."""
    hasil = []
    for i in range(len(arr)):
        hasil.append(arr.get(i))
    return hasil


def ambil_awal(A, n):
    """Salinan n elemen pertama, supaya larik asli tidak ikut terurut."""
    if n < 0:
        n = 0
    if n > len(A):
        n = len(A)
    hasil = []
    for i in range(n):
        hasil.append(A[i])
    return hasil


# Sorting
def insertion_sort(A, kunci, pencacah=None, batas=BATAS_INSERTION):
    """Mengurutkan A DI TEMPAT, stabil, O(n^2).

    Stabil karena menggeser hanya bila kunci kiri LEBIH BESAR (>), bukan >=.
    pemindahan = jumlah geseran + satu penempatan untuk tiap elemen (indeks 1..n-1).
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


def _gabung_larik(A, K, tA, tK, lo, mid, hi, pencacah):
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
    _gabung_larik(A, K, tA, tK, lo, mid, hi, pencacah)


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


# Searching
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
    while lo <= hi:                   
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

# Pembungkus untuk UI: hasil + pencacah + waktu (ms, lewat ukur() milik M1)
def jalankan_sort(data, jumlah, nama_kunci, metode):
    """Mengurutkan `jumlah` baris pertama `data` (list Pesanan), data asli utuh.

    metode: "insertion" atau "merge". Mengembalikan (hasil, pencacah, ms).
    insertion_sort melempar ValueError bila jumlah melebihi batasnya.
    """
    kunci = ambil_kunci(nama_kunci)
    salinan = ambil_awal(data, jumlah)
    pencacah = Pencacah()
    if metode == "insertion":
        hasil, ms = ukur(insertion_sort, salinan, kunci, pencacah)
    elif metode == "merge":
        hasil, ms = ukur(merge_sort, salinan, kunci, pencacah)
    else:
        raise ValueError("Metode sort tidak dikenal: " + str(metode))
    return hasil, pencacah, ms


def jalankan_cari(A, target, metode, kunci=None):
    """metode: "linear" atau "binary". Mengembalikan (indeks, pencacah, ms).

    Untuk "binary", A harus sudah terurut menurut kunci yang dicari
    (mis. hasil bangun_indeks_oid untuk pencarian oid).
    """
    pencacah = Pencacah()
    if metode == "linear":
        indeks, ms = ukur(linear_search, A, target, kunci, pencacah)
    elif metode == "binary":
        indeks, ms = ukur(binary_search, A, target, kunci, pencacah)
    else:
        raise ValueError("Metode cari tidak dikenal: " + str(metode))
    return indeks, pencacah, ms


def demo():
    data = [
        Pesanan("O-000001", "A", "kafe-teknik", "roti-bakar", 12000, 3, 100, None, "CANCEL"),
        Pesanan("O-000002", "B", "kedai-kopi", "bubur-ayam", 11000, 3, 200, 17000, "DONE"),
        Pesanan("O-000003", "C", "warung-bu-ida", "mie-goreng", 13000, 3, 300, 12000, "DONE"),
        Pesanan("O-000004", "D", "kafe-teknik", "nasi-padang", 25000, 2, 400, None, "CANCEL"),
        Pesanan("O-000005", "E", "kedai-kopi", "iga-penyet", 11000, 3, 500, 9000, "DONE"),
    ]

    print("=== 1. SORT (kunci = harga; stabil: O-000002 sebelum O-000005) ===")
    for metode in ("insertion", "merge"):
        hasil, pc, ms = jalankan_sort(data, 5, "harga", metode)
        urutan = ""
        for p in hasil:
            urutan += p.oid + " "
        print(f"{metode:<10}: {urutan}| {pc.perbandingan} perbandingan, "
              f"{pc.pemindahan} pemindahan")

    print("\n=== 2. SEARCH oid O-000004 ===")
    idx, pc, ms = jalankan_cari(data, "O-000004", "linear", kunci_oid)
    print(f"linear : indeks {idx} | {pc.perbandingan} perbandingan")
    indeks = bangun_indeks_oid(data)
    idx, pc, ms = jalankan_cari(indeks, "O-000004", "binary", kunci_oid)
    print(f"binary : indeks {idx} | {pc.perbandingan} perbandingan")


if __name__ == "__main__":
    demo()