from gyomu.base64 import Base64Encode
import pytest
import binascii


def test_encode_string():
    plain = "Hello$Test"
    enc = Base64Encode.encode_string(plain=plain)
    assert plain == Base64Encode.decode_string(enc)


def test_invalid_decode():
    plain = "Hello$Test"
    with pytest.raises(binascii.Error):
        Base64Encode.decode_string(plain)