"""
Class for creating and configuring the room
"""

import secrets
import json
from projectLibrary.apis import rentry
from projectLibrary.apis import CONSTANTS
from projectLibrary.apis.crypto import scryptDeriveKeyModular


def getConfigText(room_code: bytes, edit_code: bytes) -> str:
    derived_verification_tag: str = scryptDeriveKeyModular(
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

    def create_room(self):
        # TODO: Check if room already exists
        config_text: str = getConfigText(
            room_code=self.room_code.encode("utf-8"),
            edit_code=self.edit_code.encode("utf-8"),
        )

        rentry.new(
            url=self.room_code,
            edit_code=self.edit_code,
            text=config_text,
        )
