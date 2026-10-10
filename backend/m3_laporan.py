# --- ALGORITMA SORTING ---

def insertion_sort(data, key_func):
    """
    Insertion Sort - O(n^2) di tempat dan stabil.
    Mengembalikan: (data_terurut, jumlah_perbandingan, jumlah_pemindahan)
    """
    n = len(data)
    # Salin array agar tidak merusak data asli
    arr = [item for item in data]
    comparisons = 0
    moves = 0

    for i in range(1, n):
        item = arr[i]
        j = i - 1
        # Menggunakan > untuk menjaga kestabilan (stability)
        while j >= 0:
            comparisons += 1
            if key_func(arr[j]) > key_func(item):
                arr[j + 1] = arr[j]
                moves += 1
                j -= 1
            else:
                break
        arr[j + 1] = item
        moves += 1

    return arr, comparisons, moves


def merge_sort(data, key_func):
    """
    Merge Sort - O(n log n) stabil.
    Mengembalikan: (data_terurut, jumlah_perbandingan, jumlah_pemindahan)
    """
    if len(data) <= 1:
        return data, 0, 0

    mid = len(data) // 2
    left, comp_l, mov_l = merge_sort(data[:mid], key_func)
    right, comp_r, mov_r = merge_sort(data[mid:], key_func)

    merged, comp_m, mov_m = _merge(left, right, key_func)
    
    total_comp = comp_l + comp_r + comp_m
    total_mov = mov_l + mov_r + mov_m
    return merged, total_comp, total_mov


def _merge(left, right, key_func):
    result = []
    comparisons = 0
    moves = 0
    i = 0
    j = 0
    len_l = len(left)
    len_r = len(right)

    while i < len_l and j < len_r:
        comparisons += 1
        # Pakai <= agar elemen dari bagian kiri didahulukan saat kuncinya sama (stabil)
        if key_func(left[i]) <= key_func(right[j]):
            result.append(left[i])
            moves += 1
            i += 1
        else:
            result.append(right[j])
            moves += 1
            j += 1

    while i < len_l:
        result.append(left[i])
        moves += 1
        i += 1

    while j < len_r:
        result.append(right[j])
        moves += 1
        j += 1

    return result, comparisons, moves


# --- ALGORITMA SEARCHING ---

def linear_search(data, target_oid, key_func):
    """
    Linear Search - O(n) menelusuri satu per satu dari depan.
    Mengembalikan: (indeks_ditemukan, jumlah_perbandingan)
    """
    comparisons = 0
    for i in range(len(data)):
        comparisons += 1
        if key_func(data[i]) == target_oid:
            return i, comparisons
    return -1, comparisons


def binary_search(data_terurut, target_oid, key_func):
    """
    Binary Search - O(log n) membuang separuh sisa pada tiap langkah.
    Syarat: Data HARUS sudah terurut berdasarkan kunci yang dicari.
    Mengembalikan: (indeks_ditemukan, jumlah_perbandingan)
    """
    lo = 0
    hi = len(data_terurut) - 1
    comparisons = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        mid_val = key_func(data_terurut[mid])

        if mid_val == target_oid:
            return mid, comparisons
        elif mid_val < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, comparisons


# --- PENGUJI M3 ---

class PesananDummy:
    """Kelas sederhana untuk merepresentasikan data pesanan."""
    def __init__(self, oid, harga, selesai):
        self.oid = oid
        self.harga = harga
        self.selesai = selesai

    def __repr__(self):
        return f"({self.oid}, Rp{self.harga}, {self.selesai})"


if __name__ == "__main__":
    # Sample data acak
    laporan = [
        PesananDummy("O-000005", 20000, "21:23:26"),
        PesananDummy("O-000002", 11000, "17:15:15"),
        PesananDummy("O-000001", 12000, "08:00:00"),
        PesananDummy("O-000004", 25000, "10:15:00"),
        PesananDummy("O-000003", 13000, "11:07:06"),
    ]

    print("=== DATA AWAL ===")
    for p in laporan:
        print(p)

    print("\n=== 1. UJI INSERTION SORT (Berdasarkan Harga) ===")
    hasil_ins, comp_ins, mov_ins = insertion_sort(laporan, lambda x: x.harga)
    for p in hasil_ins:
        print(p)
    print(f"Perbandingan: {comp_ins}, Pemindahan: {mov_ins}")

    print("\n=== 2. UJI MERGE SORT (Berdasarkan OID) ===")
    hasil_merge, comp_mrg, mov_mrg = merge_sort(laporan, lambda x: x.oid)
    for p in hasil_merge:
        print(p)
    print(f"Perbandingan: {comp_mrg}, Pemindahan: {mov_mrg}")

    print("\n=== 3. UJI LINEAR SEARCH vs BINARY SEARCH ===")
    target = "O-000004"

    # Linear Search pada data acak
    idx_lin, comp_lin = linear_search(laporan, target, lambda x: x.oid)
    print(f"Linear Search : Ditemukan di indeks {idx_lin} ({comp_lin} perbandingan)")

    # Binary Search pada data terurut OID
    idx_bin, comp_bin = binary_search(hasil_merge, target, lambda x: x.oid)
    print(f"Binary Search : Ditemukan di indeks {idx_bin} ({comp_bin} perbandingan)")