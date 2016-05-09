      ______
     / ____/_____________________   ____________  _____________  ______  __
    / /_____  ___/ ____/ ____/   | / ____/ __ \ \/ / __ \_  __/ / __ \ \/ /
   /___  / / /  / __/ / / __/ /| |/ /   / /_/ /\  / /_/ // /   / /_/ /\  /
  ____/ / / /  / /___/ /_/ / ___ / /___/ _, _/ / / ____// /   / ____/ / /
 /_____/ /_/  /_____/\____/_/  |_\____/_/ |_| /_/_/    /_/ (_)_/     /_/
 (c) Agusti Gunawan 2016

=========================================================================
Sekilas tentang Script ini
-------------------------------------------------------------------------
Script sederhana untuk menggamankan file/data dengan metode Cryptography
dan Steganography. Script ini menggunakan Algoritma AES-256 untuk keperl-
uan Encrypsi. AES-256 merupakan kunci blok terkuat dari pada versi kunci 
AES lainnya seperti AES-128, AES-192.

Dalam fungsi Steganography disini menggunakan modul Matplotlib. Matplot-
lib merupakan sebuah perintah yang digunakan untuk mengolah gambar.


-------------------------------------------------------------------------
Persiapan sebelum menjalankan Script/Aplikasi
-------------------------------------------------------------------------
- Sistem Operasi berbasis GNU/Linux
- Python
- Python-Crypto
- Python-Matplotlib


-------------------------------------------------------------------------
Instalasi modul Python-Crypto & Python-Matplotlib
-------------------------------------------------------------------------
Debian / Ubuntu : 
	~$ sudo apt-get install python-crypto
	~$ sudo apt-get install python-matplotlib

Fedora / Redhat :
	~$ sudo yum install python-crypto
	~$ sudo yum install python-matplotlib


-------------------------------------------------------------------------
Menjalankan Aplikasi
-------------------------------------------------------------------------
1. Cek dahulu apakah file StegaCrypt.py sudah exutable atau belum. Jika 
   sudah, step 2 abaikan.
2. Ubah StegaCrypt.py supaya dengan cara ketik di terminal :
	~$ sudo chmod +x StegaCrypt.py
3. Execute aplikasi/script nya dengan mengetikkan diterminal :
	~$ python ./StegaCrypt.py , atau
	~$ ./StegaCrypt.py
4. Pilih Opsi yang tersedia di aplikasi tersebut.
=========================================================================