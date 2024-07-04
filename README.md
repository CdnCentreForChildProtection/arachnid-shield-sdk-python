# arachnid-shield-sdk
An SDK for consuming the Arachnid Shield API.

## Installation

(From `bergpi`)

```sh
pip install arachnid-shield-sdk
```

## Usage

First, obtain login credentials by contacting [Project Arachnid](https://projectarachnid.ca/en/contact). 

This client acts simply as a global resource that may live as long as your application. So you may use it in different ways.

### Vanilla Python (Sync)

```python
from arachnid_shield_sdk import ArachnidShield

shield = ArachnidShield(username="", password="")


class HarmfulMediaFoundException(Exception):
    """Raised when a CSAM/Harmful to Children media is found to be uploaded on the server"""
    user = None
    scanned_media_metadata = None
    
    def __init__(self, user, scanned_media_metadata):
        self.user = user
        self.scanned_media_metadata = scanned_media_metadata

    
def process_media_for_user(user_id, contents):
    """
    
    Raises:
        HarmfulMediaFoundException If the 
    """

    scanned_media = shield.scan_media_from_bytes(contents, "image/jpeg")
    if scanned_media.matches_known_image:
        raise HarmfulMediaFoundException(user=user_id, scanned_media_metadata=scanned_media)
    
    # do more processing here.
    ... 


def main():
    
    with open("some-image.jpeg", "rb") as f:
        contents = f.read()
    
    process_media_for_user(user_id=1, contents=contents)


if __name__ == '__main__':
    main()
```

### Vanilla Python (Async)

```python
import asyncio
from arachnid_shield_sdk import ArachnidShieldAsync as ArachnidShield

shield = ArachnidShield(username="", password="")


class HarmfulMediaFoundException(Exception):
    """Raised when a CSAM/Harmful to Children media is found to be uploaded on the server"""
    user = None
    scanned_media_metadata = None
    
    def __init__(self, scanned_media_metadata):
        self.scanned_media_metadata = scanned_media_metadata

    
async def process_media(contents):
    """
    
    Raises:
        HarmfulMediaFoundException If the 
    """

    scanned_media = await shield.scan_media_from_bytes(contents, "image/jpeg")
    if scanned_media.matches_known_image:
        raise HarmfulMediaFoundException(scanned_media)
    
    # do more processing here.
    ... 


async def main():
    with open("some-image.jpeg", "rb") as f:
        contents = f.read()
    await process_media(contents=contents)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```
