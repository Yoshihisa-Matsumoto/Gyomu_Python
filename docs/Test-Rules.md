# Gyomu-Python Test Rules

## 1. 基本方針

Gyomu-Pythonでは、pytestをテストフレームワークとして使用する。

テストは原則として以下の2種類に分離する。

- Unit Test
- Integration Test

通常の開発・CIではUnit Testを中心に実行し、外部システムへの接続が必要なIntegration Testは明示的に実行する。

---

## 2. テストディレクトリ構成

各packageでは、原則として以下の構成を採用する。

```text
packages/<package>/
├── src/
│   └── <package_source>/
│
└── tests/
    ├── unit/
    │   ├── mapper/
    │   ├── repository/
    │   ├── service/
    │   └── ...
    │
    └── integration/
        ├── database/
        ├── ai/
        ├── external_api/
        └── ...
```

### Unit Test

外部システムに依存しないテスト。

例:

- 純粋なロジック
- Mapper
- Service
- RepositoryのMockを利用したテスト
- Error Handling
- ResultのSuccess / Failure

### Integration Test

実際の外部システムやInfrastructureとの接続を確認するテスト。

例:

- SQL Server
- 外部API
- Gemini等のLLM API
- その他の外部サービス

---

## 3. Unit / Integrationを物理的に分離する

原則として、Unit TestとIntegration Testを同じディレクトリ・同じテストファイルに混在させない。

```text
tests/
├── unit/
└── integration/
```

という物理的な分離を基本とする。

これにより、実行対象をディレクトリで明確に指定できる。

```powershell
# Unit Testのみ
uv run pytest packages/infra/tests/unit

# Integration Testのみ
uv run pytest packages/infra/tests/integration
```

---

## 4. Integration Testは通常のテスト実行から除外する

Integration Testは、以下の理由から通常の開発サイクル・通常のCIでは実行しない。

- DB接続が必要
- API KeyなどのSecretが必要
- ネットワーク接続が必要
- API料金が発生する可能性がある
- Rate Limitの影響を受ける
- 外部サービス障害の影響を受ける
- 実行時間が長くなる可能性がある

通常の開発ではUnit Testを実行する。

```powershell
uv run pytest packages/<package>/tests/unit
```

Integration Testは必要なときだけ明示的に実行する。

```powershell
uv run pytest packages/<package>/tests/integration
```

---

## 5. pytest marker

Integration Testには`integration` markerを使用できる。

`pyproject.toml`に登録する。

```toml
[tool.pytest.ini_options]
markers = [
    "integration: tests requiring external infrastructure",
]
```

### ファイル単位でmarkerを付ける

同じファイル内のすべてのテストがIntegration Testである場合、各関数にmarkerを書くのではなく、ファイル先頭で`pytestmark`を使用する。

```python
import pytest

pytestmark = pytest.mark.integration
```

これにより、そのファイル内の全テストがIntegration Testとして扱われる。

### 複数marker

必要に応じて複数のmarkerをファイル単位で付けられる。

```python
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.ai,
]
```

例えばAI Integration Testでは、

```python
pytestmark = [
    pytest.mark.integration,
    pytest.mark.ai,
]
```

とする。

### 関数単位marker

関数単位のmarkerは原則使用しない。

同一ファイル内にUnit TestとIntegration Testを混在させる必要がある特殊なケースのみ使用する。

---

## 6. Integration Testの環境依存

Integration Testでは、必要な環境変数や外部リソースが存在しない場合、安全にSkipできるようにする。

例:

```python
connection = os.getenv("GYOMU_COMMON_MAINDB_CONNECTION")

if connection is None:
    pytest.skip(
        "GYOMU_COMMON_MAINDB_CONNECTION is not configured"
    )
```

これはIntegration Testを通常実行するための仕組みではなく、

> Integration Testを明示的に実行したが、必要な環境が存在しない場合の安全装置

として扱う。

「実行対象かどうか」はUnit / Integrationのディレクトリやpytest markerで管理し、「実行可能な環境かどうか」は環境変数等で判定する。

---

## 7. CIでのテスト方針

通常のCIでは、Integration Testを実行しない。

基本的なCIの流れは、

```text
Ruff
  ↓
mypy
  ↓
Unit Test
```

とする。

Integration Testは必要に応じて別CI Jobとして用意する。

Integration Test用Jobにのみ、DB接続情報やAPI KeyなどのSecretを渡す。

```text
Unit Test Job
    ↓
Secret不要
    ↓
常時実行可能


Integration Test Job
    ↓
DB/API等の外部環境
    ↓
必要なSecretをJob単位で提供
    ↓
明示的に実行
```

---

## 8. テストファイルの命名

テストファイルは、プロジェクト全体で意味が分かりやすい名前にする。

基本形式:

```text
test_<対象>.py
```

例:

```text
test_market_holiday_mapper.py
test_market_holiday_repository.py
test_market_holiday_service.py
```

Integration Testの場合、必要に応じて`_integration`を付ける。

```text
test_market_holiday_repository_integration.py
```

同名のテストファイルを異なるディレクトリに配置することは避ける。

例えば、

```text
# 避ける
tests/unit/repository/test_market_holiday_repository.py
tests/integration/repository/test_market_holiday_repository.py
```

より、

```text
tests/unit/repository/test_market_holiday_repository.py
tests/integration/repository/test_market_holiday_repository_integration.py
```

とする。

これはpytestおよびPythonのimport/module解決時の混乱を避け、テストファイルを一意に識別しやすくするためである。

---

## 9. テスト関数の命名

テスト関数は、何を検証しているかが名前から分かるようにする。

基本形式:

```python
def test_<対象>_<条件>_<期待結果>():
    ...
```

例:

```python
def test_find_by_market_returns_success():
    ...

def test_find_by_market_returns_empty_when_no_data():
    ...

def test_find_by_market_returns_database_error_when_db_fails():
    ...
```

テスト関数名そのものをプロジェクト全体で一意にする必要はない。

pytestはファイル・クラス・関数からテストのnode IDを構成して識別する。

---

## 10. テスト対象を限定して実行する

pytestでは、全テストを実行する必要はない。

### テストファイル

```powershell
uv run pytest packages/infra/tests/unit/repository/test_market_holiday_repository.py
```

### テスト関数

```powershell
uv run pytest packages/infra/tests/unit/repository/test_market_holiday_repository.py::test_find_by_market_returns_success
```

### `-k`による名前検索

```powershell
uv run pytest -k "find_by_market"
```

### marker

```powershell
# Integration Testのみ
uv run pytest -m integration

# Integration Testを除外
uv run pytest -m "not integration"
```

開発時には変更対象を絞って実行し、CIなどでは必要な範囲をまとめて実行する。

---

## 11. Unit Testでの外部依存

Unit Testでは、外部システムへ接続しない。

例えばRepositoryでは、

```text
Unit Test
    ↓
Mock Session
    ↓
Repository
```

とする。

SQL Serverとの実際の互換性はIntegration Testで確認する。

同様にAI関連では、

```text
Unit Test
    ↓
Mock / Fake LLM
    ↓
Application logic
```

とし、実際のGemini等への接続はIntegration Testで確認する。

---

## 12. Repository Testの基本ケース

Repositoryについては、最低限以下を確認する。

### 成功

```text
DB access
    ↓
Success[data]
```

### 該当データなし

```text
DB access
    ↓
Success([])
```

0件はエラーではない。

### 想定されたInfrastructure Error

```text
SQLAlchemyError
    ↓
DatabaseError
    ↓
Failure[DatabaseError]
```

### 想定外のException

```text
ValueError等
    ↓
そのままraise
```

すべてのExceptionを無条件にResult化しない。

---

## 13. Result / Error Handlingのテスト

GyomuではResultを使用して明示的にエラーを扱う。

Repository / Serviceのテストでは、

```text
Success
Failure
```

を明確に検証する。

例えば、

```python
from returns.result import Failure, Success

result = repository.find_by_market("#TEST")

assert isinstance(result, Success)
```

Errorの場合:

```python
result = repository.find_by_market("#TEST")

assert isinstance(result, Failure)
assert isinstance(result.failure(), DatabaseError)
```

ResultのError型と実際のError型が設計どおりであることをテストする。

---

## 14. テストの実行頻度

基本的な開発サイクル:

```text
コード編集
    ↓
Save
    ↓
Ruff Formatter
    ↓
Ruff Linter
    ↓
Pylance
    ↓
必要なUnit Test
```

型チェック:

```powershell
uv run mypy packages/<package>/src
```

テスト:

```powershell
uv run pytest packages/<package>/tests/unit
```

Integration Test:

```powershell
uv run pytest packages/<package>/tests/integration
```

必要なときだけ明示的に実行する。

---

## 15. Watch Mode

pytest本体はVitestと同じwatch modeを標準機能として持っているわけではない。

必要になった場合はpytest watcher系のpluginを導入し、

```text
test file変更
    ↓
該当Unit Testを自動再実行
```

という開発体験を構築する。

ただし、watcherは必要性が明確になってから導入する。

---

## 16. Gyomu-Pythonの基本ルールまとめ

### テスト配置

```text
packages/<package>/
├── src/
└── tests/
    ├── unit/
    └── integration/
```

### 実行方針

```text
Unit
    → 通常開発
    → 通常CI
    → 外部環境不要

Integration
    → 明示的に実行
    → 必要な環境を用意
    → 通常CIとは分離
```

### Marker

```text
integration
    → ファイル単位でpytestmarkを設定
    → 関数単位は例外的に使用
```

### 命名

```text
test_<対象>.py
test_<対象>_integration.py
```

テストファイルはプロジェクト内で一意になるようにする。

### Unit Test

外部システムをMock / Fake化する。

### Integration Test

実際のDB/API/LLM等との接続を検証する。

### CI

```text
Ruff
  ↓
mypy
  ↓
Unit Test
```

を基本とし、Integration Testは別途管理する。
