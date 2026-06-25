import os
import base64
import getpass
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import aead
from cryptography.hazmat.primitives import hashes, serialization

private_key_path = os.path.expanduser("~/.config/sys/.syskey")

# Minta passphrase
passphrase = getpass.getpass("Masukkan passphrase: ").encode()

# Memuat kunci privat
with open(private_key_path, "rb") as private_file:
    recipient_private_key = serialization.load_pem_private_key(private_file.read(), password=passphrase)

# Input file terenkripsi
input_file = input("Enter encrypted file path: ")
with open(input_file, "r") as f:
    encrypted_input = f.read().encode()

# Dekode dari base64
final_transport_blob = base64.b64decode(encrypted_input)

# Ekstraksi komponen
encrypted_session_key = final_transport_blob[:256]
session_nonce = final_transport_blob[256:256 + 12]
encrypted_payload = final_transport_blob[256 + 12:]

# Dekripsi kunci sesi
session_symmetric_key = recipient_private_key.decrypt(
    encrypted_session_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Dekripsi payload
aes_engine = aead.AESGCM(session_symmetric_key)
plain_output_data = aes_engine.decrypt(session_nonce, encrypted_payload, None)

# Simpan output
output_file = input("Enter output filename: ")
with open(output_file, "wb") as f:
    f.write(plain_output_data)
print(f"Saved to: {output_file}")
