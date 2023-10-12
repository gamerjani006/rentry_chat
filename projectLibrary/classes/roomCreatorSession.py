"""
Class for creating and configuring the room
"""

import secrets
import json
import base64

from projectLibrary.apis import rentry
from projectLibrary.apis import CONSTANTS
from projectLibrary.apis import crypto


def getConfigText(room_code: bytes, edit_code: bytes) -> str:
    derived_verification_tag: str = crypto.scryptDeriveKeyModular(
        key=edit_code,
        salt=room_code,
        derived_key_length=16
    )
    data = {
        "version": CONSTANTS.VERSION,
        "verification_tag": derived_verification_tag,
        "encryption_kdf_salt": secrets.token_urlsafe(16),
    }

    config_data = json.dumps(data)
    config_text = f"{CONSTANTS.NAME}${config_data}"

    return config_text


class roomCreatorSession:
    def __init__(self, edit_code: str):
        self.room_code: str = secrets.token_urlsafe(16)
        self.edit_code: str = edit_code
        self.encryption_kdf_salt = secrets.token_urlsafe(16)

        self.encryption_key = crypto.scryptDeriveKey(
            key=edit_code.encode("utf-8"),
            salt=self.encryption_kdf_salt.encode("utf-8"),
        )
        self.encrypt_message = lambda message: base64.b64encode(
            crypto.chaCha20Poly1305EncryptData(
                key=self.encryption_key,
                data=message.encode("utf-8")
            )
        )

    def create_room(self):
        # TODO: Check if room already exists, send first system message
        config_text: str = getConfigText(
            room_code=self.room_code.encode("utf-8"),
            edit_code=self.edit_code.encode("utf-8"),
        ) + f"\n-{self.encrypt_message('CHAT START')}\n-"

        rentry.new(
            url=self.room_code,
            edit_code=self.edit_code,
            text=config_text,
        )
