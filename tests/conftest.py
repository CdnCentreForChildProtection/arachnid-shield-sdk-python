import pathlib
import os

import numpy as np
import pdqhash
from PIL import Image
import base64

import pytest

from arachnid_shield_sdk import ArachnidShield


@pytest.fixture
def shield():
    username = os.environ.get("ARACHNID_SHIELD_USERNAME", "test")
    password = os.environ.get("ARACHNID_SHIELD_PASSWORD", "test")
    yield ArachnidShield(username=username, password=password)


@pytest.fixture
def unauthorized_shield():
    yield ArachnidShield(username="unauthorized", password="unauthorized")


@pytest.fixture
def example_image_filepath():
    return pathlib.Path(__file__).parent / "dog.jpg"

@pytest.fixture
def example_image(example_image_filepath):
    return example_image_filepath.read_bytes()

def generate_random_pdqhash(count: int = 1):
    data = os.urandom(32 * count)
    results = []
    for start_index in range(0, 32 * count, 32):
        results.append(data[start_index:start_index+32])
    return results


@pytest.fixture
def example_image_pdq_b64encoded(example_image_filepath):
    img = Image.open(str(example_image_filepath))
    arr = np.array(img).astype(np.uint8)
    hash_, quality = pdqhash.compute(arr)
    packed = np.packbits(hash_)
    return base64.b64encode(packed.tobytes()).decode('ascii')
