import os
import base64
import json
import secrets
import subprocess
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import aead
from cryptography.hazmat.primitives import hashes, serialization

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.3gp'}

public_key_path = os.path.expanduser("~/.config/sys/.syspub")

# Muat public key
with open(public_key_path, "rb") as f:
    recipient_public_key = serialization.load_pem_public_key(f.read())

# Input folder
input_folder = input("Enter input folder: ")
output_folder = "cache_" + secrets.token_hex(4)
print(f"Output folder: {output_folder}")

# Buat output folder dan temp folder
os.makedirs(output_folder, exist_ok=True)
temp_folder = os.path.expanduser("~/voidcrypt_temp")
os.makedirs(temp_folder, exist_ok=True)

files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
total = len(files)

print(f"Found {total} files. Starting encryption...\n")

# Menyimpan peta nama file terenkripsi → ekstensi asli
manifest = {}
success = 0
failed = 0

for i, filename in enumerate(files, 1):
    input_path = os.path.join(input_folder, filename)
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext in VIDEO_EXTENSIONS:
            compressed_path = os.path.join(temp_folder, "compressed.mp4")
            print(f"[{i}/{total}] Compressing {filename}...")
            result = subprocess.run([
                "ffmpeg", "-i", input_path,
                "-vcodec", "libx264", "-crf", "28",
                "-y", compressed_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if result.returncode == 0 and os.path.exists(compressed_path):
                read_path = compressed_path
                ext = ".mp4"
            else:
                print(f"  Compression failed, encrypting original...")
                read_path = input_path
        else:
            read_path = input_path

        with open(read_path, "rb") as f:
            plain_data = f.read()

        session_key = aead.AESGCM.generate_key(bit_length=256)
        nonce = os.urandom(12)
        aes = aead.AESGCM(session_key)
        encrypted_payload = aes.encrypt(nonce, plain_data, None)

        encrypted_key = recipient_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        blob = base64.b64encode(encrypted_key + nonce + encrypted_payload).decode()

        output_filename = secrets.token_hex(8) + ".dat"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, "w") as f:
            f.write(blob)

        # Simpan ekstensi asli ke manifest
        manifest[output_filename] = ext

        print(f"[{i}/{total}] {filename} → {output_filename} ✓")
        success += 1

    except Exception as e:
        print(f"[{i}/{total}] FAILED: {filename} — {e}")
        failed += 1

# Simpan manifest
manifest_path = os.path.join(output_folder, "manifest.json")
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

subprocess.run(["rm", "-rf", temp_folder])

print(f"\nDone. {success} berhasil, {failed} gagal.")
print(f"Output disimpan di: '{output_folder}'")
print(f"Manifest ekstensi : '{manifest_path}'")

