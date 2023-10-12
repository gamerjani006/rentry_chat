"""
Class for creating and configuring the room
"""
import base64
import json
from projectLibrary.apis import rentry
from projectLibrary.apis import crypto


def getRoomInfo(room_code: str) -> dict:
    raw_data: str = rentry.raw(room_code).get("content")
    metadata: str = raw_data.splitlines()[0]
    json_text_data: str = metadata.split("|")[-1]
    parsed_json_data: dict = json.loads(json_text_data)

    assert metadata.startswith("rtchat|"), "Invalid room code"
    # assert parsed_json_data.get("version") == CONSTANTS.VERSION, "Unsupported version!"
    # TODO: Somehow make a database that shows what versions work with eachother in the future

    return parsed_json_data


class userSession:  # TODO: Get messages, stopping write conflicts(maybe complete, idk)
    def __init__(self, room_code: str, edit_code: str):
        self.room_code: str = room_code
        self.edit_code: str = edit_code
        self.server_metadata: dict = getRoomInfo(self.room_code)
        self.encryption_key = crypto.scryptDeriveKey(
            key=edit_code.encode("utf-8"),
            salt=self.server_metadata.get("encryption_kdf_salt").encode("utf-8"),
        )

        self.get_raw_contents = lambda: rentry.raw(self.room_code).get("content")

        self.encrypt_message = lambda message: base64.b64encode(
            crypto.chaCha20Poly1305EncryptData(
                key=self.encryption_key,
                data=message.encode("utf-8")
            )
        ).decode("utf-8")

        self.decrypt_message = lambda message: crypto.chaCha20Poly1305DecryptVerifyData(
            key=self.encryption_key,
            data=base64.b64decode(message)
        ).decode("utf-8")

        # Verify edit code for safety
        assert self.verify_edit_code(), "Invalid edit code"

    def verify_edit_code(self):
        return crypto.verifyModularCryptDigest(
            modular_digest=self.server_metadata.get("verification_tag"),
            key=self.edit_code.encode("utf-8")
        )

    def send_message(self, message: str):
        rentry.edit(
            url=self.room_code,
            edit_code=self.edit_code,
            text=self.get_raw_contents() + self.encrypt_message(message) + "\n-"
        )

    def getDecryptedRoomMessages(self) -> list:  # TODO: Finish function
        encrypted_messages: list = rentry.raw(self.room_code).get("content").splitlines()[1:-1]
        decrypted_messages: list = []
        for ct in encrypted_messages:
            assert ct.startswith("-"), "Invalid message" + ct
            pt = self.decrypt_message(ct[1:])
            decrypted_messages.append(pt)

        return decrypted_messages
