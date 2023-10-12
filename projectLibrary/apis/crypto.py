import secrets

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import constant_time
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import base64


def scryptDeriveKey(key: bytes, salt: bytes, derived_key_length: int = 32) -> bytes:
    """
    :param key: n byte key
    :param salt: 16 byte salt
    :param derived_key_length: length of derived key
    :return: n byte key
    """

    kdf: Scrypt = Scrypt(
        salt=salt,
        length=derived_key_length,
        n=2 ** 14,
        r=8,
        p=1,
    )
    scrypt_derived_key: bytes = kdf.derive(key)

    return scrypt_derived_key


def scryptDeriveKeyModular(
    key: bytes, salt: bytes, derived_key_length: int = 32
) -> str:
    """
    :param key: n byte key
    :param salt: 16 byte salt
    :param derived_key_length: length of derived key
    :return: modular crypt version of scryptDeriveKey
    """

    kdf: Scrypt = Scrypt(
        salt=salt,
        length=derived_key_length,
        n=2 ** 14,
        r=8,
        p=1,
    )
    scrypt_derived_key: bytes = kdf.derive(key)

    modular_digest: str = (
        f"sDKM$"
        f"{derived_key_length}$"
        f"{base64.b32encode(salt).decode().lower()}$"
        f"{base64.b32encode(scrypt_derived_key).decode().lower()}"
    )

    return modular_digest.replace(
        "=", ""
    )  # remove the equals signs because they're not in the [a-zA-Z0-9./] regex


def parseModularCryptParams(modular_crypt_derived_key: str) -> dict:
    assert modular_crypt_derived_key.startswith("sDKM$")
    key_split = modular_crypt_derived_key.split("$")

    params: dict = {
        "length": int(key_split[1]),
        "salt": key_split[2],
        "digest": key_split[3],
    }
    return params


def verifyModularCryptDigest(modular_digest: str, key: bytes):
    params = parseModularCryptParams(modular_digest)
    derived_key = scryptDeriveKeyModular(
        key=key,
        salt=base64.b32decode(params.get("salt").upper() + "===="),
        derived_key_length=params.get("length"),
    )
    return constant_time.bytes_eq(
        modular_digest.encode("utf-8"), derived_key.encode("utf-8")
    )


def chaCha20Poly1305EncryptData(key: bytes, data: bytes):
    """
    :param key: 32 byte key
    :param data: Data of any length
    :return: 12 byte nonce; n byte ciphertext; 16 byte tag
    """
    aad: bytes = b"rtchat\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16"
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(key)
    nonce: bytes = secrets.token_bytes(12)
    ciphertext: bytes = cipher.encrypt(
        nonce=nonce,
        data=data,
        associated_data=aad,
    )

    return nonce + ciphertext


def chaCha20Poly1305DecryptVerifyData(key: bytes, data: bytes):
    aad: bytes = b"rtchat\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16"
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(key)
    nonce: bytes = data[0:12]
    plaintext: bytes = cipher.decrypt(
        nonce=nonce,
        data=data[12:],
        associated_data=aad
    )
    return plaintext
