import os
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import aead
from cryptography.hazmat.primitives import hashes, serialization

public_key_path = os.path.expanduser("~/.config/sys/.syspub")

# Memuat kunci publik
with open(public_key_path, "rb") as public_file:
    recipient_public_key = serialization.load_pem_public_key(public_file.read())

# Input file
input_file = input("Enter file path: ")
with open(input_file, "rb") as f:
    plain_input_data = f.read()

# Generate kunci sesi
session_symmetric_key = aead.AESGCM.generate_key(bit_length=256)
session_nonce = os.urandom(12)

# Enkripsi data
aes_engine = aead.AESGCM(session_symmetric_key)
encrypted_payload = aes_engine.encrypt(session_nonce, plain_input_data, None)

# Enkripsi kunci sesi
encrypted_session_key = recipient_public_key.encrypt(
    session_symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Gabungkan dan encode
final_transport_blob = base64.b64encode(
    encrypted_session_key + session_nonce + encrypted_payload
).decode()

# Simpan output
output_file = input("Enter output filename: ")
with open(output_file, "w") as f:
    f.write(final_transport_blob)
print(f"Saved to: {output_file}")
