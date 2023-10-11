from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
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


def scryptDeriveKeyModular(key: bytes, salt: bytes, derived_key_length: int = 32) -> str:
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

    modular_digest: str = f"sDKM$" \
                          f"{derived_key_length}$" \
                          f"{base64.b32encode(salt).decode().lower()}$" \
                          f"{base64.b32encode(scrypt_derived_key).decode().lower()}"

    return modular_digest.replace("=", "")  # remove the equals signs because they're not in the [a-zA-Z0-9./] regex


def chachaEncryptData():
    pass


def chachaDecryptData():
    pass
