# voidcrypt 2.0

🔐 Hybrid RSA-2048 + AES-256-GCM file encryption toolkit.

## Features
- Single file encryption & decryption
- Batch encryption & decryption with folder support
- Video compression via ffmpeg before encryption
- Manifest-based file extension recovery
- Passphrase-protected private key

## Requirements
- Python 3.x
- cryptography library
- ffmpeg (optional, for video compression)

## Usage

### 1. Generate Keys
```bash
python keygen.py
```
### 2.Encrypt
```bash
python encrypt.py        # single file
python batch_encrypt.py  # batch
```
### 3.Decrypt
```bash
python decrypt.py        # single file
python batch_decrypt.py  # batch
```
## Key Location
Private key: ~/.config/sys/.syskey
Public key: ~/.config/sys/.syspub

## Author
voidkod3r
