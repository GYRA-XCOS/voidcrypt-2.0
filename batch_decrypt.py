import os
import base64
import getpass
import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import aead
from cryptography.hazmat.primitives import hashes, serialization

private_key_path = os.path.expanduser("~/.config/sys/.syskey")

# Muat private key
passphrase = getpass.getpass("Enter passphrase: ").encode()
with open(private_key_path, "rb") as f:
    recipient_private_key = serialization.load_pem_private_key(f.read(), password=passphrase)

# Pilih mode
print("\n[1] Decrypt singgle  file")
print("[2] Decrypt all folder")
mode = input("Pilih mode (1/2): ").strip()

if mode == "1":
    input_file = input("Enter encrypted file path: ")
    output_file = input("Enter output filename (sertakan ekstensi): ")

    try:
        with open(input_file, "r") as f:
            blob = f.read().encode()

        final_blob = base64.b64decode(blob)
        encrypted_session_key = final_blob[:256]
        nonce = final_blob[256:256 + 12]
        encrypted_payload = final_blob[256 + 12:]

        session_key = recipient_private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        aes = aead.AESGCM(session_key)
        plain_data = aes.decrypt(nonce, encrypted_payload, None)

        with open(output_file, "wb") as f:
            f.write(plain_data)

        print(f"Saved to: {output_file}")

    except Exception as e:
        print(f"Dekripsi failed: {e}")

elif mode == "2":
    input_folder = input("Enter input folder: ")
    output_folder = input("Enter output folder: ")
    os.makedirs(output_folder, exist_ok=True)

    # Coba muat manifest jika ada
    manifest_path = os.path.join(input_folder, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        print(f"Manifest found: {len(manifest)} entri.")
    else:
        print("Manifest not found. File extensions will not be restored.")

    files = [
        f for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f)) and f != "manifest.json"
    ]
    total = len(files)

    print(f"Found {total} files. Starting decryption...\n")

    success = 0
    failed = 0

    for i, filename in enumerate(files, 1):
        input_path = os.path.join(input_folder, filename)

        try:
            with open(input_path, "r") as f:
                blob = f.read().encode()

            final_blob = base64.b64decode(blob)
            encrypted_session_key = final_blob[:256]
            nonce = final_blob[256:256 + 12]
            encrypted_payload = final_blob[256 + 12:]

            session_key = recipient_private_key.decrypt(
                encrypted_session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            aes = aead.AESGCM(session_key)
            plain_data = aes.decrypt(nonce, encrypted_payload, None)

            # Pulihkan ekstensi dari manifest jika tersedia
            base_name = os.path.splitext(filename)[0]
            ext = manifest.get(filename, "")
            output_filename = base_name + ext
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb") as f:
                f.write(plain_data)

            print(f"[{i}/{total}] {filename} → {output_filename} ✓")
            success += 1

        except Exception as e:
            print(f"[{i}/{total}] FAILED: {filename} — {e}")
            failed += 1

    print(f"\nDone. {success} berhasil, {failed} gagal.")
    print(f"output is stored in: '{output_folder}'")

else:
    print("infalid mode.")

