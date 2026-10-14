"""Antarmuka Tkinter: 2EZ4U Food Delivery.

Satu jendela, tiga bagian: daftar menu di kiri, form + hasil di kanan,
panel COMMAND di bawah (perintah yang sudah dijalankan beserta modul dan
waktunya). Jalankan dari root repo:  python app.py

Aturan proyek berlaku juga di sini: tanpa dict, set, sorted, .sort(),
heapq, bisect, collections, maupun literal {} dan comprehension dict/set.
"""
import os
import sys
import time

def _cari_root():
    """Folder root repo: yang berisi data/pesanan.csv. Dicoba induk folder ui.py
    (ui.py di frontend/), folder ui.py sendiri, lalu folder kerja saat ini."""
    sini = os.path.dirname(os.path.abspath(__file__))
    for kandidat in (os.path.join(sini, ".."), sini, os.getcwd()):
        kandidat = os.path.abspath(kandidat)
        if os.path.exists(os.path.join(kandidat, "data", "pesanan.csv")):
            return kandidat
    return os.path.abspath(os.path.join(sini, ".."))


_ROOT = _cari_root()
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:          
    tk = None
    ttk = None

from backend.m1_pesanan import Array, LinkList, Pesanan, baca_csv, ukur
from backend.m2_antrean import ManajerUndoRedo, proses_kasir, format_rupiah
from backend.m3_laporan import (jalankan_sort, jalankan_cari,
                                bangun_indeks_oid, array_ke_list, kunci_oid)

BATAS_TAMPIL = 200000    # baris tabel yang ditampilkan paling banyak (200000 = semua)


# Pembantu format
def angka(n):
    """1234567 -> '1.234.567'."""
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
        return "-" + hasil
    return hasil


def fmt_ms(ms):
    """Waktu dalam ms; operasi sangat cepat diberi lebih banyak desimal."""
    if ms < 0.1:
        return f"{ms:.3f}"
    return f"{ms:.2f}"


def jam(detik):
    """Detik sejak 00:00 -> 'HH:MM:SS'; None -> '-'."""
    if detik is None:
        return "-"
    detik = detik % 86400
    h = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def detail(p):
    """Satu pesanan sebagai daftar pasangan (kolom, isi)."""
    return [("oid", p.oid), ("pelanggan", p.pelanggan), ("resto", p.resto),
            ("menu", p.menu), ("harga", angka(p.harga)),
            ("prioritas", str(p.prioritas)), ("masuk", jam(p.t_masuk)),
            ("selesai", jam(p.t_selesai)), ("status", p.status)]


def baris_pesanan(nomor, p):
    return (str(nomor), p.oid, p.pelanggan, p.resto, p.menu, jam(p.t_masuk))


KOLOM_PESANAN = ("#", "oid", "pelanggan", "resto", "menu", "masuk")


class Hasil:
    """Keluaran satu perintah, siap ditampilkan UI."""
    def __init__(self, perintah, modul, ms, ringkas, kolom=None, baris=None):
        self.perintah = perintah
        self.modul = modul
        self.ms = ms
        self.ringkas = ringkas            # daftar teks
        self.kolom = kolom if kolom is not None else ()
        self.baris = baris if baris is not None else []


# Kontroler: menjembatani UI dengan backend. Tanpa Tkinter, jadi bisa diuji.
class Kontroler:
    def __init__(self, path_csv=None):
        if path_csv is None:
            path_csv = os.path.join(_ROOT, "data", "pesanan.csv")
        self.path_csv = path_csv
        self.semua = None          # list Pesanan urutan file (untuk M3)
        self.arr = None            # Array M1
        self.ll = None             # LinkList M1
        self.manajer = None        # antrean naif + melingkar + undo/redo (M2)
        self.indeks_oid = None     # daftar terurut oid (dibangun sekali)
        self.oid_berikut = 1

    # umum
    def _perlu_data(self):
        if self.semua is None:
            raise ValueError("Data belum dimuat. Klik Load (menu DATA) dulu.")

    def _int(self, teks, label, awal, akhir):
        teks = teks.strip().replace(".", "").replace(",", "")
        if teks == "":
            raise ValueError(f"{label} harus diisi.")
        try:
            nilai = int(teks)
        except ValueError:
            raise ValueError(f"{label} harus berupa bilangan bulat.")
        if nilai < awal or nilai > akhir:
            raise ValueError(
                f"{label} harus antara {angka(awal)} dan {angka(akhir)}.")
        return nilai

    def _baru(self, nama, prioritas):
        nama = nama.strip()
        if nama == "":
            nama = "Pelanggan Baru"
        p = Pesanan("O-%06d" % self.oid_berikut, nama, "kafe-teknik",
                    "roti-bakar", 12000, prioritas, 28800, None, "ANTRE")
        self.oid_berikut += 1
        return p

    # DATA
    def load(self):
        if not os.path.exists(self.path_csv):
            raise ValueError(f"File tidak ditemukan: {self.path_csv}")
        awal = time.perf_counter()
        sumber = baca_csv(self.path_csv)

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

        semua = array_ke_list(sumber)
        manajer = ManajerUndoRedo()
        antre = 0
        for p in semua:
            if p.status == "ANTRE":
                manajer.naif.enqueue(p)
                manajer.circular.enqueue(p)
                antre += 1

        self.semua = semua
        self.arr = arr
        self.ll = ll
        self.manajer = manajer
        self.indeks_oid = None
        self.oid_berikut = len(semua) + 1
        total = (time.perf_counter() - awal) * 1000
        return Hasil("load", "M1 - larik", total, [
            f"{angka(len(semua))} pesanan dimuat dari data/pesanan.csv.",
            f"Isi Array: {ms_arr:.2f} ms | isi LinkList: {ms_ll:.2f} ms "
            "(keduanya lewat append, urutan file).",
            f"{angka(antre)} pesanan berstatus ANTRE masuk ke kedua antrean (M2).",
        ])

    # M1
    def _struktur(self, nama):
        self._perlu_data()
        if nama == "array":
            return self.arr, "array", "ARRAY"
        return self.ll, "linkedlist", "LINKEDLIST"

    def _panjang(self):
        return (f"Panjang sekarang: array {angka(len(self.arr))}, "
                f"linkedlist {angka(len(self.ll))}.")

    def m1_lihat(self, nama, teks):
        s, kode, label = self._struktur(nama)
        n = len(s)
        if n == 0:
            raise ValueError(f"{label} kosong.")
        if teks.strip() == "":
            idx = n // 2
        else:
            idx = self._int(teks, "Indeks", 0, n - 1)
        p, ms = ukur(s.lihat_pesanan, idx)
        return Hasil(f"{kode}_get", f"M1 - {kode}", ms,
                     [f"Pesanan pada indeks {angka(idx)} dari {angka(n)} ({label})."],
                     ("kolom", "isi"), detail(p))

    def m1_tambah(self, nama, jenis, pelanggan):
        s, kode, label = self._struktur(nama)
        n = len(s)
        if jenis == "reguler":
            prioritas, pos, ket = 3, n, "paling belakang"
        elif jenis == "prioritas":
            prioritas, pos, ket = 2, n // 2, "ke tengah barisan"
        else:
            prioritas, pos, ket = 1, 0, "langsung ke urutan pertama"
        p = self._baru(pelanggan, prioritas)
        _, ms = ukur(getattr(s, "tambah_" + jenis), p)
        return Hasil(f"{kode}_tambah_{jenis}", f"M1 - {kode}", ms,
                     [f"{p.oid} masuk {ket} ({label}), indeks {angka(pos)}.",
                      self._panjang()],
                     ("kolom", "isi"), detail(p))

    def m1_hapus(self, nama, teks):
        s, kode, label = self._struktur(nama)
        n = len(s)
        if n == 0:
            raise ValueError(f"{label} kosong.")
        if teks.strip() == "":
            idx = n // 2
        else:
            idx = self._int(teks, "Indeks", 0, n - 1)
        p, ms = ukur(s.hapus_pesanan, idx)
        return Hasil(f"{kode}_hapus", f"M1 - {kode}", ms,
                     [f"{p.oid} dicabut dari indeks {angka(idx)} ({label}).",
                      self._panjang()],
                     ("kolom", "isi"), detail(p))

    # M2
    def postfix(self, teks):
        if teks.strip() == "":
            raise ValueError("Struk belanja belum diisi.")
        (postfix, total, langkah), ms = ukur(proses_kasir, teks)
        gabung = ""
        for i in range(len(postfix)):
            if i > 0:
                gabung += " "
            gabung += postfix[i]
        return Hasil("stack_postfix", "M2 - stack", ms,
                     [f"Struk : {teks.strip()}", f"Postfix: {gabung}",
                      f"TOTAL : {format_rupiah(total)}"],
                     ("langkah", "token", "tindakan", "stack", "output"),
                     langkah)

    def _ringkas_antrean(self):
        m = self.manajer
        m.sinkron_naif()     # naif bisa basi sesudah undo/redo DEQUEUE gabungan
        return (f"Panjang antrean sekarang: naif {angka(m.naif.size())}, "
                f"circular {angka(m.circular.size())}.")

    def queue_enqueue(self, nama):
        self._perlu_data()
        m = self.manajer
        p = self._baru(nama, 3)
        _, ms = ukur(m.enqueue, p)
        return Hasil("queue_enqueue", "M2 - queue", ms,
                     [f"{p.oid} masuk paling belakang pada KEDUA antrean.",
                      self._ringkas_antrean()],
                     ("kolom", "isi"), detail(p))

    def queue_dequeue(self, jenis, teks):
        self._perlu_data()
        m = self.manajer
        m.sinkron_naif()     # ukuran naif harus yang terbaru sebelum divalidasi
        antrean = m.naif if jenis == "naif" else m.circular
        if antrean.size() == 0:
            raise ValueError("Antrean kosong, tidak ada yang bisa dikeluarkan.")
        k = self._int(teks, "Jumlah dequeue", 1, antrean.size())
        if jenis == "naif":
            g0 = m.naif.total_geseran
            items, ms = m.dequeue_naif(k)
            jml = len(items)
            g = m.naif.total_geseran - g0
            ringkas = [
                f"{angka(jml)} pesanan keluar dari depan antrean naif.",
                f"Total {angka(g)} elemen digeser, rata-rata "
                f"{angka(g // jml)} geseran per dequeue.",
                f"Sisa antrean naif {angka(m.naif.size())}.",
            ]
            modul = "M2 - queue naif"
        else:
            items, ms = m.dequeue_circular(k)
            jml = len(items)
            c = m.circular
            ringkas = [
                f"{angka(jml)} pesanan keluar dari depan antrean circular.",
                f"Tidak ada elemen yang digeser. front sekarang {angka(c.front)}, "
                f"rear {angka(c.rear)}, kapasitas {angka(c.capacity)}.",
                f"Sisa antrean circular {angka(c.size())}.",
            ]
            modul = "M2 - queue circular"
        if jml > BATAS_TAMPIL:
            ringkas.append(f"(Menampilkan {BATAS_TAMPIL} pesanan pertama.)")
        baris = []
        for i in range(min(jml, BATAS_TAMPIL)):
            baris.append(baris_pesanan(i + 1, items[i]))
        return Hasil(f"queue_dequeue_{jenis}", modul, ms, ringkas,
                     KOLOM_PESANAN, baris)

    def _undo_redo(self, jenis):
        self._perlu_data()
        m = self.manajer
        tumpukan = m.undo_stack if jenis == "undo" else m.redo_stack
        aksi = tumpukan.peek()
        if jenis == "undo":
            pesan, ms = ukur(m.undo_last)
        else:
            pesan, ms = ukur(m.redo_last)
        baris = []
        if aksi is not None:
            data = aksi[1]
            items = data if isinstance(data, list) else [data]
            for i in range(min(len(items), BATAS_TAMPIL)):
                p = items[i]
                baris.append((str(i + 1), p.oid, p.pelanggan, p.resto, p.menu))
        return Hasil(f"stack_{jenis}", "M2 - stack", ms,
                     [pesan, self._ringkas_antrean() +
                      f" Tumpukan undo {m.undo_stack.size()}, "
                      f"redo {m.redo_stack.size()}."],
                     ("#", "oid", "pelanggan", "resto", "menu"), baris)

    def undo(self):
        return self._undo_redo("undo")

    def redo(self):
        return self._undo_redo("redo")

    # M3
    def m3_sort(self, algoritma, teks_n, nama_kunci):
        self._perlu_data()
        label = nama_kunci.strip().lower()
        n = self._int(teks_n, "Jumlah baris", 1, len(self.semua))
        if label != "oid" and label != "harga" and label != "selesai":
            raise ValueError("Kunci harus oid, harga, atau selesai.")
        # insertion_sort melempar ValueError("DITOLAK: ...") bila n terlalu besar
        hasil, pc, ms = jalankan_sort(self.semua, n, label, algoritma)
        if algoritma == "insertion":
            perintah, modul = "insertion_sort", "M3 - insertion sort"
        else:
            perintah, modul = "merge_sort", "M3 - merge sort"
        ringkas = [
            f"{angka(n)} pesanan diurutkan menurut {label}.",
            f"{angka(pc.perbandingan)} perbandingan, "
            f"{angka(pc.pemindahan)} pemindahan.",
        ]
        if n > BATAS_TAMPIL:
            ringkas.append(f"(Menampilkan {BATAS_TAMPIL} baris pertama.)")
        baris = []
        for i in range(min(n, BATAS_TAMPIL)):
            p = hasil[i]
            baris.append((str(i + 1), p.oid, angka(p.harga), jam(p.t_selesai),
                          p.resto, p.menu))
        return Hasil(perintah, modul, ms, ringkas,
                     ("#", "oid", "harga", "selesai", "resto", "menu"), baris)

    def m3_linear(self, teks):
        self._perlu_data()
        oid = teks.strip().upper()
        if oid == "":
            raise ValueError("Nomor pesanan (oid) harus diisi.")
        idx, pc, ms = jalankan_cari(self.semua, oid, "linear", kunci_oid)
        return self._hasil_cari("linear_search", "M3 - linear search",
                                self.semua, oid, idx, pc, ms, [])

    def m3_binary(self, teks):
        self._perlu_data()
        oid = teks.strip().upper()
        if oid == "":
            raise ValueError("Nomor pesanan (oid) harus diisi.")
        awal = []
        if self.indeks_oid is None:
            self.indeks_oid, ms_bangun = ukur(bangun_indeks_oid, self.semua)
            awal.append("Daftar terurut oid dibangun sekali dengan merge sort, "
                        f"{ms_bangun:.2f} ms.")
        else:
            awal.append("Memakai daftar terurut oid yang sudah dibangun.")
        idx, pc, ms = jalankan_cari(self.indeks_oid, oid, "binary", kunci_oid)
        return self._hasil_cari("binary_search", "M3 - binary search",
                                self.indeks_oid, oid, idx, pc, ms, awal)

    def _hasil_cari(self, perintah, modul, larik, oid, idx, pc, ms, awal):
        ringkas = list(awal)
        if idx < 0:
            ringkas.append(f"Pesanan {oid} tidak ditemukan.")
            ringkas.append(f"{angka(pc.perbandingan)} perbandingan.")
            return Hasil(perintah, modul, ms, ringkas)
        if perintah == "linear_search":
            ringkas.append(f"Ditemukan pada indeks {angka(idx)}.")
        else:
            ringkas.append(f"Ditemukan pada baris ke-{angka(idx + 1)} "
                           f"dari {angka(len(larik))}.")
        ringkas.append(f"{angka(pc.perbandingan)} perbandingan.")
        return Hasil(perintah, modul, ms, ringkas, ("kolom", "isi"),
                     detail(larik[idx]))


# Definisi menu
class Isian:
    def __init__(self, label, awal="", tipe="entry", opsi=(), petunjuk=""):
        self.label = label
        self.awal = awal
        self.tipe = tipe            # "entry" atau "combo"
        self.opsi = opsi
        self.petunjuk = petunjuk


class Menu:
    def __init__(self, grup, label, aksi, tetap, judul, sub, isian, tombol,
                 catatan):
        self.grup = grup
        self.label = label
        self.aksi = aksi            # nama method Kontroler
        self.tetap = tetap          # argumen tetap di depan isian form
        self.judul = judul
        self.sub = sub
        self.isian = isian
        self.tombol = tombol
        self.catatan = catatan


def daftar_menu():
    g_data = "DATA"
    g1 = "M1 - DATA PESANAN"
    g2 = "M2 - STACK DAN QUEUE"
    g3 = "M3 - SORT DAN SEARCH"
    nama = Isian("Nama pelanggan", "Pelanggan Baru",
                 petunjuk="nama untuk pesanan yang akan dibuat")
    idx = Isian("Indeks pesanan", "",
                petunjuk="mulai dari 0; kosongkan untuk indeks tengah")
    m = []
    m.append(Menu(g_data, "Load", "load", (), "Data: muat pesanan.csv",
                  "Membaca pesanan.csv ke Array, LinkList, dan kedua antrean. "
                  "Lakukan sekali sebelum memakai menu lain.",
                  [], "LOAD",
                  "Array dan LinkList diisi dengan urutan file lewat append. "
                  "Perhatikan selisih waktunya: LinkList harus membuat 200.000 simpul."))

    for struktur, kode, nm in (("array", "ARRAY", "Array"),
                               ("linkedlist", "LINKEDLIST", "Linked List")):
        arr = (struktur == "array")
        m.append(Menu(g1, f"{kode} - LIHAT PESANAN", "m1_lihat", (struktur,),
                      f"{nm}: lihat pesanan ke-i",
                      "Membuka detail satu pesanan berdasarkan indeksnya.",
                      [idx], "LIHAT",
                      "Array menghitung alamat indeks langsung, jadi O(1) "
                      "berapa pun indeksnya." if arr else
                      "Linked list tidak punya alamat untuk indeks ke-i. "
                      "Harus menelusuri dari head, O(n)."))
        m.append(Menu(g1, f"{kode} - TAMBAH PESANAN REGULER", "m1_tambah",
                      (struktur, "reguler"),
                      f"{nm}: pesanan REGULER, masuk paling belakang",
                      "Pesanan reguler mengantre di ujung belakang barisan.",
                      [nama], "TAMBAH",
                      "O(1) amortized: array hanya sesekali menyalin ke petak "
                      "baru saat kapasitas penuh." if arr else
                      "O(1): penunjuk tail disimpan, jadi tidak perlu menelusuri."))
        m.append(Menu(g1, f"{kode} - TAMBAH PESANAN PRIORITAS", "m1_tambah",
                      (struktur, "prioritas"),
                      f"{nm}: pesanan PRIORITAS, menyerobot ke tengah",
                      "Pesanan prioritas disisipkan di tengah barisan (n // 2).",
                      [nama], "TAMBAH",
                      "O(n): array menggeser separuh isinya ke kanan." if arr else
                      "O(n): linked list menelusuri separuh simpul lalu "
                      "menyambung. Hampir seimbang dengan array, tapi sebabnya berbeda."))
        m.append(Menu(g1, f"{kode} - TAMBAH PESANAN VIP", "m1_tambah",
                      (struktur, "vip"),
                      f"{nm}: pesanan VIP, langsung ke urutan pertama",
                      "Pesanan VIP disisipkan di indeks 0.",
                      [nama], "TAMBAH",
                      "O(n): array harus menggeser seluruh isinya satu petak." if arr
                      else "O(1): cukup mengubah penunjuk head. Inilah kekuatan linked list."))
        m.append(Menu(g1, f"{kode} - HAPUS PESANAN", "m1_hapus", (struktur,),
                      f"{nm}: hapus pesanan ke-i",
                      "Mencabut satu pesanan dari barisan.",
                      [idx], "HAPUS",
                      "O(n): sisa isi digeser satu petak ke kiri." if arr else
                      "O(n): menelusuri sampai simpul sebelum target lalu memutus sambungan."))

    m.append(Menu(g2, "STACK - POSTFIX (MESIN KASIR)", "postfix", (),
                  "Stack: hitung struk lewat postfix",
                  "Struk ditulis infix, lalu dihitung dua tahap dengan stack: "
                  "tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi.",
                  [Isian("Struk belanja (infix)",
                         "( 3 * 12000 ) + ( 2 * 8500 ) - 5000",
                         petunjuk="angka, + - * / dan tanda kurung; "
                                   "3 x Rp12.000 dan 2 x Rp8.500, potongan Rp5.000")],
                  "HITUNG",
                  "Baris 1.x adalah konversi, baris 2.x evaluasi. Tahap 1 menahan "
                  "operator di stack sampai gilirannya tiba. Tahap 2 menumpuk "
                  "angka, dan setiap operator mengambil dua nilai teratas. "
                  "Operand kanan selalu keluar lebih dulu."))
    m.append(Menu(g2, "STACK - UNDO", "undo", (),
                  "Stack: batalkan aksi antrean terakhir",
                  "Mengambil catatan teratas tumpukan undo, lalu menjalankan "
                  "kebalikannya. Aksi terakhirlah yang dibatalkan lebih dulu.",
                  [], "UNDO",
                  "Kebalikan dari enqueue membuang elemen paling belakang (murah). "
                  "Kebalikan dari dequeue mengembalikan seluruh daftar pesanan "
                  "ke DEPAN antrean, bukan ke belakang."))
    m.append(Menu(g2, "STACK - REDO", "redo", (),
                  "Stack: kerjakan lagi aksi yang dibatalkan",
                  "Mengambil catatan teratas tumpukan redo, lalu mengerjakan "
                  "ulang aksi aslinya. Aksi baru mengosongkan tumpukan ini.",
                  [], "REDO",
                  "Redo mengerjakan ULANG aksi aslinya, bukan kebalikannya, lalu "
                  "mengembalikan catatannya ke tumpukan undo supaya bisa dibatalkan lagi."))
    m.append(Menu(g2, "QUEUE - ENQUEUE", "queue_enqueue", (),
                  "Queue: pesanan baru masuk ke belakang",
                  "Menambahkan pesanan di ujung belakang kedua antrean sekaligus, "
                  "yang naif maupun yang circular.",
                  [nama], "ENQUEUE",
                  "Enqueue selalu menempel di belakang, jadi O(1) pada kedua versi. "
                  "Perbedaannya baru muncul saat dequeue."))
    jumlah = Isian("Berapa kali dequeue", "1",
                   petunjuk="coba 1, lalu 10, lalu 100 untuk melihat bedanya")
    m.append(Menu(g2, "QUEUE - DEQUEUE NAIF", "queue_dequeue", ("naif",),
                  "Queue naif: ambil dari depan dengan menggeser isi",
                  "Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak "
                  "ke kiri. Biayanya O(n) setiap kali.",
                  [jumlah], "DEQUEUE",
                  "Mengambil indeks 0 memaksa seluruh sisa isi bergeser satu petak "
                  "ke kiri, jadi O(n) per dequeue. Bandingkan waktunya dengan menu "
                  "DEQUEUE CIRCULAR."))
    m.append(Menu(g2, "QUEUE - DEQUEUE CIRCULAR", "queue_dequeue", ("circular",),
                  "Queue circular: ambil dari depan dengan memajukan penunjuk",
                  "Hanya penunjuk front yang maju, memakai sisa modulo terhadap "
                  "kapasitas. Isi larik tidak digeser sama sekali.",
                  [jumlah], "DEQUEUE",
                  "Yang berpindah hanya penunjuk front, tidak ada elemen yang "
                  "digeser, jadi O(1) berapa pun panjang antreannya."))

    kunci_sort = Isian("Diurutkan menurut", "harga", "combo",
                       ("oid", "harga", "selesai"),
                       "oid (teks), harga (angka), selesai (waktu selesai)")
    m.append(Menu(g3, "SORT - INSERTION SORT", "m3_sort", ("insertion",),
                  "Sort: insertion sort, O(n²)",
                  "Setiap elemen digeser mundur sampai menemukan tempatnya. "
                  "Sederhana, tetapi kerjanya tumbuh kuadratik.",
                  [Isian("Jumlah baris diurutkan", "1000",
                         petunjuk="diambil dari awal data; coba 1.000 lalu "
                                   "2.000 lalu 4.000"), kunci_sort],
                  "URUTKAN",
                  "Setiap elemen digeser mundur sampai menemukan tempatnya, jadi "
                  "biayanya tumbuh kuadratik: melipatduakan jumlah baris membuat "
                  "perbandingan naik sekitar empat kali. Batas 20.000 baris."))
    m.append(Menu(g3, "SORT - MERGE SORT", "m3_sort", ("merge",),
                  "Sort: merge sort, O(n log n)",
                  "Larik dibelah dua terus-menerus, lalu potongan yang sudah "
                  "terurut disatukan kembali.",
                  [Isian("Jumlah baris diurutkan", "4000",
                         petunjuk="coba juga 200.000 untuk seluruh data"),
                   Isian("Diurutkan menurut", "oid", "combo",
                         ("oid", "harga", "selesai"),
                         "oid (teks), harga (angka), selesai (waktu selesai)")],
                  "URUTKAN",
                  "Larik dibelah dua sampai tersisa satu elemen, lalu digabung "
                  "kembali. Kedalaman belahannya log n dan tiap tingkat memakai O(n), "
                  "jadi O(n log n). Hasilnya sama persis dengan insertion sort karena "
                  "keduanya stabil."))
    cari = Isian("Nomor pesanan (oid)", "O-137442",
                 petunjuk="format O-000001 sampai O-200000")
    m.append(Menu(g3, "SEARCH - LINEAR SEARCH", "m3_linear", (),
                  "Search: linear search, O(n)",
                  "Memeriksa pesanan satu per satu dari depan. Tidak menuntut "
                  "data terurut.",
                  [cari], "CARI",
                  "Data tidak perlu terurut, tetapi setiap pesanan diperiksa satu "
                  "per satu dari depan. Kasus terburuk menyentuh seluruh 200.000 baris."))
    m.append(Menu(g3, "SEARCH - BINARY SEARCH", "m3_binary", (),
                  "Search: binary search, O(log n)",
                  "Membuang separuh daftar pada setiap perbandingan. Menuntut "
                  "daftar yang sudah terurut menurut oid.",
                  [cari], "CARI",
                  "Setiap perbandingan membuang separuh daftar, jadi 200.001 baris "
                  "habis dalam paling banyak 18 langkah. Syaratnya daftar harus "
                  "SUDAH terurut menurut kunci yang dicari; di sini terurut menurut oid."))
    return m


# ======================================================================
# Jendela Tkinter (tema ungu)
# Hanya urusan tampilan. Logikanya ada di Kontroler di atas.
# ======================================================================
UNGU = "#8b4aa8"          # ungu sedang (warna badan): tombol dan aksen utama
UNGU_TUA = "#2a2561"      # biru malam (warna surai): teks judul tabel, header
UNGU_HOVER = "#763a92"
PINK = "#d9418c"          # magenta (garis surai): aksen kecil
LILAC = "#c9a7e0"         # lavender muda: scrollbar, hiasan
LAVENDER = "#f7f1fb"      # latar jendela
PANEL = "#ecdff6"         # latar menu kiri dan bar bawah
GARIS = "#dac6ec"
KARTU = "#ffffff"
HOVER_MENU = "#f4eafa"
TEKS = "#241f5a"
TEKS_REDUP = "#7a6a95"
CATATAN_BG = "#fce8f2"
GALAT = "#b91c1c"
KONSOL_BG = "#1f1b4a"
KONSOL_FG = "#f6d6ea"

FONT = ("Segoe UI", 10)
FONT_TEBAL = ("Segoe UI", 10, "bold")
FONT_JUDUL = ("Segoe UI", 16, "bold")
FONT_KECIL = ("Segoe UI", 9)
FONT_GRUP = ("Segoe UI", 8, "bold")
FONT_MONO = ("Consolas", 10)


def campur(c1, c2, t):
    """Warna di antara c1 dan c2 (t = 0..1), untuk gradasi."""
    a = (int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16))
    b = (int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16))
    r = int(a[0] + (b[0] - a[0]) * t)
    g = int(a[1] + (b[1] - a[1]) * t)
    bl = int(a[2] + (b[2] - a[2]) * t)
    return "#%02x%02x%02x" % (r, g, bl)


def gradasi(t):
    """Biru malam -> ungu -> magenta untuk header."""
    if t < 0.55:
        return campur(UNGU_TUA, UNGU, t / 0.55)
    return campur(UNGU, PINK, (t - 0.55) / 0.45)


def kotak_bulat(kanvas, x1, y1, x2, y2, r, warna):
    """Persegi panjang bersudut membulat di Canvas."""
    titik = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
             x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
             x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return kanvas.create_polygon(titik, smooth=True, fill=warna, outline=warna)


class TombolBulat(tk.Canvas):
    """Tombol dengan sudut membulat dan efek sorot. Dipakai untuk menu dan aksi."""
    def __init__(self, induk, teks, perintah, latar, warna, warna_sorot,
                 warna_teks, font, tinggi=34, rata="center", lebar=None,
                 radius=12):
        tk.Canvas.__init__(self, induk, height=tinggi, bg=latar, bd=0,
                           highlightthickness=0, cursor="hand2")
        if lebar is not None:
            self.configure(width=lebar)
        self.teks = teks
        self.perintah = perintah
        self.warna = warna
        self.warna_sorot = warna_sorot
        self.warna_teks = warna_teks
        self.warna_teks_aktif = "white"
        self.font = font
        self.rata = rata
        self.radius = radius
        self.aktif = False
        self.di_atas = False
        self.bind("<Configure>", lambda e: self._gambar())
        self.bind("<Enter>", self._masuk)
        self.bind("<Leave>", self._keluar)
        self.bind("<ButtonRelease-1>", self._klik)

    def _gambar(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10:
            return
        if self.aktif:
            isi = UNGU
            tulisan = self.warna_teks_aktif
        elif self.di_atas:
            isi = self.warna_sorot
            tulisan = self.warna_teks
        else:
            isi = self.warna
            tulisan = self.warna_teks
        kotak_bulat(self, 1, 1, w - 1, h - 1, self.radius, isi)
        if self.rata == "w":
            self.create_text(14, h // 2, text=self.teks, fill=tulisan,
                             font=self.font, anchor="w")
        else:
            self.create_text(w // 2, h // 2, text=self.teks, fill=tulisan,
                             font=self.font)

    def set_aktif(self, nilai):
        self.aktif = nilai
        self._gambar()

    def _masuk(self, _):
        self.di_atas = True
        self._gambar()

    def _keluar(self, _):
        self.di_atas = False
        self._gambar()

    def _klik(self, event):
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.perintah()


class AplikasiUI:
    def __init__(self, root, kontroler):
        self.root = root
        self.k = kontroler
        self.menu = daftar_menu()
        self.tombol_menu = []
        self.menu_aktif = None
        self.vars = []
        self.entri_pertama = None
        self.baris_ke = 0

        root.title("2EZ4U Food Delivery")
        root.configure(bg=LAVENDER)
        lebar = min(1280, int(root.winfo_screenwidth() * 0.86))
        tinggi = min(820, int(root.winfo_screenheight() * 0.86))
        kiri = (root.winfo_screenwidth() - lebar) // 2
        atas = max(0, (root.winfo_screenheight() - tinggi) // 3)
        root.geometry(f"{lebar}x{tinggi}+{kiri}+{atas}")
        root.minsize(960, 640)
        self._atur_gaya()

        self._bangun_header()
        self._bangun_bawah()
        self._bangun_badan()
        self._bangun_menu_kiri()
        self.pilih(self.menu[0])

    # ---- gaya ttk (tabel, scrollbar, combobox) ----
    def _atur_gaya(self):
        gaya = ttk.Style()
        try:
            gaya.theme_use("clam")
        except tk.TclError:
            pass
        gaya.configure("Treeview", rowheight=26, font=FONT_MONO,
                       background=KARTU, fieldbackground=KARTU,
                       foreground=TEKS, borderwidth=0)
        gaya.configure("Treeview.Heading", font=FONT_TEBAL, background=PANEL,
                       foreground=UNGU_TUA, relief="flat", padding=(8, 6),
                       borderwidth=0)
        gaya.map("Treeview", background=[("selected", "#e6cff3")],
                 foreground=[("selected", TEKS)])
        gaya.map("Treeview.Heading", background=[("active", GARIS)])
        for arah in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
            gaya.configure(arah, background=LILAC, troughcolor=LAVENDER,
                           bordercolor=LAVENDER, lightcolor=LILAC,
                           darkcolor=LILAC, arrowcolor=UNGU, relief="flat",
                           arrowsize=14)
            gaya.map(arah, background=[("active", "#b27ad0")])
        gaya.configure("TCombobox", fieldbackground=KARTU, background=PANEL,
                       foreground=TEKS, arrowcolor=UNGU, bordercolor=GARIS,
                       lightcolor=KARTU, darkcolor=KARTU, padding=5)
        gaya.map("TCombobox", fieldbackground=[("readonly", KARTU)],
                 foreground=[("readonly", TEKS)])
        self.root.option_add("*TCombobox*Listbox.background", KARTU)
        self.root.option_add("*TCombobox*Listbox.foreground", TEKS)
        self.root.option_add("*TCombobox*Listbox.selectBackground", UNGU)
        self.root.option_add("*TCombobox*Listbox.font", FONT)

    # ---- kerangka ----
    def _bangun_header(self):
        self.header = tk.Canvas(self.root, height=72, bd=0, highlightthickness=0)
        self.header.pack(side="top", fill="x")
        self.header.bind("<Configure>", self._gambar_header)

    def _gambar_header(self, event):
        c = self.header
        c.delete("all")
        w = event.width
        langkah = 4
        for x in range(0, w, langkah):
            c.create_rectangle(x, 0, x + langkah, 72, outline="",
                               fill=gradasi(x / max(w, 1)))
        # gelembung hiasan di kanan
        c.create_oval(w - 150, -40, w - 30, 80, outline="", fill="#e0679f")
        c.create_oval(w - 90, 20, w + 10, 120, outline="", fill="#f08cba")
        c.create_oval(w - 230, 30, w - 170, 90, outline="", fill="#b7569f")
        c.create_text(26, 28, text="2EZ4U Food Delivery", fill="white",
                      font=("Segoe UI", 18, "bold"), anchor="w")
        c.create_text(28, 54, text="mini engine pesanan  -  array, antrean, sort, search",
                      fill="#f3d9f0", font=FONT_KECIL, anchor="w")

    def _bangun_bawah(self):
        b = tk.Frame(self.root, bg=PANEL)
        b.pack(side="bottom", fill="x")
        TombolBulat(b, "Tutup", self.root.destroy, PANEL, UNGU, UNGU_HOVER,
                    "white", FONT_TEBAL, tinggi=32, lebar=96).pack(
            side="left", padx=(14, 10), pady=8)
        self.status = tk.StringVar(value="Siap. Klik Load untuk memuat data.")
        tk.Label(b, textvariable=self.status, bg=PANEL, fg=UNGU_TUA,
                 font=FONT_MONO, anchor="w").pack(side="left", pady=8)

    def _bangun_badan(self):
        self.badan = tk.Frame(self.root, bg=LAVENDER)
        self.badan.pack(side="top", fill="both", expand=True)
        self.kiri = tk.Frame(self.badan, bg=PANEL, width=372)
        self.kiri.pack(side="left", fill="y")
        self.kiri.pack_propagate(False)
        self.kanan = tk.Frame(self.badan, bg=LAVENDER, padx=20, pady=12)
        self.kanan.pack(side="left", fill="both", expand=True)

        self.judul = tk.Label(self.kanan, text="", font=FONT_JUDUL, fg=TEKS,
                              bg=LAVENDER, anchor="w", justify="left")
        self.judul.pack(fill="x")
        self.sub = tk.Label(self.kanan, text="", font=FONT_KECIL,
                            fg=TEKS_REDUP, bg=LAVENDER, anchor="w",
                            justify="left")
        self.sub.pack(fill="x", pady=(2, 8))

        # kartu form
        self.form = tk.Frame(self.kanan, bg=KARTU, highlightthickness=1,
                             highlightbackground=GARIS, padx=16, pady=12)
        self.form.pack(fill="x")

        self.ringkas = tk.Label(self.kanan, text="", font=FONT, fg=TEKS,
                                bg=LAVENDER, anchor="w", justify="left")
        self.ringkas.pack(fill="x", pady=(10, 6))

        # catatan dan COMMAND dipasang dari bawah lebih dulu supaya tidak terpotong
        kn = tk.Frame(self.kanan, bg=CATATAN_BG)
        kn.pack(side="bottom", fill="x", pady=(10, 0))
        tk.Frame(kn, bg=PINK, width=5).pack(side="left", fill="y")
        self.catatan = tk.Label(kn, text="", font=FONT_KECIL, fg=TEKS,
                                bg=CATATAN_BG, anchor="w", justify="left",
                                padx=12, pady=8)
        self.catatan.pack(side="left", fill="x", expand=True)

        kc = tk.Frame(self.kanan, bg=KONSOL_BG)
        kc.pack(side="bottom", fill="x")
        tk.Label(self.kanan, text="COMMAND", font=FONT_GRUP, fg=UNGU,
                 bg=LAVENDER, anchor="w").pack(side="bottom", fill="x",
                                               pady=(10, 3))
        self.cmd = tk.Text(kc, height=4, font=FONT_MONO, state="disabled",
                           bg=KONSOL_BG, fg=KONSOL_FG, wrap="none", bd=0,
                           highlightthickness=0, padx=12, pady=8,
                           insertbackground=KONSOL_FG, selectbackground=UNGU)
        sc = ttk.Scrollbar(kc, orient="vertical", command=self.cmd.yview)
        self.cmd.configure(yscrollcommand=sc.set)
        self.cmd.pack(side="left", fill="x", expand=True)
        sc.pack(side="right", fill="y")

        # kartu tabel mengisi sisa ruang di tengah
        kt = tk.Frame(self.kanan, bg=KARTU, highlightthickness=1,
                      highlightbackground=GARIS)
        kt.pack(fill="both", expand=True)
        self.tabel = ttk.Treeview(kt, show="headings", height=4)
        self.tabel.tag_configure("genap", background="#fbf6fd")
        sy = ttk.Scrollbar(kt, orient="vertical", command=self.tabel.yview)
        sx = ttk.Scrollbar(kt, orient="horizontal", command=self.tabel.xview)
        self.tabel.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabel.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        kt.grid_rowconfigure(0, weight=1)
        kt.grid_columnconfigure(0, weight=1)
        self.kanan.bind("<Configure>", self._atur_lebar)

    def _atur_lebar(self, event):
        lebar = max(300, event.width - 80)
        self.sub.configure(wraplength=lebar)
        self.ringkas.configure(wraplength=lebar)
        self.catatan.configure(wraplength=lebar)

    def _bangun_menu_kiri(self):
        kanvas = tk.Canvas(self.kiri, bg=PANEL, highlightthickness=0)
        sb = ttk.Scrollbar(self.kiri, orient="vertical", command=kanvas.yview)
        kanvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        kanvas.pack(side="left", fill="both", expand=True)
        dalam = tk.Frame(kanvas, bg=PANEL)
        jendela = kanvas.create_window((0, 0), window=dalam, anchor="nw")
        dalam.bind("<Configure>",
                   lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.bind("<Configure>",
                    lambda e: kanvas.itemconfigure(jendela, width=e.width))

        def roda(event):
            if event.num == 4:
                kanvas.yview_scroll(-1, "units")
            elif event.num == 5:
                kanvas.yview_scroll(1, "units")
            else:
                kanvas.yview_scroll(int(-event.delta / 120), "units")

        def masuk(_):
            kanvas.bind_all("<MouseWheel>", roda)
            kanvas.bind_all("<Button-4>", roda)
            kanvas.bind_all("<Button-5>", roda)

        def keluar(_):
            kanvas.unbind_all("<MouseWheel>")
            kanvas.unbind_all("<Button-4>")
            kanvas.unbind_all("<Button-5>")

        self.kiri.bind("<Enter>", masuk)
        self.kiri.bind("<Leave>", keluar)

        grup_terakhir = ""
        for menu in self.menu:
            if menu.grup != grup_terakhir:
                tk.Label(dalam, text=menu.grup, bg=PANEL, fg=UNGU,
                         font=FONT_GRUP, anchor="w").pack(
                    fill="x", padx=16, pady=(14, 4))
                grup_terakhir = menu.grup
            tombol = TombolBulat(dalam, menu.label,
                                 lambda m=menu: self.pilih(m), PANEL, KARTU,
                                 HOVER_MENU, TEKS, FONT, tinggi=34, rata="w")
            tombol.pack(fill="x", padx=12, pady=2)
            self.tombol_menu.append((menu, tombol))
        tk.Frame(dalam, bg=PANEL, height=12).pack()

    # pilih menu & form
    def pilih(self, menu):
        self.menu_aktif = menu
        for m, tombol in self.tombol_menu:
            tombol.set_aktif(m is menu)
        self.judul.configure(text=menu.judul)
        self.sub.configure(text=menu.sub)
        self.catatan.configure(text=menu.catatan)
        self._bangun_form(menu)
        self._bersihkan_hasil()

    def _bangun_form(self, menu):
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = []
        self.entri_pertama = None
        kolom = 0
        for isian in menu.isian:
            tk.Label(self.form, text=isian.label, font=FONT_TEBAL, fg=TEKS,
                     bg=KARTU, anchor="w").grid(row=0, column=kolom,
                                                sticky="w", padx=(0, 16))
            v = tk.StringVar(value=isian.awal)
            if isian.tipe == "combo":
                w = ttk.Combobox(self.form, textvariable=v, state="readonly",
                                 values=isian.opsi, width=14, font=FONT)
            else:
                lebar = 46 if len(isian.awal) > 20 else 22
                w = tk.Entry(self.form, textvariable=v, width=lebar, font=FONT,
                             fg=TEKS, bg=KARTU, relief="flat",
                             highlightthickness=2, highlightbackground=GARIS,
                             highlightcolor=UNGU, insertbackground=UNGU,
                             selectbackground="#e6cff3", selectforeground=TEKS)
                w.bind("<Return>", lambda e: self.jalankan())
                if self.entri_pertama is None:
                    self.entri_pertama = w
            w.grid(row=1, column=kolom, sticky="w", padx=(0, 16), pady=(4, 0),
                   ipady=4)
            if isian.petunjuk != "":
                tk.Label(self.form, text=isian.petunjuk, font=FONT_KECIL,
                         fg=TEKS_REDUP, bg=KARTU, anchor="w", justify="left",
                         wraplength=250).grid(row=2, column=kolom, sticky="w",
                                              padx=(0, 16), pady=(4, 0))
            self.vars.append(v)
            kolom += 1
        lebar_tombol = len(menu.tombol) * 11 + 52
        TombolBulat(self.form, menu.tombol, self.jalankan, KARTU, UNGU,
                    UNGU_HOVER, "white", FONT_TEBAL, tinggi=36,
                    lebar=lebar_tombol, radius=14).grid(
            row=1, column=kolom, sticky="w", pady=(4, 0))
        if self.entri_pertama is not None:
            self.entri_pertama.focus_set()

    # menjalankan
    def jalankan(self):
        menu = self.menu_aktif
        nilai = []
        for v in self.vars:
            nilai.append(v.get())
        self.status.set("memproses...")
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            hasil = getattr(self.k, menu.aksi)(*menu.tetap, *nilai)
        except ValueError as galat:
            self._tampilkan_galat(str(galat))
            return
        except Exception as galat:     # galat tak terduga: tampilkan, jangan crash
            self._tampilkan_galat(f"Galat: {galat}")
            return
        finally:
            self.root.configure(cursor="")
        self._tampilkan(hasil)

    def _bersihkan_hasil(self):
        self.ringkas.configure(text="", fg=TEKS)
        self.tabel.delete(*self.tabel.get_children())
        self.baris_ke = 0

    def _tampilkan_galat(self, pesan):
        self._bersihkan_hasil()
        self.ringkas.configure(text=pesan, fg=GALAT)
        self.status.set("Ditolak.")

    def _tampilkan(self, hasil):
        self._bersihkan_hasil()
        self.ringkas.configure(text="\n".join(hasil.ringkas), fg=TEKS)
        self._isi_tabel(hasil.kolom, hasil.baris)
        self.status.set(f"[{hasil.modul}]  {fmt_ms(hasil.ms)} ms")
        self._catat(hasil)

    def _isi_tabel(self, kolom, baris):
        self.tabel.configure(columns=kolom)
        n = len(kolom)
        for i in range(n):
            lebar = len(kolom[i])
            for r in range(min(len(baris), BATAS_TAMPIL)):
                panjang = len(str(baris[r][i]))
                if panjang > lebar:
                    lebar = panjang
            px = min(max(lebar * 9 + 28, 80), 440)
            self.tabel.heading(kolom[i], text=kolom[i], anchor="w")
            self.tabel.column(kolom[i], width=px, minwidth=50,
                              stretch=(i == n - 1), anchor="w")
        for r in baris:
            if self.baris_ke % 2 == 1:
                self.tabel.insert("", "end", values=r, tags=("genap",))
            else:
                self.tabel.insert("", "end", values=r)
            self.baris_ke += 1

    def _catat(self, hasil):
        teks = (f"{hasil.perintah:<24}-> {hasil.modul:<22}"
                f"{fmt_ms(hasil.ms):>10} ms\n")
        self.cmd.configure(state="normal")
        self.cmd.insert("1.0", teks)
        self.cmd.configure(state="disabled")


def main():
    if tk is None:
        print("Tkinter tidak ditemukan. Pasang Python dengan komponen Tcl/Tk "
              "(Windows: centang 'tcl/tk and IDLE' saat instalasi).")
        return
    try:                                   # tampilan tajam di layar beresolusi tinggi
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    AplikasiUI(root, Kontroler())
    root.mainloop()


if __name__ == "__main__":
    main()