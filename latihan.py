angka = [5, 3, 2, 1, 4]

for nilai in angka:
    print(nilai)


def angka_terbesar(angka1, angka2):
    if angka1 > angka2:
        return angka1
    return angka2


print(angka_terbesar(8, 5))


class Kotak:
    def __init__(self, isi):
        self.isi = isi

    def tampilkan_isi(self):
        print(self.isi)

    def cek_kosong(self):
        if self.isi is None:
            print("Kotak kosong")
        else:
            print("Kotak tidak kosong")


kotak_buku = Kotak("buku")
kotak_bola = Kotak("bola")
kotak_kosong = Kotak(None)

kotak_buku.tampilkan_isi()
kotak_bola.tampilkan_isi()
kotak_kosong.cek_kosong()