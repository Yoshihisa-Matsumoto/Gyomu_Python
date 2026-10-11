import hashlib
import json
from pathlib import Path

from gyomu_schema.error.io import GyomuIOError

from gyomu_infra.hash.hash import hash_file, hash_object, sha256


class TestSha256:
    def test_string(self) -> None:
        value = "hello"

        assert sha256(value) == hashlib.sha256(value.encode("utf-8")).hexdigest()

    def test_bytes(self) -> None:
        value = b"hello"

        assert sha256(value) == hashlib.sha256(value).hexdigest()

    def test_unicode_string(self) -> None:
        value = "こんにちは"

        assert sha256(value) == hashlib.sha256(value.encode("utf-8")).hexdigest()


class TestHashFile:
    def test_hash_file(self, tmp_path: Path) -> None:
        path = tmp_path / "test.txt"
        content = b"hello"

        path.write_bytes(content)

        result = hash_file(path)

        assert result.unwrap() == hashlib.sha256(content).hexdigest()

    def test_same_content_produces_same_hash(
        self,
        tmp_path: Path,
    ) -> None:
        path1 = tmp_path / "test1.txt"
        path2 = tmp_path / "test2.txt"
        content = b"same content"

        path1.write_bytes(content)
        path2.write_bytes(content)

        assert hash_file(path1).unwrap() == hash_file(path2).unwrap()

    def test_different_content_produces_different_hash(
        self,
        tmp_path: Path,
    ) -> None:
        path1 = tmp_path / "test1.txt"
        path2 = tmp_path / "test2.txt"

        path1.write_bytes(b"content 1")
        path2.write_bytes(b"content 2")

        assert hash_file(path1).unwrap() != hash_file(path2).unwrap()

    def test_missing_file_returns_failure(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "missing.txt"

        result = hash_file(path)

        assert result.failure() is not None
        assert isinstance(result.failure(), GyomuIOError)


class TestHashObject:
    def test_returns_sha256_of_json_serialized_string(self) -> None:
        target = "Gyomu"

        actual = hash_object(target)

        expected = sha256(
            json.dumps(
                target,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        assert actual == expected

    def test_returns_same_hash_for_same_object(self) -> None:
        target = {"name": "Gyomu", "version": 1}

        actual = hash_object(target)

        assert actual == hash_object(target)

    def test_preserves_non_ascii_characters_in_json(self) -> None:
        target = {"name": "業務"}

        actual = hash_object(target)

        expected = sha256('{"name":"業務"}')
        assert actual == expected

    def test_uses_compact_json_serialization(self) -> None:
        target = {"name": "Gyomu", "version": 1}

        actual = hash_object(target)

        expected = sha256('{"name":"Gyomu","version":1}')
        assert actual == expected
