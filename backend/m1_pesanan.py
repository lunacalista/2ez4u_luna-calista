class Array:
    """Implementasi Dynamic Array dari blok memori berukuran tetap."""
    def __init__(self, capacity=4):
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
        """Menyisipkan elemen pada indeks tertentu dengan menggeser elemen - O(n)."""
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
        """Menghapus elemen pada indeks ke-i dengan menggeser ke kiri - O(n)."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        item = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.data[self.size - 1] = None
        self.size -= 1
        return item

    # Operasi Sesuai Aturan Bisnis M1
    def tambah_reguler(self, pesanan):
        """Pesanan REGULER: masuk paling belakang."""
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        """Pesanan PRIORITAS: menyerobot ke tengah barisan."""
        pos = self.size // 2
        self.insert(pos, pesanan)

    def tambah_vip(self, pesanan):
        """Pesanan VIP: langsung ke urutan pertama (indeks 0)."""
        self.insert(0, pesanan)

    def __len__(self):
        return self.size


class Node:
    """Simpul penampung nilai dan penunjuk ke simpul berikutnya."""
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkList:
    """Implementasi Singly Linked List dengan penunjuk head dan tail."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        """Menambahkan elemen di paling belakang - O(1) memakai tail."""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def insert_front(self, value):
        """Menyisipkan elemen di paling depan - O(1)."""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def insert(self, index, value):
        """Menyisipkan elemen pada indeks ke-i melalui penelusuran - O(n)."""
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

        if target == self.tail:
            self.tail = curr

        self.size -= 1
        return val

    # Operasi Sesuai Aturan Bisnis M1
    def tambah_reguler(self, pesanan):
        """Pesanan REGULER: masuk paling belakang."""
        self.append(pesanan)

    def tambah_prioritas(self, pesanan):
        """Pesanan PRIORITAS: menelusuri ke tengah barisan lalu menyambung."""
        pos = self.size // 2
        self.insert(pos, pesanan)

    def tambah_vip(self, pesanan):
        """Pesanan VIP: ubah penunjuk di depan (O(1))."""
        self.insert_front(pesanan)

    def __len__(self):
        return self.size


if __name__ == "__main__":
    # 1. Uji Struktur Data Array
    arr = Array()
    arr.tambah_reguler("Pesanan A (Reguler)")
    arr.tambah_vip("Pesanan B (VIP)")
    arr.tambah_prioritas("Pesanan C (Prioritas)")

    print("--- HASIL ARRAY ---")
    for i in range(len(arr)):
        print(f"Indeks {i}: {arr.get(i)}")

    # 2. Uji Struktur Data Linked List
    ll = LinkList()
    ll.tambah_reguler("Pesanan A (Reguler)")
    ll.tambah_vip("Pesanan B (VIP)")
    ll.tambah_prioritas("Pesanan C (Prioritas)")

    print("\n--- HASIL LINKED LIST ---")
    for i in range(len(ll)):
        print(f"Indeks {i}: {ll.get(i)}")