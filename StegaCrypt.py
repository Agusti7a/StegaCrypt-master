#!/usr/bin/env python
import sys
import os, random
import struct
import numpy
import matplotlib.pyplot as plt
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

from PIL import Image


#menghapus history bash yang tampil sebelumnya
clear = lambda : os.system('tput reset')
clear()

#Define Colors
class bcolors:
    ENDC = '\033[0m'
    BOLD = '\033[1m'

#Menampilkan Lambang Selamat Datang
print bcolors.BOLD + """
      ______
     / ____/_____________________   ____________  _____________  ______  __
    / /_____  ___/ ____/ ____/   | / ____/ __ \ \/ / __ \_  __/ / __ \ \/ /
   /___  / / /  / __/ / / __/ /| |/ /   / /_/ /\  / /_/ // /   / /_/ /\  /
  ____/ / / /  / /___/ /_/ / ___ / /___/ _, _/ / / ____// /   / ____/ / /
 /_____/ /_/  /_____/\____/_/  |_\____/_/ |_| /_/_/    /_/ (_)_/     /_/
 (c) Agusti Gunawan 2016
\n """ + bcolors.ENDC

def clear():
	clear = lambda : os.system('tput reset')
	clear()

# Cryptography file
def encrypt(key, filename):
	chunksize = 64*1024
	outputFile = "(encrypted)"+filename
	filesize = str(os.path.getsize(filename)).zfill(16)
	IV = ''

	for i in range(16):
		IV += chr(random.randint(0, 0xFF))

	encryptor = AES.new(key, AES.MODE_CBC, IV)

	with open(filename, 'rb') as infile:
		with open(outputFile, 'wb') as outfile:
			outfile.write(filesize)
			outfile.write(IV)

			while True:
				chunk =  infile.read(chunksize)

				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - (len(chunk) % 16))

				outfile.write(encryptor.encrypt(chunk))

	print "[+] Data anda Berhasi di Encrypsi!"

def decrypt(key, filename):
	chunksize = 64*1024
	outputFile = "(decrypted)"+filename

	with open(filename, 'rb') as infile:
		filesize = long(infile.read(16))
		IV = infile.read(16)

		decryptor = AES.new(key, AES.MODE_CBC, IV)

		with open (outputFile, 'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)

				if len(chunk) == 0:
					break

				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(filesize)


	print "[+] Data anda berhasil di Decrypsi!"

def getKey(password):
	hasher = SHA256.new(password)
	return hasher.digest()

# Crypt for Stega
class AESCipher:

    def __init__(self, key): 
        self.bs = 32						# Ukuran Block
        self.key = hashlib.sha256(key.encode()).digest()	# 32 bit digest

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

# Decompose a binary file into an array of bits
def decompose(data):
	v = []

	# Pack file len in 4 bytes
	fSize = len(data)
	bytes = [ord(b) for b in struct.pack("i", fSize)]

	bytes += [ord(b) for b in data]

	for b in bytes:
		for i in range(7, -1, -1):
			v.append((b >> i) & 0x1)

	return v

# Assemble an array of bits into a binary file
def assemble(v):
	bytes = ""

	length = len(v)
	for idx in range(0, len(v)/8):
		byte = 0
		for i in range(0, 8):
			if (idx*8+i < length):
				byte = (byte<<1) + v[idx*8+i]
		bytes = bytes + chr(byte)

	payload_size = struct.unpack("i", bytes[:4])[0]

	return bytes[4: payload_size + 4]

# Set the i-th bit of v to x
def set_bit(n, i, x):
	mask = 1 << i
	n &= ~mask
	if x:
		n |= mask
	return n

# Embed payload file into LSB bits of an image
def embed(imgFile, payload, password):
	# Process source image
	img = Image.open(imgFile)
	(width, height) = img.size
	conv = img.convert("RGBA").getdata()
	print "[*] Input image size: %dx%d pixels." % (width, height)
	max_size = width*height*3.0/8/1024		# max payload size
	print "[*] Usable payload size: %.2f KB." % (max_size)

	f = open(payload, "rb")
	data = f.read()
	f.close()
	print "[+] Payload size: %.3f KB " % (len(data)/1024.0)

	# Encypt
	cipher = AESCipher(password)
	data_enc = cipher.encrypt(data)

	# Process data from payload file
	v = decompose(data_enc)

	# Add until multiple of 3
	while(len(v)%3):
		v.append(0)

	payload_size = len(v)/8/1024.0
	print "[+] Encrypted payload size: %.3f KB " % (payload_size)
	if (payload_size > max_size - 4):
		print "[-] Cannot embed. File too large"
		sys.exit()

	# Create output image
	steg_img = Image.new('RGBA',(width, height))
	data_img = steg_img.getdata()

	idx = 0

	for h in range(height):
		for w in range(width):
			(r, g, b, a) = conv.getpixel((w, h))
			if idx < len(v):
				r = set_bit(r, 0, v[idx])
				g = set_bit(g, 0, v[idx+1])
				b = set_bit(b, 0, v[idx+2])
			data_img.putpixel((w,h), (r, g, b, a))
			idx = idx + 3

	steg_img.save(imgFile + "-stego.png", "PNG")

	print "[+] %s embedded successfully!" % payload

# Extract data embedded into LSB of the input file
def extract(in_file, out_file, password):
	# Process source image
	img = Image.open(in_file)
	(width, height) = img.size
	conv = img.convert("RGBA").getdata()
	print "[+] Image size: %dx%d pixels." % (width, height)

	# Extract LSBs
	v = []
	for h in range(height):
		for w in range(width):
			(r, g, b, a) = conv.getpixel((w, h))
			v.append(r & 1)
			v.append(g & 1)
			v.append(b & 1)

	data_out = assemble(v)

	# Decrypt
	cipher = AESCipher(password)
	data_dec = cipher.decrypt(data_out)

	# Write decrypted data
	out_f = open(out_file, "wb")
	out_f.write(data_dec)
	out_f.close()

	print "[+] Written extracted data to %s." % out_file


#Untuk Crypto+Stegano
#EncryptStega
def encryptstega(key, filename):
	chunksize = 64*1024
	outputFile = "(encrypted)"+filename
	var_file1 = outputFile
	filesize = str(os.path.getsize(filename)).zfill(16)
	IV = ''

	for i in range(16):
		IV += chr(random.randint(0, 0xFF))

	encryptor = AES.new(key, AES.MODE_CBC, IV)

	with open(filename, 'rb') as infile:
		with open(outputFile, 'wb') as outfile:
			outfile.write(filesize)
			outfile.write(IV)

			while True:
				chunk =  infile.read(chunksize)

				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - (len(chunk) % 16))

				outfile.write(encryptor.encrypt(chunk))

	print "[+] Data anda Berhasil di Encrypsi!"
	lanjut = raw_input("Apakah anda ingin melanjutkan ke tahap Steganography? y/n: ")

	if lanjut == 'y':
		imgFile = raw_input("Masukkan Gambar untuk Menyembunyikan Data: ")
		payload = var_file1
		password = raw_input("Masukkan Password: ")
		embed(imgFile, payload, password)
	elif lanjut == 'n':
		print "Program Dihentikan. Keluar....."
		sys.exit
	else:
		print "Anda Tidak Memilih Apapun. Keluar....."
		sys.exit

#DecryptStega
def extractdecrypt(in_file, out_file, password):
	# Process source image
	img = Image.open(in_file)
	(width, height) = img.size
	conv = img.convert("RGBA").getdata()
	print "[+] Image size: %dx%d pixels." % (width, height)

	# Extract LSBs
	v = []
	for h in range(height):
		for w in range(width):
			(r, g, b, a) = conv.getpixel((w, h))
			v.append(r & 1)
			v.append(g & 1)
			v.append(b & 1)

	data_out = assemble(v)

	# Decrypt
	cipher = AESCipher(password)
	data_dec = cipher.decrypt(data_out)

	# Write decrypted data
	out_f = open(out_file, "wb")
	out_f.write(data_dec)
	out_f.close()
	var_file2 = out_file

	print "[+] Written extracted data to %s." % out_file

	lanjut = raw_input("Apakah anda ingin melanjutkan ke tahap Decrypsi? y/n: ")
	if lanjut == 'y':
		filename = var_file2
		password = raw_input("Masukkan Password: ")
		decrypt(getKey(password), filename)
	elif lanjut == 'n':
		print "Program Dihentikan. Keluar....."
		sys.exit
	else:
		print "Anda Tidak Memilih Apapun. Keluar....."
		sys.exit

def about():
	print "Nama	: Agusti Gunawan"
	print "Alamat	: Alue Bilie Rayeuk, Baktiya, Aceh Utara"
	print "\n \n"
	print "9. Kembali"
	print "0. Keluar"
	pilih = raw_input("Masukkan pilihan Anda: ")
	if pilih == '9':
		clear()
		main()
	elif pilih == '0':
		sys.exit
	else:
		print "masukan yang Anda berikan salah. Keluar...."
		sys.exit

def main():
	print "1. Sembunyikan Data"
	print "2. Keluarkan Data"
	print "3. Encrypsi Data"
	print "4. Decrypsi Data"
	print "5. Encrypsi dan Sembunyikan Data"
	print "6. Keluarkan dan Decrypsi Data"
	print "7. Tentang Pembuat Program"
	print "0. Keluar"
	print "\n"
	main = raw_input("Silahkan Pilih Menu Diatas: ")

	if main == '1':
		imgFile = raw_input("Masukkan Gambar untuk Menyembunyikan Data: ")
		payload = raw_input("Masukkan file rahasia: ")
		password = raw_input("Masukkan Password: ")
		embed(imgFile, payload, password)

	elif main == '2':
		in_file = raw_input("Masukkan Gambar yang akan di Exract: ")
		out_file = raw_input("Masukkan nama untuk file keluaran hasil Extraxt: ")
		password = raw_input("Password: ")
		extract(in_file, out_file, password)

	elif main == '3':
		filename = raw_input("Masukkan file untuk di Encrypsi: ")
		password = raw_input("Masukkan Password: ")
		encrypt(getKey(password), filename)

	elif main == '4':
		filename = raw_input("Masukkan file untuk di Decrypsi: ")
		password = raw_input("Masukkan Password: ")
		decrypt(getKey(password), filename)

	elif main == '5':
		filename = raw_input("Masukkan file untuk di Encrypsi: ")
		password = raw_input("Masukkan Password: ")
		encryptstega(getKey(password), filename)

	elif main == '6':
		in_file = raw_input("Masukkan Gambar yang akan di Exract: ")
		out_file = raw_input("Masukkan nama untuk file keluaran hasil Extraxt: ")
		password = raw_input("Masukkan Password: ")
		extractdecrypt(in_file, out_file, password)

	elif main == '7':
		about()

	elif main == '0':
		sys.exit

	else :
		print "Anda Tidak Memilih Apapun. Keluar....."
		sys.exit


if __name__ == "__main__":
	main()
