class Stack:
    """Implementasi Tumpukan (LIFO) berbasis array primitif."""
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


class AntreanNaif:
    """Antrean (Queue) Naif - Dequeue menggeser seluruh sisa isi O(n)."""
    def __init__(self):
        self.data = []
        self.total_geseran = 0

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        item = self.data[0]
        sisa = len(self.data) - 1
        self.total_geseran += sisa
        
        # Menggeser isi manual satu petak ke kiri
        baru = [None] * sisa
        for i in range(sisa):
            baru[i] = self.data[i + 1]
        self.data = baru
        return item

    def is_empty(self):
        return len(self.data) == 0

    def size(self):
        return len(self.data)


class AntreanMelingkar:
    """Antrean Melingkar (Circular Queue) - Dequeue O(1) memajukan penunjuk front."""
    def __init__(self, capacity=4):
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.capacity]
        self.data = new_data
        self.front = 0
        self.rear = self.count
        self.capacity = new_capacity

    def enqueue(self, item):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            return None
        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count


# --- KASIR STACK (INFIX -> POSTFIX -> EVALUASI) ---

def prioritas_operator(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0

def pisah_token(ekspresi):
    """Memecah string ekspresi menjadi token (angka multi-digit & operator)."""
    tokens = []
    i = 0
    n = len(ekspresi)
    while i < n:
        c = ekspresi[i]
        if c == ' ':
            i += 1
            continue
        if c in '0123456789':
            num = ''
            while i < n and ekspresi[i] in '0123456789':
                num += ekspresi[i]
                i += 1
            tokens.append(num)
        else:
            tokens.append(c)
            i += 1
    return tokens

def ke_postfix(ekspresi):
    """Mengubah ekspresi Infix ke Postfix menggunakan Stack operator."""
    tokens = pisah_token(ekspresi)
    output = []
    op_stack = Stack()

    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token == '(':
            op_stack.push(token)
        elif token == ')':
            while not op_stack.is_empty() and op_stack.peek() != '(':
                output.append(op_stack.pop())
            op_stack.pop()  # Buang '('
        else:
            while (not op_stack.is_empty() and 
                   op_stack.peek() != '(' and 
                   prioritas_operator(op_stack.peek()) >= prioritas_operator(token)):
                output.append(op_stack.pop())
            op_stack.push(token)

    while not op_stack.is_empty():
        output.append(op_stack.pop())

    return output

def hitung_postfix(postfix_tokens):
    """Mengevaluasi ekspresi Postfix menggunakan Stack nilai."""
    val_stack = Stack()

    for token in postfix_tokens:
        if token.isdigit():
            val_stack.push(int(token))
        else:
            b = val_stack.pop()  # Pop operand kanan lebih dulu
            a = val_stack.pop()  # Pop operand kiri
            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                res = a // b
            val_stack.push(res)

    return val_stack.pop()


# --- MANAJER UNDO / REDO ---

class ManajerUndoRedo:
    def __init__(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def catat_aksi(self, tipe, data):
        self.redo_stack = Stack()  # Kosongkan redo tiap kali ada aksi baru
        self.undo_stack.push((tipe, data))

    def undo(self, antrean_naif, antrean_circular):
        if self.undo_stack.is_empty():
            print("Tidak ada aksi yang bisa dibatalkan.")
            return None

        aksi = self.undo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            # Kebalikan ENQUEUE: buang dari belakang
            antrean_naif.data.pop()
            antrean_circular.count -= 1
            antrean_circular.rear = (antrean_circular.rear - 1) % antrean_circular.capacity
            print(f"Undo ENQUEUE: {data} dibatalkan.")

        elif tipe == "DEQUEUE":
            # Kebalikan DEQUEUE: kembalikan pesanan ke depan antrean
            items = data if isinstance(data, list) else [data]
            for item in reversed(items):
                antrean_naif.data.insert(0, item)
                antrean_circular.front = (antrean_circular.front - 1) % antrean_circular.capacity
                antrean_circular.data[antrean_circular.front] = item
                antrean_circular.count += 1
            print(f"Undo DEQUEUE: {len(items)} pesanan dikembalikan ke depan.")

        self.redo_stack.push(aksi)

    def redo(self, antrean_naif, antrean_circular):
        if self.redo_stack.is_empty():
            print("Tidak ada aksi untuk di-redo.")
            return None

        aksi = self.redo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            antrean_naif.enqueue(data)
            antrean_circular.enqueue(data)
            print(f"Redo ENQUEUE: {data} dikerjakan ulang.")

        elif tipe == "DEQUEUE":
            items = data if isinstance(data, list) else [data]
            for _ in range(len(items)):
                antrean_naif.dequeue()
                antrean_circular.dequeue()
            print(f"Redo DEQUEUE: {len(items)} pesanan dikeluarkan lagi.")

        self.undo_stack.push(aksi)


if __name__ == "__main__":
    print("=== 1. UJI KASIR STACK (INFIX -> POSTFIX) ===")
    struk = "(3*12000)+(2*8500)-5000"
    postfix = ke_postfix(struk)
    total = hitung_postfix(postfix)
    print(f"Infix   : {struk}")
    print(f"Postfix : {' '.join(postfix)}")
    print(f"Total   : Rp {total:,}")

    print("\n=== 2. UJI QUEUE & UNDO/REDO ===")
    q_naif = AntreanNaif()
    q_circ = AntreanMelingkar()
    manager = ManajerUndoRedo()

    # Tambah Pesanan
    q_naif.enqueue("O-000001")
    q_circ.enqueue("O-000001")
    manager.catat_aksi("ENQUEUE", "O-000001")

    q_naif.enqueue("O-000002")
    q_circ.enqueue("O-000002")
    manager.catat_aksi("ENQUEUE", "O-000002")

    print(f"Panjang Naif: {q_naif.size()}, Circular: {q_circ.size()}")

    # Jalankan Undo
    manager.undo(q_naif, q_circ)
    print(f"Panjang setelah Undo: Naif {q_naif.size()}, Circular {q_circ.size()}")

    # Jalankan Redo
    manager.redo(q_naif, q_circ)
    print(f"Panjang setelah Redo: Naif {q_naif.size()}, Circular {q_circ.size()}")