"""Tes M1. Jalankan dari root repo:  python tests/test_m1.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.m1_pesanan import Array, LinkList


def isi_array(a):
    out = [None] * len(a)
    for i in range(len(a)):
        out[i] = a.get(i)
    return out


def isi_ll(l):
    out = [None] * len(l)
    for i in range(len(l)):
        out[i] = l.get(i)
    return out


def tegak(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def uji_kosong():
    for s in (Array(), LinkList()):
        assert len(s) == 0
        assert tegak(IndexError, s.get, 0)
        assert tegak(IndexError, s.delete, 0)


def uji_resize():
    a = Array(4)
    for i in range(4):
        a.append(i)
    assert a.capacity == 4
    a.append(4)
    assert a.capacity == 8 and len(a) == 5
    assert isi_array(a) == [0, 1, 2, 3, 4]
    for i in range(5, 100):
        a.append(i)
    assert isi_array(a) == list(range(100))


def uji_insert_posisi():
    for S in (Array, LinkList):
        s = S()
        for x in ("a", "b", "c"):
            s.append(x)
        s.insert(0, "depan")
        s.insert(2, "tengah")
        s.insert(len(s), "belakang")
        isi = isi_array(s) if S is Array else isi_ll(s)
        assert isi == ["depan", "a", "tengah", "b", "c", "belakang"], isi
        assert tegak(IndexError, s.insert, -1, "x")
        assert tegak(IndexError, s.insert, len(s) + 1, "x")


def uji_delete_posisi():
    for S in (Array, LinkList):
        s = S()
        for x in range(6):
            s.append(x)
        f = isi_array if S is Array else isi_ll
        assert s.delete(0) == 0            # depan
        assert s.delete(2) == 3            # tengah
        assert s.delete(len(s) - 1) == 5   # belakang
        assert f(s) == [1, 2, 4], f(s)
        assert tegak(IndexError, s.delete, 3)
        assert tegak(IndexError, s.delete, -1)


def uji_tail_linklist():
    l = LinkList()
    l.append(1)
    l.append(2)
    l.delete(1)                  # hapus tail
    assert l.tail.value == 1 and l.tail.next is None
    l.append(3)                  # tail harus tetap benar
    assert isi_ll(l) == [1, 3]
    l.delete(0)
    l.delete(0)                  # kosong lagi
    assert l.head is None and l.tail is None
    l.append(9)
    assert l.head is l.tail and l.get(0) == 9


def uji_aturan_bisnis():
    for S in (Array, LinkList):
        s = S()
        f = isi_array if S is Array else isi_ll
        s.tambah_reguler("R1")
        s.tambah_reguler("R2")
        s.tambah_reguler("R3")
        s.tambah_reguler("R4")
        s.tambah_prioritas("P1")     # size 4 -> posisi 2
        assert f(s) == ["R1", "R2", "P1", "R3", "R4"], f(s)
        s.tambah_vip("V1")
        assert f(s) == ["V1", "R1", "R2", "P1", "R3", "R4"], f(s)
        s.tambah_reguler("R5")
        assert f(s)[-1] == "R5"


def uji_array_dan_linklist_sama():
    a, l = Array(), LinkList()
    urutan = ("R", "P", "V", "R", "R", "P", "V", "P", "R")
    for n, jenis in enumerate(urutan):
        nama = jenis + str(n)
        if jenis == "R":
            a.tambah_reguler(nama); l.tambah_reguler(nama)
        elif jenis == "P":
            a.tambah_prioritas(nama); l.tambah_prioritas(nama)
        else:
            a.tambah_vip(nama); l.tambah_vip(nama)
    assert isi_array(a) == isi_ll(l)
    a.hapus_pesanan(3); l.hapus_pesanan(3)
    assert isi_array(a) == isi_ll(l)


if __name__ == "__main__":
    tes = [uji_kosong, uji_resize, uji_insert_posisi, uji_delete_posisi,
           uji_tail_linklist, uji_aturan_bisnis, uji_array_dan_linklist_sama]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print("\nSemua tes M1 lulus.")