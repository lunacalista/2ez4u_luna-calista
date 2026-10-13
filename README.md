# 2EZ4U: Sistem Pesanan Kafe

Aplikasi pengelola pesanan kafe yang dibangun tanpa `dict`, `set`, `sorted`, `.sort()`, `heapq`, `bisect`, maupun `collections`. Semua struktur data (array dinamis, linked list, stack, antrean, sort, search) ditulis sendiri di atas `list` Python sebagai larik primitif.

Data uji: `data/pesanan.csv` (200.000 baris pesanan).

## Struktur Repo

```
2ez4u/
├── backend/
│   ├── m1_pesanan.py     # M1: Array vs Linked List
│   ├── m2_antrean.py     # M2: Stack, Queue, Undo/Redo, Kasir postfix
│   └── m3_laporan.py     # M3: Sort dan Search
├── data/
│   └── pesanan.csv
├── frontend/
│   └── ui.py             # UI Tkinter (menu, form, panel COMMAND)
├── app.py                # titik masuk aplikasi
└── README.md
```

Setiap file `backend/m*.py` memuat logika milestone sekaligus benchmark-nya.

## Cara Menjalankan

Butuh Python 3.10 ke atas, tanpa library tambahan.

```
python backend/m1_pesanan.py data/pesanan.csv     # benchmark M1
python backend/m2_antrean.py data/pesanan.csv     # benchmark M2
python backend/m2_antrean.py demo                 # demo kasir dan undo/redo
python backend/m3_laporan.py data/pesanan.csv     # benchmark M3
```

Aplikasi (UI Tkinter), dari root repo:

```
python app.py
```

Klik **Load** lebih dulu untuk memuat `data/pesanan.csv`, lalu pilih menu di kiri. Setiap perintah dicatat di panel COMMAND beserta modul dan waktunya.

## M1: Data Pesanan (Array vs Linked List)

Pesanan disimpan di dua struktur sekaligus agar bisa dibandingkan:

- **Array dinamis**: kapasitas dilipatduakan saat penuh (append O(1) amortized), sisip/hapus menggeser elemen (O(n)).
- **Linked List** dengan penunjuk `head` dan `tail`: tambah di depan dan belakang O(1), sisip/hapus di tengah harus menelusuri (O(n)).

Aturan bisnis:

| Jenis | Posisi masuk |
|---|---|
| REGULER | paling belakang |
| PRIORITAS | tengah antrean (`size // 2`) |
| VIP | paling depan |

Hasil benchmark pada 200.000 baris (waktu dalam ms, rata-rata 5 kali):

| Operasi | Array | Linked List | Penyebab |
|---|---|---|---|
| Lihat tengah | 0,0028 | 2,0825 | Array langsung loncat ke indeks, Linked List menelusuri dari `head` |
| Tambah REGULER | 0,0026 | 0,0011 | Keduanya hanya menempel di belakang |
| Tambah PRIORITAS | 5,2754 | 2,0224 | Array menggeser separuh isi, Linked List menelusuri separuh lalu menyambung |
| Tambah VIP | 10,1792 | 0,0056 | Array menggeser seluruh isi, Linked List hanya mengubah satu penunjuk |
| Hapus tengah | 5,1531 | 1,8657 | Sama seperti PRIORITAS |

Memuat 200.000 baris: Array 46,26 ms, Linked List 105,46 ms.

## M2: Stack dan Queue

**Kasir (Stack).** Struk infix diubah ke postfix memakai stack operator, lalu dievaluasi memakai stack nilai (operand kanan di-pop lebih dulu). Contoh: `(3*12000)+(2*8500)-5000` menjadi `3 12000 * 2 8500 * + 5000 -` dengan total Rp 48.000. Ekspresi yang salah (kurung tidak berpasangan, pembagian nol, karakter asing) ditolak dengan pesan jelas.

**Antrean.** Dua versi memakai data yang sama:

- **Naif**: `dequeue` mengambil indeks 0 lalu menggeser seluruh sisa isi, O(n).
- **Melingkar**: `dequeue` hanya memajukan penunjuk `front`, O(1).

Keputusan desain antrean melingkar:
- Saat penuh, kapasitas **tumbuh 2x** (enqueue tidak pernah ditolak).
- Kosong atau penuh dibedakan dengan pencacah `count`, karena `front == rear` bisa berarti keduanya.

**Undo/Redo.** Dua stack. Yang dicatat untuk DEQUEUE adalah *daftar pesanannya*, bukan hitungannya, supaya bisa dikembalikan ke depan antrean dengan urutan asli. Aksi baru mengosongkan stack redo. Undo/redo DEQUEUE hanya menyentuh antrean melingkar; antrean naif ditandai "basi" dan disalin ulang saat dibutuhkan (di luar hitungan waktu undo).

Hasil benchmark pada 19.850 pesanan berstatus ANTRE:

| Dequeue n | Naif (ms) | Melingkar (ms) | Geseran naif | Geseran melingkar |
|---|---|---|---|---|
| 1 | 3,2359 | 0,0142 | 19.849 | 0 |
| 10 | 37,9523 | 0,0151 | 198.445 | 0 |
| 100 | 503,6577 | 0,0928 | 1.979.950 | 0 |
| 1000 | 2470,0280 | 0,4212 | 19.349.500 | 0 |

Enqueue 1 pesanan hampir sama di keduanya (naif 0,0037 ms, melingkar 0,0010 ms). Undo dequeue 100 pesanan: 0,0752 ms, redo: 0,0522 ms.

## M3: Sort dan Search

Setiap algoritma melaporkan **jumlah perbandingan** lewat objek `Pencacah`, bukan hanya waktu.

| Algoritma | Kompleksitas | Catatan |
|---|---|---|
| Insertion sort | O(n²) | Stabil (geser hanya bila `>`), di tempat; menolak data di atas 20.000 baris |
| Merge sort | O(n log n) | Stabil (`<=` saat menggabung), mengembalikan larik baru |
| Linear search | O(n) | Tidak butuh data terurut |
| Binary search | O(log n) | Butuh data terurut menurut kunci yang dicari |

Karena laporan harian terurut menurut waktu selesai, binary search atas `oid` memakai **daftar terpisah yang diurutkan menurut `oid`** (dibangun sekali dengan merge sort).

Sort menurut `harga`, perbandingan vs n:

| n | Insertion (cmp) | Insertion (ms) | Merge (cmp) | Merge (ms) |
|---|---|---|---|---|
| 1.000 | 233.802 | 30,33 | 8.650 | 2,12 |
| 2.000 | 962.430 | 121,78 | 19.240 | 4,53 |
| 4.000 | 3.831.520 | 556,78 | 42.355 | 9,81 |
| 8.000 | 15.058.881 | 2.702,60 | 92.616 | 37,90 |

Saat n digandakan, perbandingan insertion sort naik sekitar 4x (kuadratik), sedangkan merge sort sekitar 2x (n log n). Merge sort atas seluruh 200.000 baris: 3.226.139 perbandingan, 1.439,49 ms.

Search `oid` O-199999:

| Metode | Perbandingan | Waktu |
|---|---|---|
| Linear | 199.999 | 30,2430 ms |
| Binary | 17 | 0,0552 ms |

Ongkos sekali bayar membangun daftar terurut `oid`: 1.155,14 ms.

## Diagram

_(menyusul: diagram arsitektur dan alur data)_

## Screenshot dan Demo

_(isi dengan screenshot tiap menu dan tautan video demo)_

## Catatan Desain

- Tanpa `dict`/`set`: semua struktur dibangun dari `list` primitif, tuple, dan class biasa.
- Data pesanan memakai class `Pesanan` (bukan dict). Pembacaan CSV memakai `csv.reader` karena kolom `pelanggan` bisa mengandung koma di dalam tanda kutip.
- Pesanan tanpa waktu selesai diberi kunci sangat besar saat diurutkan, sehingga selalu berada di paling akhir.