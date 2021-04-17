from Crypto.Cipher import AES
from gyomu.base64 import Base64Encode


class AesEncryption:

    NONCE_BYTE_SIZE: int = 16
    MAC_BYTE_SIZE: int = 16

    @classmethod
    def aes_encrypt(cls, plain: str, key: str, encoding='UTF-8') -> str:
        cipher = cls.__create_cypher(key, encoding)
        plain_bytes = plain.encode(encoding)
        encrypted_bytes, tag = cipher.encrypt_and_digest(plain_bytes)
        output_bytes = cipher.nonce + encrypted_bytes + tag
        return Base64Encode.encode_bytes(output_bytes)
        # encrypted_text = Base64Encode.encode_bytes(encrypted_bytes)
        # tag_text = Base64Encode.encode_bytes(tag)
        # nonce_text = Base64Encode.encode_bytes(cipher.nonce)
        # return nonce_text + "\n" + tag_text + "\n" + encrypted_text

    @classmethod
    def aes_decrypt(cls, encrypted_text: str, key: str, encoding='UTF-8') -> str:

        encrypted_bytes = Base64Encode.decode_bytes(encrypted_text)
        nonce_bytes = encrypted_bytes[:cls.NONCE_BYTE_SIZE]
        tag_bytes = encrypted_bytes[-cls.MAC_BYTE_SIZE:]
        encrypted_bytes = encrypted_bytes[cls.NONCE_BYTE_SIZE:-cls.MAC_BYTE_SIZE]

        # index = encrypted_text.find('\n')
        # index2 = encrypted_text.find('\n', index + 1)
        # nonce_text = encrypted_text[:index]
        # tag_text = encrypted_text[index + 1:index2]
        # encrypted_text = encrypted_text[index2 + 1:]
        # encrypted_bytes = Base64Encode.decode_bytes(encrypted_text)
        # tag_bytes = Base64Encode.decode_bytes(tag_text)
        # nonce_bytes = Base64Encode.decode_bytes(nonce_text)
        cipher = cls.__create_cypher(key, encoding, nonce_bytes)
        plain_bytes = cipher.decrypt_and_verify(encrypted_bytes, tag_bytes)
        return plain_bytes.decode(encoding=encoding)

    @classmethod
    def __create_cypher(cls, key: str, encoding='UTF-8', nonce: bytes = None):
        key_bytes = cls.__get_key(key).encode(encoding)
        if nonce is None:
            return AES.new(key_bytes, AES.MODE_GCM, mac_len=cls.MAC_BYTE_SIZE)
        return AES.new(key_bytes, AES.MODE_GCM, nonce, mac_len=cls.MAC_BYTE_SIZE)

    @classmethod
    def __get_key(cls, key: str) -> str:
        key_length = len(key)
        if key_length < 16:
            return key.ljust(16)
        elif key_length == 16:
            return key
        elif key_length < 32:
            return key.ljust(32)
        elif key_length == 32:
            return key
        else:
            raise ValueError
