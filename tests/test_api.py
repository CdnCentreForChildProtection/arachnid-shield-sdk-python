import pytest
from arachnid_shield_sdk.models import (
    ScanMediaFromBytes,
    ScannedMedia,
    ArachnidShieldException,
    ScanMediaFromPdq,
    MediaClassification,
)


def test_example_image_exists(example_image_filepath, example_image):
    assert True

def verify_example_image(scanned_media: ScannedMedia):
    assert not scanned_media.matches_known_media, "Example dog image doesn't match anything"
    assert scanned_media.match_type is None
    assert scanned_media.sha1_base32 == "TTY4MGOMVNR5KI2ZZ62EMYDZALUTBOHN"
    assert scanned_media.sha256_hex == "8C3B43FB9BA63B7120CEDF87BC9F348BBAAF5D39A97266D0C7587B5EFD6ABA2D"
    assert scanned_media.classification == MediaClassification.NoKnownMatch
    assert scanned_media.near_match_details == []
    assert scanned_media.size_bytes == 24335


def test_scan_media_from_bytes(shield, example_image):
    request = ScanMediaFromBytes(contents=example_image, mime_type="image/jpg")
    scanned_media = shield.scan_media_from_bytes_with_config(request)
    verify_example_image(scanned_media)


def test_scan_media_from_file(shield, example_image_filepath):
    scanned_media = shield.scan_media_from_file(example_image_filepath)
    verify_example_image(scanned_media)


def test_scan_pdq_hashes(shield, example_image_pdq_b64encoded):
    request = ScanMediaFromPdq(hashes=[example_image_pdq_b64encoded])
    scanned_hashes = shield.scan_pdq_hashes(request)
    assert example_image_pdq_b64encoded in scanned_hashes.scanned_hashes
    assert not scanned_hashes.scanned_hashes[example_image_pdq_b64encoded].matches_known_media


def test_scan_unauthorized(unauthorized_shield, example_image_filepath):
    with pytest.raises(
        ArachnidShieldException,
        match='Please supply your API username '
              'and password in the Authorization '
              'header'
    ):
        unauthorized_shield.scan_media_from_file(example_image_filepath)

def test_scan_unauthorized_hostname(shield):
    with pytest.raises(ArachnidShieldException, match='Hostname not authorized for this user') as exc:
        shield.scan_media_from_url("https://example.com")
