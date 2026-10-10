"""Benchmark M2: antrean naif vs melingkar, plus undo/redo.

Pakai:  python benchmark_m2.py [data/pesanan.csv]
Antrean diisi pesanan berstatus ANTRE dari CSV (seperti contoh di PDF).
Hasilnya bisa disalin ke tabel di README.
"""
import sys

from backend.m1_pesanan import baca_csv, ukur
from backend.m2_antrean import ManajerUndoRedo


def muat_antre(path):
    """Mengambil oid pesanan berstatus ANTRE (urutan file)."""
    semua = baca_csv(path)
    antre = []
    for i in range(len(semua)):
        p = semua.get(i)
        if p.status == "ANTRE":
            antre.append(p.oid)
    return antre


def manajer_baru(antre):
    """Manajer segar; kedua antrean diisi data yang persis sama."""
    m = ManajerUndoRedo()
    for oid in antre:
        m.naif.enqueue(oid)
        m.circular.enqueue(oid)
    return m


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/pesanan.csv"
    antre = muat_antre(path)
    print(f"Pesanan ANTRE dimuat: {len(antre)}\n")

    # --- enqueue: harus sama murahnya di kedua versi ---
    m = manajer_baru(antre)
    _, ms_n = ukur(m.naif.enqueue, "O-BARU")
    _, ms_c = ukur(m.circular.enqueue, "O-BARU")
    print("ENQUEUE (1 pesanan)")
    print(f"  naif {ms_n:.4f} ms | circular {ms_c:.4f} ms\n")

    # --- dequeue: di sinilah selisihnya muncul ---
    print(f"{'DEQUEUE n':<12}{'naif (ms)':>12}{'circular (ms)':>15}{'geseran naif':>16}{'geseran circ':>14}")
    print("-" * 69)
    for n in (1, 10, 100, 1000):
        m = manajer_baru(antre)
        _, ms_naif, ms_circ = m.dequeue(n)
        print(f"{n:<12}{ms_naif:>12.4f}{ms_circ:>15.4f}"
              f"{m.naif.total_geseran:>16}{m.circular.total_geseran:>14}")

    # --- undo / redo atas satu aksi DEQUEUE 100 ---
    m = manajer_baru(antre)
    m.dequeue(100)
    _, ms_undo = ukur(m.undo_last)
    _, ms_redo = ukur(m.redo_last)
    print(f"\nUNDO dequeue 100: {ms_undo:.4f} ms | REDO: {ms_redo:.4f} ms "
          "(hanya antrean circular)")
    _, ms_sinkron = ukur(m.sinkron_naif)
    print(f"Sinkron ulang antrean naif (bukan bagian undo): {ms_sinkron:.4f} ms")


if __name__ == "__main__":
    main()