"""M1: Data Pesanan - Array (dynamic) vs Linked List.

Aturan: tanpa dict, set, sorted, .sort(), heapq, bisect, collections.*.
Hanya list sebagai larik primitif, tuple, aritmetika, dan I/O.
"""
import csv
import time


class Pesanan:
    """Satu baris pesanan. Memakai class biasa (bukan dict)."""
    __slots__ = ("oid", "pelanggan", "resto", "menu", "harga",
                 "prioritas", "t_masuk", "t_selesai", "status")

    def __init__(self, oid, pelanggan, resto, menu, harga,
                 prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas      # 1 VIP, 2 Prioritas, 3 Reguler
        self.t_masuk = t_masuk          # detik
        self.t_selesai = t_selesai      # detik atau None
        self.status = status            # DONE / CANCEL / ANTRE

    def __repr__(self):
        return f"Pesanan({self.oid}, {self.pelanggan}, p={self.prioritas})"


class Array:
    """Implementasi Dynamic Array dari blok memori berukuran tetap."""
    def __init__(self, capacity=4):
        if capacity < 1:
            capacity = 1
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _resize(self, new_capacity):
        """Mengalokasikan petak baru 2x lipat dan menyalin isi lama."""
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def append(self, value):
        """Menambahkan elemen di paling belakang - O(1) amortized."""
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = value
        self.size += 1

    def insert(self, index, value):
        """Menyisipkan elemen pada indeks tertentu dengan menggeser - O(n)."""
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
        self.data[index] = value
        self.size += 1

    def get(self, index):
        """Melihat elemen pada indeks ke-i - O(1)."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[index]

    def delete(self, index):
        """Menghapus elemen ke-i dengan menggeser ke kiri - O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        item = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        return item

    # ---- Operasi bisnis M1 (nama seragam dengan LinkList) ----
    def tambah_reguler(self, pesanan):
        """REGULER: paling belakang."""
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        """PRIORITAS: ke tengah barisan."""
        self.insert(self.size // 2, pesanan)

    def tambah_vip(self, pesanan):
        """VIP: urutan pertama."""
        self.insert(0, pesanan)

    def lihat_pesanan(self, index):
        return self.get(index)

    def hapus_pesanan(self, index):
        return self.delete(index)

    def __len__(self):
        return self.size


class Node:
    """Simpul penampung nilai dan penunjuk ke simpul berikutnya."""
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkList:
    """Singly Linked List dengan penunjuk head dan tail."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        """Menambahkan di belakang - O(1) memakai tail."""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def insert_front(self, value):
        """Menyisipkan di depan - O(1)."""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def insert(self, index, value):
        """Menyisipkan pada indeks ke-i melalui penelusuran - O(n)."""
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if index == 0:
            self.insert_front(value)
        elif index == self.size:
            self.append(value)
        else:
            new_node = Node(value)
            curr = self.head
            for _ in range(index - 1):
                curr = curr.next
            new_node.next = curr.next
            curr.next = new_node
            self.size += 1

    def get(self, index):
        """Melihat elemen ke-i dengan menelusuri dari head - O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        curr = self.head
        for _ in range(index):
            curr = curr.next
        return curr.value

    def delete(self, index):
        """Menghapus elemen ke-i - O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        if index == 0:
            val = self.head.value
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return val

        curr = self.head
        for _ in range(index - 1):
            curr = curr.next
        target = curr.next
        val = target.value
        curr.next = target.next
        if target is self.tail:
            self.tail = curr
        self.size -= 1
        return val

    # ---- Operasi bisnis M1 ----
    def tambah_reguler(self, pesanan):
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        self.insert(self.size // 2, pesanan)

    def tambah_vip(self, pesanan):
        self.insert_front(pesanan)

    def lihat_pesanan(self, index):
        return self.get(index)

    def hapus_pesanan(self, index):
        return self.delete(index)

    def __len__(self):
        return self.size


# ------------------------------------------------------------------
# Pemuatan data & pengukuran waktu
# ------------------------------------------------------------------
def _ke_int_atau_none(teks):
    teks = teks.strip()
    if teks == "":
        return None
    return int(teks)


def baca_csv(path):
    """Membaca pesanan.csv -> Array berisi objek Pesanan.

    Memakai csv.reader karena kolom pelanggan bisa mengandung koma di dalam
    tanda kutip (mis. "Dr. Raina Firmansyah, S.I.Kom"); split(",") akan salah.
    """
    hasil = Array(1024)
    with open(path, newline="", encoding="utf-8") as f:
        pembaca = csv.reader(f)
        next(pembaca, None)  # lewati header
        for baris in pembaca:
            if len(baris) < 9:
                continue
            hasil.append(Pesanan(
                baris[0], baris[1], baris[2], baris[3],
                int(baris[4]), int(baris[5]), int(baris[6]),
                _ke_int_atau_none(baris[7]), baris[8].strip(),
            ))
    return hasil


def muat_ke_struktur(path):
    """Memuat CSV ke Array dan LinkList (urutan file, lewat append).

    Mengembalikan (arr, ll, ms_array, ms_linklist).
    """
    sumber = baca_csv(path)

    t0 = time.perf_counter()
    arr = Array()
    for i in range(len(sumber)):
        arr.tambah_reguler(sumber.get(i))
    ms_arr = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    ll = LinkList()
    for i in range(len(sumber)):
        ll.tambah_reguler(sumber.get(i))
    ms_ll = (time.perf_counter() - t0) * 1000

    return arr, ll, ms_arr, ms_ll


def ukur(fungsi, *args):
    """Menjalankan fungsi dan mengembalikan (hasil, waktu_ms)."""
    t0 = time.perf_counter()
    hasil = fungsi(*args)
    return hasil, (time.perf_counter() - t0) * 1000