"""Tes M2. Jalankan dari root repo:  python tests/test_m2.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.m2_antrean import (Stack, AntreanNaif, AntreanMelingkar,
                                ManajerUndoRedo, ke_postfix, hitung_postfix,
                                proses_kasir, format_rupiah)


def isi(q):
    out = []
    for i in range(len(q)):
        out.append(q.get(i))
    return out


def gabung(tokens):
    return " ".join(tokens)


def hitung(e):
    return hitung_postfix(ke_postfix(e))


def galat(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def uji_stack():
    s = Stack()
    assert s.is_empty() and s.pop() is None and s.peek() is None
    for x in (1, 2, 3):
        s.push(x)
    assert s.peek() == 3 and s.size() == 3
    assert s.pop() == 3 and s.pop() == 2 and s.pop() == 1
    assert s.pop() is None


def uji_postfix_empat_bentuk():
    assert gabung(ke_postfix("3+4*2")) == "3 4 2 * +"
    assert hitung("3+4*2") == 11
    assert gabung(ke_postfix("(1+2)*3")) == "1 2 + 3 *"
    assert hitung("(1+2)*3") == 9
    assert gabung(ke_postfix("10-3-2")) == "10 3 - 2 -"
    assert hitung("10-3-2") == 5
    assert gabung(ke_postfix("((2+3)*(4-1))")) == "2 3 + 4 1 - *"
    assert hitung("((2+3)*(4-1))") == 15


def uji_struk_kasir():
    e = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
    postfix, total, langkah = proses_kasir(e)
    assert gabung(postfix) == "3 12000 * 2 8500 * + 5000 -"
    assert total == 48000
    assert format_rupiah(total) == "Rp 48.000"
    assert format_rupiah(0) == "Rp 0" and format_rupiah(1234567) == "Rp 1.234.567"
    # tanda ( tidak pernah muncul di kolom keluaran
    for baris in langkah:
        assert "(" not in baris[4]


def uji_urutan_pop():
    assert hitung("10-4") == 6
    assert hitung("20/4") == 5
    assert hitung("8/2/2") == 2
    assert hitung("100-30/5") == 94


def uji_ekspresi_salah():
    for e in ("(1+2", "1+2)", "1+", "5/0", "1 $ 2", ""):
        assert galat(hitung, e), e


def uji_antrean_naif():
    q = AntreanNaif()
    assert q.dequeue() is None
    for x in range(5):
        q.enqueue(x)
    for x in range(5):
        assert q.dequeue() == x
    assert q.total_geseran == 4 + 3 + 2 + 1 + 0
    assert q.dequeue() is None


def uji_circular_berputar():
    q = AntreanMelingkar(4)
    for x in ("a", "b", "c"):
        q.enqueue(x)
    assert q.dequeue() == "a" and q.dequeue() == "b"
    for x in ("d", "e", "f"):
        q.enqueue(x)
    assert q.capacity == 4                    # tidak tumbuh, penunjuk berputar
    assert isi(q) == ["c", "d", "e", "f"]
    q.enqueue("g")                            # penuh -> tumbuh, urutan terjaga
    assert q.capacity == 8
    assert isi(q) == ["c", "d", "e", "f", "g"]
    for x in ("c", "d", "e", "f", "g"):
        assert q.dequeue() == x
    assert q.is_empty() and q.dequeue() is None


def uji_circular_kosong_vs_penuh():
    q = AntreanMelingkar(2)
    q.enqueue(1)
    q.enqueue(2)
    assert not q.is_empty() and q.count == 2
    q.dequeue()
    q.dequeue()
    assert q.is_empty() and q.front == q.rear
    q.enqueue(9)
    assert q.dequeue() == 9


def uji_circular_tumbuh_banyak():
    q = AntreanMelingkar(4)
    for x in range(100):
        q.enqueue(x)
    assert isi(q) == list(range(100))


def uji_push_depan_saat_penuh():
    q = AntreanMelingkar(4)
    for x in ("a", "b", "c", "d"):
        q.enqueue(x)
    q.push_depan("x")                         # tidak boleh menimpa
    assert q.capacity == 8
    assert isi(q) == ["x", "a", "b", "c", "d"]


def uji_naif_vs_circular_sama():
    m = ManajerUndoRedo()
    for x in range(50):
        m.enqueue("O-" + str(x))
    items, ms_n, ms_c = m.dequeue(30)
    assert len(items) == 30 and items[0] == "O-0"
    assert isi(m.naif) == isi(m.circular)
    assert m.naif.total_geseran > 0 and m.circular.total_geseran == 0


def uji_undo_redo_enqueue():
    m = ManajerUndoRedo()
    m.enqueue("A")
    m.enqueue("B")
    m.undo_last()
    assert isi(m.naif) == ["A"] and isi(m.circular) == ["A"]
    m.redo_last()
    assert isi(m.naif) == ["A", "B"] and isi(m.circular) == ["A", "B"]


def uji_undo_redo_dequeue():
    m = ManajerUndoRedo(AntreanNaif(), AntreanMelingkar(4))
    for x in range(10):
        m.enqueue("O" + str(x))
    items, _, _ = m.dequeue(4)
    assert items == ["O0", "O1", "O2", "O3"]
    m.undo_last()                              # kembali ke DEPAN circular, urutan asli
    awal = ["O" + str(x) for x in range(10)]
    assert isi(m.circular) == awal
    assert m.naif.size() == 6                  # naif belum disalin (sengaja)
    m.sinkron_naif()
    assert isi(m.naif) == awal
    m.redo_last()
    assert isi(m.circular) == awal[4:]
    m.sinkron_naif()
    assert isi(m.naif) == awal[4:]


def uji_enqueue_saat_naif_basi():
    m = ManajerUndoRedo()
    for x in ("A", "B", "C", "D"):
        m.enqueue(x)
    m.dequeue(2)
    m.undo_last()                              # naif basi
    m.enqueue("Z")                             # tetap harus masuk ke naif nanti
    m.undo_last()                              # undo ENQUEUE Z
    m.redo_last()                              # redo ENQUEUE Z
    m.sinkron_naif()
    assert isi(m.circular) == ["A", "B", "C", "D", "Z"]
    assert isi(m.naif) == isi(m.circular)
    m.dequeue(1)                               # dequeue memanggil sinkron sendiri
    assert isi(m.naif) == isi(m.circular) == ["B", "C", "D", "Z"]


def uji_redo_dikosongkan_aksi_baru():
    m = ManajerUndoRedo()
    m.enqueue("A")
    m.undo_last()
    assert m.redo_stack.size() == 1
    m.enqueue("B")                             # aksi baru
    assert m.redo_stack.size() == 0
    assert "kosong" in m.redo_last()
    assert isi(m.circular) == ["B"]


def uji_undo_kosong_dan_history():
    m = ManajerUndoRedo()
    assert "Tidak ada" in m.undo_last()
    m.enqueue("A")
    m.enqueue("B")
    m.dequeue(1)
    h = m.history()
    assert len(h) == 3 and h[0][0] == "ENQUEUE" and h[2][0] == "DEQUEUE"
    m.undo_last()
    assert len(m.history()) == 2               # konsisten dengan history()
    daftar = dict_tanpa(m.stats())
    assert daftar["undo_depth"] == 2 and daftar["redo_depth"] == 1


def dict_tanpa(pasangan):
    """Pembantu tes saja: cari nilai berdasarkan nama."""
    class Hasil:
        def __init__(self, p):
            self.p = p

        def __getitem__(self, nama):
            for k, v in self.p:
                if k == nama:
                    return v
            raise KeyError(nama)
    return Hasil(pasangan)


if __name__ == "__main__":
    tes = [uji_stack, uji_postfix_empat_bentuk, uji_struk_kasir,
           uji_urutan_pop, uji_ekspresi_salah, uji_antrean_naif,
           uji_circular_berputar, uji_circular_kosong_vs_penuh,
           uji_circular_tumbuh_banyak, uji_push_depan_saat_penuh,
           uji_naif_vs_circular_sama, uji_undo_redo_enqueue,
           uji_undo_redo_dequeue, uji_enqueue_saat_naif_basi,
           uji_redo_dikosongkan_aksi_baru,
           uji_undo_kosong_dan_history]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print("\nSemua tes M2 lulus.")