from gyomu.aes_encryption import AesEncryption
import pytest


def test_aes_encrypt():
    key = "abc"
    plains = ["This is test sample *.code",
              "Looks at me\nThis is the code you want to test",
              "Here is what you want\nToday, it's Friday"]
    for plain in plains:
        encrypted_data = AesEncryption.aes_encrypt(plain, key)
        decrypted_data = AesEncryption.aes_decrypt(encrypted_data, key)
        assert plain == decrypted_data

def test_aes_16encrypt():
    key = "1234567890123456"
    plains = ["This is test sample *.code",
              "Looks at me\nThis is the code you want to test",
              "Here is what you want\nToday, it's Friday"]
    for plain in plains:
        encrypted_data = AesEncryption.aes_encrypt(plain, key)
        decrypted_data = AesEncryption.aes_decrypt(encrypted_data, key)
        assert plain == decrypted_data

def test_aes_24encrypt():
    key = "123456789012345678901234"
    plains = ["This is test sample *.code",
              "Looks at me\nThis is the code you want to test",
              "Here is what you want\nToday, it's Friday"]
    for plain in plains:
        encrypted_data = AesEncryption.aes_encrypt(plain, key)
        decrypted_data = AesEncryption.aes_decrypt(encrypted_data, key)
        assert plain == decrypted_data

def test_aes_32encrypt():
    key = "12345678901234567890123456789012"
    plains = ["This is test sample *.code",
              "Looks at me\nThis is the code you want to test",
              "Here is what you want\nToday, it's Friday"]
    for plain in plains:
        encrypted_data = AesEncryption.aes_encrypt(plain, key)
        decrypted_data = AesEncryption.aes_decrypt(encrypted_data, key)
        assert plain == decrypted_data

def test_aes_33encrypt():
    key = "123456789012345678901234567890123"
    plains = ["This is test sample *.code",
              "Looks at me\nThis is the code you want to test",
              "Here is what you want\nToday, it's Friday"]
    for plain in plains:
        with pytest.raises(ValueError):
            encrypted_data = AesEncryption.aes_encrypt(plain, key)

def test_aes_decrypt_csharp_encryption():
    key ="abc"
    csharp_encrypted_data ="vFJphp+ZhwbyAKIHFf1Br6vEOpM81B8PxT+qJcpm6Dkft26ye+HDrl5J"
    decrypted_text = AesEncryption.aes_decrypt(csharp_encrypted_data,key)
    plain_text="Hello$Test"
    assert plain_text == decrypted_text