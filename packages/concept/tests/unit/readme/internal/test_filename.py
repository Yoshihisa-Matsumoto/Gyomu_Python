from gyomu_concept.readme.internal.filename import get_readme_filename


class TestGetReadmeFilename:
    def test_english(self) -> None:
        assert get_readme_filename("en") == "README.md"

    def test_japanese(self) -> None:
        assert get_readme_filename("ja") == "README.ja.md"
