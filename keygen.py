import getpass
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key_path = os.path.expanduser("~/.config/sys/.syskey")
public_key_path = os.path.expanduser("~/.config/sys/.syspub")

# --- 0. Buat direktori jika belum ada ---
os.makedirs(os.path.dirname(private_key_path), exist_ok=True)

# --- 1. Generate Private Key ---
asymmetric_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# --- 2. Ekstrak Public Key ---
asymmetric_public_key = asymmetric_private_key.public_key()

# --- 3. Minta passphrase ---
passphrase = getpass.getpass("enter passphrase: ").encode()
confirm = getpass.getpass("confirm passphrase: ").encode()

if passphrase != confirm:
    print("passphrase mismatch, cancel.")
    exit(1)

# --- 4. Simpan Kunci Privat ---
with open(private_key_path, "wb") as private_file:
    private_file.write(asymmetric_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
    ))

# --- 5. Simpan Kunci Publik ---
with open(public_key_path, "wb") as public_file:
    public_file.write(asymmetric_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("Key generation completed.")
print(f"  Private key : {private_key_path}")
print(f"  Public key  : {public_key_path}")

