"""
Class for creating and configuring the room
"""

import json
from projectLibrary.apis import rentry


def getRoomInfo(room_code: str) -> dict:
    raw_data: str = rentry.raw(room_code).get("content")
    metadata = raw_data.splitlines()[0]
    assert metadata.startswith("rtchat|"), "Invalid room code"

    json_text_data = metadata.split("|")[-1]

    return json.loads(json_text_data)


class userSession:  # TODO: Send/get messages, join room, stopping write conflicts
    def __init__(self):
        pass
