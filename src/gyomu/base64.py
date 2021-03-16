import base64


class Base64Encode:
    @staticmethod
    def encode_string(plain: str, encoding='UTF-8') -> str:
        return Base64Encode.encode_bytes(plain.encode(encoding=encoding))

    @staticmethod
    def encode_bytes(plain: bytes) -> str:
        return base64.b64encode(plain).decode("ascii")

    @staticmethod
    def decode_string(encoded_string: str, encoding='UTF-8') -> str:
        return Base64Encode.decode_bytes(encoded_string).decode(encoding=encoding)

    @staticmethod
    def decode_bytes(encoded_string: str) -> bytes:
        return base64.b64decode(encoded_string.encode("ascii"))
