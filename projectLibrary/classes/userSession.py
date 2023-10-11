"""
Class for creating and configuring the room
"""

import json
from projectLibrary.apis import rentry
from projectLibrary.apis import crypto


def getRoomInfo(room_code: str) -> dict:
    raw_data: str = rentry.raw(room_code).get("content")
    metadata = raw_data.splitlines()[0]
    json_text_data = metadata.split("|")[-1]
    parsed_json_data = json.loads(json_text_data)

    assert metadata.startswith("rtchat|"), "Invalid room code"
    # assert parsed_json_data.get("version") == CONSTANTS.VERSION, "Unsupported version!"
    # TODO: Somehow make a database that shows what versions work with eachother in the future

    return parsed_json_data


class userSession:  # TODO: Send/get messages, join room, stopping write conflicts
    def __init__(self, room_code: str, edit_code: str):
        self.room_code: str = room_code
        self.edit_code: str = edit_code
        self.server_metadata: dict = getRoomInfo(self.room_code)

    def verify_edit_code(self):
        return crypto.verifyModularCryptDigest(
            modular_digest=self.server_metadata.get("verification_tag"),
            key=self.edit_code.encode("utf-8")
        )
