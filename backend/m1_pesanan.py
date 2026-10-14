 # M1: data pesanan, Array (larik dinamis) vs Linked List
import csv
import time


class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga,
                 prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas  # 1 VIP, 2 prioritas, 3 reguler
        self.t_masuk = t_masuk      # dalam detik
        self.t_selesai = t_selesai  # dalam detik, None kalau belum selesai
        self.status = status        # DONE / CANCEL / ANTRE

    def __repr__(self):
        return f"Pesanan({self.oid}, {self.pelanggan})"


class Array:
    def __init__(self, capacity=4):
        if capacity < 1:
            capacity = 1
        self.capacity = capacity
        self.size = 0
        self.data = [None] * capacity

    def _resize(self, kapasitas_baru):
        # bikin petak baru yang lebih besar, lalu salin isi yang lama
        baru = [None] * kapasitas_baru
        for i in range(self.size):
            baru[i] = self.data[i]
        self.data = baru
        self.capacity = kapasitas_baru

    def append(self, value):
        # tambah di belakang, O(1) amortized
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = value
        self.size += 1

    def insert(self, index, value):
        # sisip di indeks tertentu, elemen sesudahnya digeser ke kanan, O(n)
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
        self.data[index] = value
        self.size += 1

    def get(self, index):
        # langsung ke indeksnya, O(1)
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[index]

    def delete(self, index):
        # hapus elemen, sisanya digeser ke kiri, O(n)
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        item = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        return item

    # operasi yang dipanggil dari menu
    def tambah_reguler(self, pesanan):
        self.append(pesanan)                # paling belakang

    def tambah_prioritas(self, pesanan):
        self.insert(self.size // 2, pesanan)  # tengah

    def tambah_vip(self, pesanan):
        self.insert(0, pesanan)             # paling depan

    def lihat_pesanan(self, index):
        return self.get(index)

    def hapus_pesanan(self, index):
        return self.delete(index)

    def __len__(self):
        return self.size


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None   # disimpan supaya tambah di belakang tidak perlu menelusuri
        self.size = 0

    def append(self, value):
        # tambah di belakang lewat tail, O(1)
        baru = Node(value)
        if self.head is None:
            self.head = baru
            self.tail = baru
        else:
            self.tail.next = baru
            self.tail = baru
        self.size += 1

    def insert_front(self, value):
        # tambah di depan, cukup ubah head, O(1)
        baru = Node(value)
        if self.head is None:
            self.tail = baru
        else:
            baru.next = self.head
        self.head = baru
        self.size += 1

    def insert(self, index, value):
        # sisip di indeks ke-i, harus menelusuri dulu, O(n)
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if index == 0:
            self.insert_front(value)
        elif index == self.size:
            self.append(value)
        else:
            baru = Node(value)
            sekarang = self.head
            for _ in range(index - 1):
                sekarang = sekarang.next
            baru.next = sekarang.next
            sekarang.next = baru
            self.size += 1

    def get(self, index):
        # telusuri dari head sampai indeks ke-i, O(n)
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        sekarang = self.head
        for _ in range(index):
            sekarang = sekarang.next
        return sekarang.value

    def delete(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        # kalau yang dihapus simpul pertama
        if index == 0:
            nilai = self.head.value
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return nilai

        # selain itu, berhenti di simpul sebelum target lalu putus sambungannya
        sebelum = self.head
        for _ in range(index - 1):
            sebelum = sebelum.next
        target = sebelum.next
        sebelum.next = target.next
        if target is self.tail:
            self.tail = sebelum
        self.size -= 1
        return target.value

    # operasi yang dipanggil dari menu
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


def baca_csv(path):
    # baca pesanan.csv jadi Array berisi Pesanan
    # pakai csv.reader karena nama pelanggan bisa mengandung koma di dalam tanda kutip
    hasil = Array(1024)
    with open(path, newline="", encoding="utf-8") as f:
        baca = csv.reader(f)
        next(baca)  # lewati baris header
        for b in baca:
            if len(b) < 9:
                continue
            selesai = None
            if b[7] != "":
                selesai = int(b[7])
            hasil.append(Pesanan(b[0], b[1], b[2], b[3], int(b[4]),
                                 int(b[5]), int(b[6]), selesai, b[8]))
    return hasil


def ukur(fungsi, *args):
    # jalankan fungsi, kembalikan (hasilnya, waktu dalam ms)
    mulai = time.perf_counter()
    hasil = fungsi(*args)
    return hasil, (time.perf_counter() - mulai) * 1000


if __name__ == "__main__":
    # python backend/m1_pesanan.py data/pesanan.csv
    import sys
    path = "data/pesanan.csv"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    data, ms = ukur(baca_csv, path)
    print(f"Terbaca {len(data)} pesanan dalam {ms:.2f} ms")
    print("Pesanan pertama :", data.get(0), data.get(0).menu)
    print("Pesanan terakhir:", data.get(len(data) - 1), data.get(len(data) - 1).menu)