# Laporan Ujian Tengah Semester - Graf Sains Data

Nama: Angelica Rosa Yuniva  
NIM: 23031554209  
Prodi: S1 Sains Data - Universitas Negeri Surabaya

## Tugas Pendahuluan

### Persiapan dan Perkenalan Lingkungan

- Membuat virtual environment baru dengan nama `myenv` untuk mengisolasi dependensi proyek.
- Mengaktifkan virtual environment dan menginstal seluruh dependensi paket dari file `requirements.txt`.

### Mempelajari Penggunaan Driver Neo4j

- Mengatur kredensial dan koneksi driver Python ke database Neo4j menggunakan `GraphDatabase.driver`.
- Membuka sesi koneksi dan menjalankan pembuatan node `Person` serta relasi berarah `KNOWS` menggunakan fungsi `add_friend`.
- Menampilkan daftar relasi pertemanan menggunakan fungsi `print_friends` dengan query Cypher `MATCH`.

#### Pertanyaan Pendahuluan (Checkpoint)

- **Apa nama database yang digunakan pada tutorial ini?**

  Jawaban: Database default yang digunakan adalah `neo4j`.

- **Sebutkan akses lain (seperti sintaks DDL/DML Cypher) yang dapat digunakan mengakses database lain dalam 1 instance!**

  Jawaban: Mengakses database lain dapat dilakukan menggunakan klausa `USE <nama_database>` pada query Cypher atau menentukan parameter `database_="nama_database"` pada eksekusi driver Python API.

- **Apa jenis graf pertemanan yang telah dibuat di sini?**

  Jawaban: Jenis graf yang dibuat adalah Graf Berarah (Directed Graph) yang menghubungkan node berlabel `Person` melalui relasi berarah `KNOWS`.

### Impor Data RetailRocket ke Database Neo4j

- Mengunduh dataset e-commerce RetailRocket (`events.csv`).
- Menjalankan impor data secara bertahap (batch import) menggunakan query Cypher dengan perintah `UNWIND` dan `MERGE` untuk membuat node `Visitor`, `Item`, serta relasi `VIEWED`, `ADDED_TO_CART`, dan `BOUGHT`.

## Soal UTS

### Wrangling dan EDA

#### Filter Periode Waktu Interaksi

- Fold Training (P1): 08/05/2015 s.d. 27/07/2015 (Total: 1.710.737 baris)
- Fold Testing (P2): 28/07/2015 s.d. 17/08/2015 (Total: 385.955 baris)

#### Penyimpanan Dataset Hasil Filter

- Berkas disimpan dalam format `.csv` di folder `data/` dengan nama `events_p1.csv` dan `events_p2.csv`.

#### Komposisi Subgraph

- Query Cypher:

```cypher
MATCH (n)
RETURN labels(n) AS Label, count(n) AS Jumlah;

MATCH ()-[r]->()
RETURN type(r) AS Jenis_Relasi, count(r) AS Jumlah;
Hasil Komposisi Node dan Relasi pada Fold P1
- Jumlah Node Visitor: 870.768
- Jumlah Node Item: 191.284
- Jumlah Relasi VIEWED: 1.655.412
- Jumlah Relasi ADDED_TO_CART: 41.699
- Jumlah Relasi BOUGHT: 13.626
Vector Space Modelling (VSM) User
Karakteristik VSM User (Visitor x Item):
- Shape Matriks: 870.768 x 191.284
- Sparsity: 99,9992% dengan 1.328.023 elemen tidak nol
- Penggunaan Memori: 19,4 MB (menggunakan scipy.sparse.csr_matrix, jika dense memerlukan 1.332,5 GB)
Vector Space Modelling (VSM) Item
Karakteristik VSM Item (Item x Visitor):
- Shape Matriks: 191.284 x 870.768
- Sparsity: 99,9992%
- Rata-rata Elemen Tidak Nol per Vektor: 6,94 (vektor item lebih padat dibandingkan user yang rata-ratanya 1,53)
Analisis Proyeksi Graf
- Proyeksi Item-Item dipilih karena lebih efektif dan efisien.
- Analisis: Jumlah simpul berkurang dari 870.768 menjadi 191.284 (turun sekitar 20,7 kali lipat). Vektor item memiliki median 2 elemen tidak nol sehingga lebih kaya informasi dan lebih stabil terhadap pengguna baru.
Perhitungan Similarity
Query Cypher untuk mendapatkan 5 record dengan similarity tertinggi (Item acuan populer 5411):
MATCH (a:Item {itemId: 5411})-[s:SIMILAR_TO]->(b:Item)
RETURN
    a.itemId AS item_acuan,
    b.itemId AS item_mirip,
    s.score AS similarity
ORDER BY s.score DESC
LIMIT 5;
Top 5 Item Mirip dengan Item 5411
- Item 33030 (Similarity: 0,145366)
- Item 33956 (Similarity: 0,100019)
- Item 37807 (Similarity: 0,098314)
- Item 256242 (Similarity: 0,092615)
- Item 89143 (Similarity: 0,079983)
Penulisan Kembali Nilai Similarity
Nilai cosine similarity ditulis kembali ke graf Neo4j sebagai relasi SIMILAR_TO dengan total 134.072 relasi ditambahkan.

**Catatan:** Aku mempertahankan angka dan isi yang kamu berikan, termasuk jumlah node, relasi, sparsity, memori, dan hasil similarity. Perubahan hanya pada format Markdown, indentasi, serta penulisan query agar lebih mudah dibaca di VS Code dan GitHub.
#### Kondisi Graf Sebelum dan Sesudah Similarity

- Sebelum: Graf hanya terdiri dari simpul Visitor dan Item yang terhubung melalui relasi interaksi langsung (`VIEWED`, `ADDED_TO_CART`, `BOUGHT`).
- Sesudah: Graf memiliki relasi homogen baru `SIMILAR_TO` yang menghubungkan antar simpul Item.
### Analytics - Rekomendasi KNN

- Pemilihan target visitor dilakukan secara reproducible menggunakan `numpy.random.default_rng(42)` dari kandidat pengguna yang aktif di P1 dan P2. Target visitor yang terpilih adalah visitor 124912.
- Hasil 3 item yang diiklankan untuk k = 5 tetangga terdekat:
  - Item 387318 (Skor: 1,2822)
  - Item 181050 (Skor: 1,0296)
  - Item 179136 (Skor: 0,9077)

### Evaluasi Sistem Rekomendasi

- Hit@5: 0
- NDCG@5: 0,0000

#### Penjelasan Evaluasi

Item relevan visitor 124912 pada periode uji P2 (item 158962) hanya berinteraksi dengan 2 user di P1 dan tidak memenuhi ambang batas minimal pasangan item bersama, sehingga tidak memiliki relasi `SIMILAR_TO`. Hasil evaluasi ini mencerminkan keterbatasan metode KNN berbasis graf pada data long-tail yang sangat sparse.
