# Python版Gyomu — Error Handling / Result Design Rules

## 1. 目的

Python版Gyomuでは、エラーを単なる例外処理の仕組みとしてではなく、

- エラーの意味
- 発生した操作・箇所
- 診断に必要な情報
- 元の例外
- 上位層への伝播方法

を一貫して扱うための設計基盤として定義する。

本ドキュメントでは、Gyomuにおける以下のルールを定義する。

- Error階層
- `BaseError`
- Error Context
- Error Details
- Python Exception Chaining
- `Result`
- Error変換
- I/O境界
- `ConfigError`
- Errorを追加する際の原則

---

# 2. 基本原則

Python版Gyomuでは、

> **予想可能なFailureは`Result`として扱い、Exceptionはエラー情報そのものを表現するために利用する。**

という考え方を基本とする。

したがって、

```text
Exception
    ↓
Error情報を表現
```

と

```text
Result
    ↓
Failureを呼び出し側へ伝播
```

は別の責務として扱う。

---

# 3.Error階層

Gyomu固有のErrorは、Python標準の`Exception`を直接継承せず、`BaseError`を共通基底とする。

概念上の構造は以下。

```text
Exception
    │
    ▼
BaseError
    │
    ├── GyomuIOError
    │       │
    │       └── DatabaseError
    │
    ├── ConfigError
    │
    └── ValidationError
```

`BaseError`はGyomu Error共通の基盤を提供する。

---

# 4. BaseError

現在の基本形：

```python
class BaseError(Exception):
    """Base class for Gyomu errors."""


    def __init__(
        self,
        message: str,
        *,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.context = context
        self.details = details
```

`BaseError`は、Gyomu Errorに共通する診断情報を保持する。

基本的な情報は以下。

```text
BaseError
├── message
├── context
└── details
```

---

# 5. message

`message`は、人間が読んだときにエラーの概要を理解できるメッセージとする。

例：

```python
ConfigError(
    "Database connection string is not configured",
)
```

`message`には、可能な限りエラーの概要を簡潔に記述する。

詳細な診断情報をすべて`message`へ埋め込むことは避ける。

構造化して扱うべき情報は`details`を使用する。

---

# 6. context

`BaseError.context`は、

> **エラーが発生した操作・発生箇所を示す、人間が読める識別子**

として使用する。

例：

```python
context="DbConnectionFactory.create_engine"
```

または、

```python
context="SqlAlchemyMarketHolidayRepository.find_by_market"
```

など。

## 6.1 contextの目的

`context`は、

```text
何をしているときに発生したエラーなのか
```

を迅速に把握するために使用する。

特に、同じError Typeが複数の場所で発生する場合に有効である。

---

## 6.2 contextはtracebackの代替ではない

`context`はPythonのtracebackを置き換えるものではない。

```text
context
    ↓
人間が理解しやすい操作・発生箇所


traceback
    ↓
実際のコード実行経路
```

という異なる役割を持つ。

したがって、tracebackから得られる情報を`context`へ無理にコピーしない。

---

# 7. details

`BaseError.details`は、

> **エラーの診断に利用する追加の構造化情報**

を保持するために使用する。

型は基本的に、

```python
Mapping[str, object] | None
```

とする。

例：

```python
ConfigError(
    "Database connection string is not configured",
    context="DbConnectionFactory.create_engine",
    details={
        "environment_variable": GYOMU_COMMON_MAINDB_CONNECTION,
    },
)
```

## 7.1 detailsの目的

`details`は、エラーの発生原因を調査するときに役立つ情報を構造化して保持する。

例えば、

- 使用した設定項目
- 対象となった識別子
- 入力値の一部
- 外部サービスの識別情報
- DB操作の対象
- その他の診断情報

など。

---

## 7.2 detailsに何でも入れない

`details`は「とりあえず情報を全部入れる場所」ではない。

特に、

- traceback
- 元例外そのもの
- 巨大なオブジェクト
- 秘密情報
- パスワード
- API Key
- Connection String全体

などを無条件に格納しない。

元例外についてはPythonのException Chainingを使用する。

---

# 8. 元例外はException Chainingを利用する

Gyomuでは、元となった例外を独自の`cause`属性へコピーして保持しない。

Python標準の、

```python
raise NewError(...) from error
```

を使用する。

例えば、

```python
try:
    return create_engine(connection_string)
except SQLAlchemyError as error:
    raise ConfigError(
        "Database connection configuration is invalid",
        context="DbConnectionFactory.create_engine",
    ) from error
```

とする。

これにより、

```text
ConfigError
    │
    └── __cause__
            │
            └── SQLAlchemyError
```

という構造になる。

---

# 9. Exception Chainingを使用する理由

元例外を`details`へ格納するのではなく、Python標準のException Chainingを利用することで、

- traceback
- 元例外の型
- 元例外のメッセージ
- 原因関係

をPythonの標準機構として保持できる。

したがって、Gyomu Errorでは、

```python
message
context
details
```

と、

```python
__cause__
```

をそれぞれ異なる目的で利用する。

---

# 10. Resultの役割

`Result`は、**呼び出し側が処理すべき予想可能なFailureを値として伝播するために使用する。**

基本形：

```python
Result[SuccessType, ErrorType]
```

例えばRepositoryでは、

```python
Result[list[MarketHoliday], GyomuIOError]
```

とする。

---

# 11. ResultとExceptionの使い分け

すべてのExceptionを無条件に`Result`へ変換するわけではない。

基本的には、

```text
予想可能なFailure
        ↓
Result Failure
```

とする。

一方、

```text
Programming Error
予期しないバグ
不変条件違反
```

などまで、

```python
try:
    ...
except Exception:
    ...
```

によって無条件にResultへ変換しない。

---

# 12. I/O境界ではErrorを変換する

外部ライブラリ固有のExceptionを、Gyomuの上位層へそのまま漏らさない。

例えばSQLAlchemyの場合、

```text
SQLAlchemyError
        ↓
DatabaseError
        ↓
GyomuIOError
        ↓
Result Failure
```

という境界を作る。

---

# 13. 外部ライブラリExceptionをGyomu Errorへ変換する

外部ライブラリ固有のExceptionは、Infrastructure層でGyomu固有のErrorへ変換する。

例えば、

```python
def to_database_error(error: SQLAlchemyError) -> DatabaseError:
    return DatabaseError(str(error))
```

とする。

Repositoryでは、

```python
return self._find_by_market(market).alt(
    to_database_error,
)
```

のように、外部ライブラリのErrorをGyomu Errorへ変換する。

これにより上位層は、

```text
SQLAlchemy
```

などの具体的なライブラリに依存せず、

```text
DatabaseError
```

というGyomu側のErrorとして扱える。

---

# 14. RepositoryにおけるError伝播

RepositoryはI/O境界であるため、予想可能なDB Failureを`Result`として返す。

概念的には、

```text
SQLAlchemy
    ↓
SQLAlchemyError
    ↓
DatabaseError
    ↓
Result.Failure
```

となる。

例えば、

```python
def find_by_market(
    self,
    market: str,
) -> Result[list[MarketHoliday], GyomuIOError]:
    ...
```

とする。

---

# 15. ServiceにおけるError伝播

ServiceはRepositoryなどの下位層から返された`Result`を受け取り、必要に応じてそのまま上位層へ伝播させる。

不要なError変換を行わない。

例えば、

```text
Repository
    ↓
Result[T, DatabaseError]
    ↓
Service
    ↓
Result[T, DatabaseError]
```

のように、意味が変わらない場合はそのまま伝播させる。

---

# 16. Error変換は意味が変わる境界で行う

Errorを単に別の型へ変換するためだけに変換を重ねない。

Error変換は、

> **下位層の具体的な技術情報を、上位層が理解できるGyomu上の意味へ変換する必要がある場所**

で行う。

例えば、

```text
SQLAlchemyError
```

を、

```text
DatabaseError
```

へ変換することには意味がある。

一方、意味が変わらないのに、

```text
ErrorA
 ↓
ErrorB
 ↓
ErrorC
```

と変換を重ねることは避ける。

---

# 17. ConfigError

`ConfigError`は、

> **Gyomuが必要とするConfigurationを取得・解釈・検証できない場合のError**

として使用する。

Configurationの取得元そのものには依存しない。

例えば、

```text
Environment Variable
        ↓
ConfigError


YAML
        ↓
ConfigError


JSON
        ↓
ConfigError


その他のConfiguration Source
        ↓
ConfigError
```

とする。

したがって、

```text
EnvironmentVariableError
YamlError
JsonError
```

のようにConfiguration SourceごとのErrorを増やすことは、必要性がない限り避ける。

---

# 18. Error Contextの記述原則

`context`には、可能な限り、

```text
ClassName.method_name
```

など、人間が理解しやすい識別子を使用する。

例：

```text
DbConnectionFactory.create_engine
SqlAlchemyMarketHolidayRepository.find_by_market
```

ただし、contextを過度に詳細化しない。

目的は、

「どの操作・発生箇所のFailureなのか」を素早く把握すること

である。

---

# 19. Error Detailsの記述原則

`details`には、後から診断するときに有用な情報を構造化して格納する。

例：

```python
details={
    "environment_variable": "GYOMU_COMMON_MAINDB_CONNECTION",
}
```

可能な限り、機械的に扱いやすい構造を維持する。

また、機密情報を含めない。

---

# 20. Errorを追加する判断基準

新しいError Typeを追加するときは、

> **既存のError Typeでは意味を適切に表現できないか**

を最初に検討する。

単に処理ごとにError Typeを作らない。

例えば、

```text
MarketHolidayRepositoryError
BusinessCalendarError
DbConnectionFactoryError
```

などを機械的に追加することは避ける。

Error Typeは「どこで発生したか」ではなく、

> **何を意味するFailureなのか**

を表現するために使用する。

発生場所は`context`で表現する。

---

# 21. Error TypeとContextの役割分担

Error Type：

```text
何が問題なのか
```

Context：

```text
どの操作・場所で発生したのか
```

Details：

```text
診断に必要な追加情報は何か
```

Cause：

```text
元々何が原因だったのか
```

例えば、

```python
DatabaseError
    context:
        SqlAlchemyMarketHolidayRepository.find_by_market


    details:
        {
            "market": "JPX"
        }


    __cause__:
        SQLAlchemyError
```

という構造になる。

---

# 22. Tracebackとの役割分担

Error情報は、以下のように役割を分担する。

```text
Error Type
    ↓
Failureの意味


message
    ↓
人間向けの概要


context
    ↓
操作・発生箇所


details
    ↓
診断用の構造化情報


__cause__
    ↓
元例外


traceback
    ↓
実際の実行経路
```

これらを重複させない。

---

# 23. Error設計の基本モデル

GyomuのErrorは、概念的に以下の情報を持つ。

```text
┌─────────────────────────────┐
│ Gyomu Error                 │
├─────────────────────────────┤
│ Error Type                  │
│ message                     │
│ context                     │
│ details                     │
│                             │
│ __cause__                   │
│                             │
│ traceback                   │
└─────────────────────────────┘
```

それぞれの情報は異なる目的で使用する。

---

#24. Result設計の基本モデル

Resultは、

```text
┌─────────────────────────────┐
│ Result                      │
├─────────────────────────────┤
│ Success                     │
│     または                  │
│ Failure                     │
└─────────────────────────────┘
```

として扱う。

Failureの場合：

```text
Result
  ↓
Gyomu Error
  ↓
message / context / details / __cause__
```

という構造になる。

---

# 24. 基本的なError Flow

Infrastructureから上位層までの基本的な流れは以下。

```text
External Library
      │
      │ Exception
      ▼
Infrastructure
      │
      │ convert
      ▼
Gyomu Error
      │
      │ Result Failure
      ▼
Repository
      │
      ▼
Service
      │
      ▼
Application
```

---

# 25. 目指すError Handling

最終的には、以下の状態を目指す。

```text
外部ライブラリの詳細
        ↓
Infrastructureで吸収
        ↓
Gyomu Error
        ↓
Result
        ↓
上位層
```

上位層は、

```text
SQLAlchemyError
```

や、

```text
その他のInfrastructure固有Exception
```

を直接扱う必要がない。

---

# 26. 実装時のチェックリスト

新しいI/O処理を実装するときは、以下を確認する。

## Error

- [ ] 適切な既存Gyomu Error Typeがあるか
- [ ] 新しいError Typeが本当に必要か
- [ ] contextを設定する必要があるか
- [ ] detailsに診断情報を追加できるか
- [ ] 機密情報をdetailsへ入れていないか
- [ ] 元例外がある場合はraise ... from errorを使用しているか

## Result

- [ ] 予想可能なFailureをResultで返しているか
- [ ] 不要なException → Result変換をしていないか
- [ ] 下位層のResultを不要に変換していないか

## Boundary

- [ ] 外部ライブラリ固有Exceptionを上位層へ漏らしていないか
- [ ] Infrastructure境界で適切なGyomu Errorへ変換しているか

## Responsibility

- [ ] Factoryの責務が過剰になっていないか
- [ ] Session LifecycleをFactoryが管理していないか
- [ ] RepositoryがDB固有Exceptionを直接公開していないか

# 27. 今後の拡張

このError設計は、現在のDB Infrastructureだけに限定しない。

将来的に、

```text
Database
File
Network
AI
External API
Configuration
Authentication
Authorization
```

などのInfrastructureが追加された場合も、同じ原則を適用する。

ただし、実際に必要になるまではError階層や抽象化を増やさない。

> **必要な実例が発生した時点で、既存モデルとの整合性を確認しながら拡張する。**

# 28. 設計原則まとめ

Python版GyomuのError Handlingでは、以下を基本原則とする。

1. Gyomu Errorは`BaseError`を共通基底とする
1. `BaseError`は`Exception`を継承する
1. `message`は人間向けのエラー概要を表す
1. `context`は操作・発生箇所を示す
1. `context`はtracebackの代替ではない
1. `details`は診断用の追加構造化情報を示す
1. 元例外は独自`cause`属性ではなくPythonの`Exception.__cause__`を利用する
1. 元例外を保持するときは`raise ... from error`を使用する
1. 予想可能なFailureは`Result`で伝播する
1. すべてのExceptionを無条件に`Result`へ変換しない
1. 外部ライブラリ固有ExceptionはInfrastructure境界でGyomu Errorへ変換する
1. Error TypeはFailureの意味を表現する
1. 発生場所・操作はError Typeではなく`context`で表現する
1. Configuration Sourceに依存しないConfiguration Errorとして`ConfigError`を使用する
1. 不要なError Typeや抽象化を先行して追加しない
1. 新しいError Typeは、既存Typeでは意味を適切に表現できない場合にのみ追加する
1. Error設計は、Error Type / message / context / details / cause / tracebackの責務を分離する
