from returns.result import Failure, Success

from gyomu_infra.stream.record_stream import RecordStream


class TestRecordStream:
    def test_map(self) -> None:
        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Success(2),
                    Success(3),
                ]
            )
        )

        result = list(stream.map(lambda value: value * 10))

        assert result == [
            Success(10),
            Success(20),
            Success(30),
        ]

    def test_map_preserves_failure(self) -> None:
        error = ValueError("invalid")

        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Failure(error),
                    Success(3),
                ]
            )
        )

        result = list(stream.map(lambda value: value * 10))

        assert result == [
            Success(10),
            Failure(error),
            Success(30),
        ]

    def test_filter(self) -> None:
        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Success(2),
                    Success(3),
                    Success(4),
                ]
            )
        )

        result = list(stream.filter(lambda value: value % 2 == 0))

        assert result == [
            Success(2),
            Success(4),
        ]

    def test_filter_preserves_failure(self) -> None:
        error = ValueError("invalid")

        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Failure(error),
                    Success(2),
                ]
            )
        )

        result = list(stream.filter(lambda value: value > 1))

        assert result == [
            Failure(error),
            Success(2),
        ]

    def test_tap(self) -> None:
        values: list[int] = []

        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Success(2),
                ]
            )
        )

        result = list(stream.tap(values.append))

        assert values == [1, 2]
        assert result == [
            Success(1),
            Success(2),
        ]

    def test_tap_failure(self) -> None:
        errors: list[ValueError] = []
        error = ValueError("invalid")

        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Failure(error),
                    Success(2),
                ]
            )
        )

        result = list(stream.tap_failure(errors.append))

        assert errors == [error]
        assert result == [
            Success(1),
            Failure(error),
            Success(2),
        ]

    def test_is_lazy(self) -> None:
        consumed = False

        def source():
            nonlocal consumed
            consumed = True
            yield Success(1)

        stream = RecordStream.from_iterator(source())

        mapped = stream.map(lambda value: value * 10)

        assert consumed is False

        assert list(mapped) == [Success(10)]

        assert consumed is True

    def test_is_single_use(self) -> None:
        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Success(2),
                ]
            )
        )

        assert list(stream) == [
            Success(1),
            Success(2),
        ]

        assert list(stream) == []

    def test_collect(self) -> None:
        error = ValueError("invalid")

        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Failure(error),
                    Success(3),
                ]
            )
        )

        result = stream.collect()

        assert result == [
            Success(1),
            Failure(error),
            Success(3),
        ]

    def test_collect_consumes_stream(self) -> None:
        stream = RecordStream.from_iterator(
            iter(
                [
                    Success(1),
                    Success(2),
                ]
            )
        )

        assert stream.collect() == [
            Success(1),
            Success(2),
        ]

        assert stream.collect() == []
