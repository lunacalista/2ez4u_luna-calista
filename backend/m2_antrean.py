"""M2: Stack & Queue (kasir postfix, undo/redo, antrean naif vs melingkar).

Aturan: tanpa dict, set, sorted, .sort(), heapq, bisect, collections.*.
Stack dan AntreanNaif dibangun di atas Array milik M1.
"""
import time

try:
    from backend.m1_pesanan import Array, baca_csv   # dari root repo
except ImportError:
    from m1_pesanan import Array, baca_csv           # langsung dari backend/


# Stack (LIFO) di atas Array M1
class Stack:
    """Tumpukan (LIFO). push/pop di ujung Array, jadi keduanya O(1)."""
    def __init__(self):
        self.items = Array()

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.delete(self.items.size - 1)

    def peek(self):
        if self.is_empty():
            return None
        return self.items.get(self.items.size - 1)

    def is_empty(self):
        return self.items.size == 0

    def size(self):
        return self.items.size

    def teks(self):
        """Isi stack dari dasar ke puncak, untuk tabel langkah di UI."""
        if self.is_empty():
            return "kosong"
        s = ""
        for i in range(self.items.size):
            if i > 0:
                s += " "
            s += str(self.items.get(i))
        return s


# Antrean naif: Array biasa, dequeue menggeser seluruh sisa isi
class AntreanNaif:
    """Antrean naif. dequeue mengambil indeks 0 lalu menggeser sisa: O(n)."""
    def __init__(self):
        self.data = Array()
        self.total_geseran = 0

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        self.total_geseran += self.data.size - 1   # jumlah elemen yang digeser
        return self.data.delete(0)

    # dipakai undo
    def pop_belakang(self):
        if self.is_empty():
            return None
        return self.data.delete(self.data.size - 1)

    def push_depan(self, item):
        self.data.insert(0, item)

    def get(self, i):
        return self.data.get(i)

    def is_empty(self):
        return self.data.size == 0

    def size(self):
        return self.data.size

    def __len__(self):
        return self.data.size


# Antrean melingkar
class AntreanMelingkar:
    """Antrean melingkar. dequeue hanya memajukan front: O(1).

    Keputusan kasus penuh: kapasitas TUMBUH 2x (enqueue tidak pernah ditolak).
    Keputusan penanda kosong/penuh: memakai pencacah `count`, karena
    front == rear bisa berarti kosong ATAU penuh.
    """
    def __init__(self, capacity=4):
        if capacity < 1:
            capacity = 1
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geseran = 0      # selalu 0, disimpan untuk perbandingan

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

    # dipakai undo
    def pop_belakang(self):
        if self.is_empty():
            return None
        self.rear = (self.rear - 1) % self.capacity
        item = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return item

    def push_depan(self, item):
        if self.count == self.capacity:      # penuh: tumbuh dulu, jangan menimpa
            self._resize(self.capacity * 2)
        self.front = (self.front - 1) % self.capacity
        self.data[self.front] = item
        self.count += 1

    def get(self, i):
        """Elemen ke-i secara logis (0 = paling depan)."""
        if i < 0 or i >= self.count:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[(self.front + i) % self.capacity]

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count

    def __len__(self):
        return self.count


# Kasir: infix -> postfix -> total
def format_rupiah(n):
    negatif = n < 0
    if negatif:
        n = -n
    s = str(n)
    hasil = ""
    hitung = 0
    for i in range(len(s) - 1, -1, -1):
        if hitung == 3:
            hasil = "." + hasil
            hitung = 0
        hasil = s[i] + hasil
        hitung += 1
    if negatif:
        return "-Rp " + hasil
    return "Rp " + hasil


def prioritas_operator(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0


def _adalah_angka(token):
    """True bila token hanya berisi digit 0-9 ASCII (str.isdigit() menerima '²')."""
    if len(token) == 0:
        return False
    for c in token:
        if c not in '0123456789':
            return False
    return True


def pisah_token(ekspresi):
    """Memecah string menjadi token (angka multi-digit, operator, kurung)."""
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


def _gabung(tokens):
    s = ""
    for i in range(len(tokens)):
        if i > 0:
            s += " "
        s += tokens[i]
    return s


def ke_postfix(ekspresi, langkah=None):
    """Infix -> postfix memakai Stack operator.

    Bila `langkah` (list) diberikan, setiap token dicatat sebagai tuple
    (no, token, tindakan, isi_stack, keluaran) untuk tabel di UI.

    Struktur infix divalidasi lewat penanda `butuh_operand`: setelah operator
    atau "(" token berikutnya harus angka/"(", setelah angka atau ")" token
    berikutnya harus operator/")". Tanpa ini, "2 3 +" lolos dan dihitung 5.
    """
    tokens = pisah_token(ekspresi)
    output = []
    op_stack = Stack()
    nomor = 0
    butuh_operand = True

    for token in tokens:
        nomor += 1
        if _adalah_angka(token):
            if not butuh_operand:
                raise ValueError("Dua angka berurutan tanpa operator")
            output.append(token)
            butuh_operand = False
            tindakan = "angka, langsung keluar"
        elif token == '(':
            if not butuh_operand:
                raise ValueError("Kurung buka tidak boleh langsung setelah angka atau kurung tutup")
            op_stack.push(token)
            tindakan = "push ("
        elif token == ')':
            if butuh_operand:
                raise ValueError("Kurung tutup tidak boleh setelah operator atau kurung buka")
            ketemu = False
            while not op_stack.is_empty():
                atas = op_stack.pop()
                if atas == '(':
                    ketemu = True
                    break
                output.append(atas)
            if not ketemu:
                raise ValueError("Kurung tutup tanpa pasangan")
            tindakan = "pop sampai ( , buang ("
        elif token in ('+', '-', '*', '/'):
            if butuh_operand:
                raise ValueError("Operator tanpa operand di kirinya")
            ada_pop = False
            while (not op_stack.is_empty() and
                   op_stack.peek() != '(' and
                   prioritas_operator(op_stack.peek()) >= prioritas_operator(token)):
                output.append(op_stack.pop())
                ada_pop = True
            op_stack.push(token)
            butuh_operand = True
            if ada_pop:
                tindakan = "pop yang lebih/sama kuat, push " + token
            else:
                tindakan = "push " + token
        else:
            raise ValueError("Karakter tidak dikenali: " + token)

        if langkah is not None:
            langkah.append(("1." + str(nomor), token, tindakan,
                            op_stack.teks(), _gabung(output)))

    if butuh_operand:
        raise ValueError("Ekspresi kosong atau tidak lengkap")

    while not op_stack.is_empty():
        atas = op_stack.pop()
        if atas == '(':
            raise ValueError("Kurung buka tanpa pasangan")
        output.append(atas)

    if langkah is not None:
        langkah.append(("1.akhir", "-", "pop sisa stack",
                        "kosong", _gabung(output)))
    return output


def hitung_postfix(postfix_tokens, langkah=None):
    """Mengevaluasi postfix memakai Stack nilai. Operand KANAN di-pop dulu."""
    val_stack = Stack()
    nomor = 0

    for token in postfix_tokens:
        nomor += 1
        if _adalah_angka(token):
            val_stack.push(int(token))
            tindakan = "operand, push " + token
        else:
            if val_stack.size() < 2:
                raise ValueError("Ekspresi tidak valid")
            b = val_stack.pop()      # kanan lebih dulu
            a = val_stack.pop()      # kiri
            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                if b == 0:
                    raise ValueError("Pembagian dengan nol")
                res = a // b
            else:
                raise ValueError("Operator tidak dikenali: " + token)
            val_stack.push(res)
            tindakan = f"pop {b} dan {a} -> {a}{token}{b} = {res}"

        if langkah is not None:
            langkah.append(("2." + str(nomor), token, tindakan,
                            val_stack.teks(), ""))

    if val_stack.size() != 1:
        raise ValueError("Ekspresi tidak valid")
    return val_stack.pop()


def proses_kasir(ekspresi):
    """Konversi + evaluasi sekaligus. Mengembalikan (postfix, total, langkah)."""
    langkah = []
    postfix = ke_postfix(ekspresi, langkah)
    total = hitung_postfix(postfix, langkah)
    return postfix, total, langkah


# Manajer: aksi antrean + undo/redo, menjaga kedua antrean tetap sama
def _nama(item):
    """oid bila item adalah Pesanan, selain itu teksnya sendiri."""
    if hasattr(item, "oid"):
        return item.oid
    return str(item)


class ManajerUndoRedo:
    def __init__(self, antrean_naif=None, antrean_circular=None):
        self.naif = antrean_naif if antrean_naif is not None else AntreanNaif()
        self.circular = (antrean_circular if antrean_circular is not None
                         else AntreanMelingkar())
        self.undo_stack = Stack()
        self.redo_stack = Stack()
        # Undo/redo DEQUEUE hanya menyentuh antrean circular (O(1) per pesanan).
        # Antrean naif ditandai "basi" dan disalin ulang dari circular saat
        # dibutuhkan, di luar hitungan waktu undo/redo.
        self._naif_basi = False

    def sinkron_naif(self):
        """Menyalin isi circular ke antrean naif bila naif sudah basi - O(n)."""
        if not self._naif_basi:
            return
        baru = Array()
        for i in range(self.circular.size()):
            baru.append(self.circular.get(i))
        self.naif.data = baru
        self._naif_basi = False

    def _catat(self, tipe, data):
        self.undo_stack.push((tipe, data))
        self.redo_stack = Stack()            # aksi baru mengosongkan redo

    def enqueue(self, item):
        if not self._naif_basi:       # bila basi, nanti disalin dari circular
            self.naif.enqueue(item)
        self.circular.enqueue(item)
        self._catat("ENQUEUE", item)

    def dequeue(self, n=1):
        """Mengeluarkan n pesanan dari KEDUA antrean.

        Mengembalikan (daftar_item, ms_naif, ms_circular).
        Yang dicatat untuk undo adalah DAFTAR pesanannya, bukan hitungannya.
        """
        self.sinkron_naif()
        if n > self.circular.size():
            n = self.circular.size()
        t0 = time.perf_counter()
        for _ in range(n):
            self.naif.dequeue()
        ms_naif = (time.perf_counter() - t0) * 1000

        items = []
        t0 = time.perf_counter()
        for _ in range(n):
            items.append(self.circular.dequeue())
        ms_circ = (time.perf_counter() - t0) * 1000

        if len(items) > 0:
            self._catat("DEQUEUE", items)
        return items, ms_naif, ms_circ

    def _dequeue_satu(self, antrean, tipe, n):
        if n > antrean.size():
            n = antrean.size()
        items = []
        t0 = time.perf_counter()
        for _ in range(n):
            items.append(antrean.dequeue())
        ms = (time.perf_counter() - t0) * 1000
        if len(items) > 0:
            self._catat(tipe, items)
        return items, ms

    def dequeue_naif(self, n=1):
        """Mengeluarkan n pesanan hanya dari antrean NAIF. Mengembalikan (daftar, ms).

        sinkron_naif() dipanggil dulu: kalau naif basi (habis undo/redo DEQUEUE),
        tanpa ini yang dikeluarkan adalah isi lama yang sudah tidak berlaku.
        Sinkron di luar pengukuran waktu.
        """
        self.sinkron_naif()
        return self._dequeue_satu(self.naif, "DEQUEUE_NAIF", n)

    def dequeue_circular(self, n=1):
        """Mengeluarkan n pesanan hanya dari antrean MELINGKAR. Mengembalikan (daftar, ms)."""
        return self._dequeue_satu(self.circular, "DEQUEUE_CIRCULAR", n)

    def undo_last(self):
        if self.undo_stack.is_empty():
            return "Tidak ada aksi yang bisa dibatalkan."
        aksi = self.undo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            if not self._naif_basi:
                self.naif.pop_belakang()
            self.circular.pop_belakang()
            pesan = f"Pembatalan enqueue: {_nama(data)} dikeluarkan lagi dari belakang."
        elif tipe == "DEQUEUE_NAIF":
            for i in range(len(data) - 1, -1, -1):
                self.naif.push_depan(data[i])
            pesan = f"Pembatalan dequeue: {len(data)} pesanan dikembalikan ke DEPAN antrean naif."
        elif tipe == "DEQUEUE_CIRCULAR":
            for i in range(len(data) - 1, -1, -1):
                self.circular.push_depan(data[i])
            pesan = f"Pembatalan dequeue: {len(data)} pesanan dikembalikan ke DEPAN antrean circular."
        else:  # DEQUEUE: kembalikan ke DEPAN antrean circular, urutan dijaga
            for i in range(len(data) - 1, -1, -1):
                self.circular.push_depan(data[i])
            self._naif_basi = True
            pesan = f"Pembatalan dequeue: {len(data)} pesanan dikembalikan ke DEPAN antrean circular."

        self.redo_stack.push(aksi)
        return pesan

    def redo_last(self):
        if self.redo_stack.is_empty():
            return "Tumpukan redo kosong, tidak ada yang diulang."
        aksi = self.redo_stack.pop()
        tipe, data = aksi

        if tipe == "ENQUEUE":
            if not self._naif_basi:
                self.naif.enqueue(data)
            self.circular.enqueue(data)
            pesan = f"Enqueue dikerjakan lagi: {_nama(data)} masuk kembali ke belakang."
        elif tipe == "DEQUEUE_NAIF":
            for _ in range(len(data)):
                self.naif.dequeue()
            pesan = f"Dequeue dikerjakan lagi: {len(data)} pesanan keluar lagi dari antrean naif."
        elif tipe == "DEQUEUE_CIRCULAR":
            for _ in range(len(data)):
                self.circular.dequeue()
            pesan = f"Dequeue dikerjakan lagi: {len(data)} pesanan keluar lagi dari antrean circular."
        else:
            for _ in range(len(data)):
                self.circular.dequeue()
            self._naif_basi = True
            pesan = f"Dequeue dikerjakan lagi: {len(data)} pesanan keluar lagi dari antrean circular."

        self.undo_stack.push(aksi)           # tidak mengosongkan redo
        return pesan

    def history(self):
        """Riwayat aksi (yang masih bisa di-undo), dari terlama ke terbaru."""
        hasil = []
        for i in range(self.undo_stack.size()):
            hasil.append(self.undo_stack.items.get(i))
        return hasil

    def stats(self):
        """Daftar (nama, nilai) untuk ditampilkan di UI."""
        self.sinkron_naif()
        return [
            ("queue_len_naif", self.naif.size()),
            ("queue_len_circular", self.circular.size()),
            ("queue_capacity", self.circular.capacity),
            ("total_geseran_naif", self.naif.total_geseran),
            ("total_geseran_circular", self.circular.total_geseran),
            ("undo_depth", self.undo_stack.size()),
            ("redo_depth", self.redo_stack.size()),
        ]


def demo():
    print("=== 1. KASIR STACK ===")
    postfix, total, langkah = proses_kasir("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
    print("Postfix :", _gabung(postfix))
    print("TOTAL   :", format_rupiah(total))

    print("\n=== 2. QUEUE + UNDO/REDO ===")
    m = ManajerUndoRedo()
    m.enqueue("O-000001")
    m.enqueue("O-000002")
    m.enqueue("O-000003")
    print(m.dequeue(2)[0])
    print(m.undo_last())
    print(m.redo_last())
    print(m.stats())


# Pemuatan data: antrean diisi pesanan berstatus ANTRE dari CSV
def _muat_antre(path):
    """Mengambil oid pesanan berstatus ANTRE (urutan file)."""
    semua = baca_csv(path)
    antre = []
    for i in range(len(semua)):
        p = semua.get(i)
        if p.status == "ANTRE":
            antre.append(p.oid)
    return antre


def _manajer_baru(antre):
    """Manajer segar; kedua antrean diisi data yang persis sama."""
    m = ManajerUndoRedo()
    for oid in antre:
        m.naif.enqueue(oid)
        m.circular.enqueue(oid)
    return m


if __name__ == "__main__":
    demo()