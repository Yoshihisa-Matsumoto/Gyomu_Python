# Gyomu-Python ディレクトリ構造・命名規則

## 1. 目的

Python版Gyomuにおけるソースコードのディレクトリ構造および命名規則を統一する。

特にInfrastructureについては、今後DB以外にもCSV、Archive、HTTP、FileSystemなどの外部リソースが追加されることを想定し、**技術的な接続先・データソースを第一階層とする構造**を採用する。

また、PythonではPythonの一般的な慣習を優先し、TypeScript版のcamelCase命名をそのまま移植しない。

---

# 2. Infrastructureのディレクトリ構造

## 2.1 基本方針

`gyomu_infra` 直下には、外部リソース・技術的な接続先を配置する。

基本形：

```text
gyomu_infra/
├── db/
├── csv/
├── archive/
├── http/
├── filesystem/
```

すべてを最初から作成する必要はなく、実際に必要になった段階で追加する。

### 第一階層の意味

| ディレクトリ  | 責務                                   |
| ------------- | -------------------------------------- |
| `db/`         | Database / SQLAlchemy / SQL Server関連 |
| `csv/`        | CSV関連                                |
| `archive/`    | Archive関連                            |
| `http/`       | HTTP / 外部API関連                     |
| `filesystem/` | File System関連                        |
| `gyomu/`      | 業務領域                               |

---

# 3. DB関連コード

DB関連のコードは、`gyomu_infra` 直下に分散させず、すべて `db/` 配下にまとめる。

```text
gyomu_infra/
└── db/
    ├── base.py
    │
    ├── error/
    │   └── database.py
    │
    ├── mapper/
    │   └── market_holiday.py
    │
    ├── model/
    │   └── market_holiday.py
    │
    └── repository/
        ├── market_holiday.py
        └── sqlalchemy_market_holiday.py
```

これにより、

```text
gyomu_infra/db/
```

を見ることでDB関連コードを把握できるようにする。

---

# 4. Infrastructure内部の分類

各Infrastructureの内部では、必要に応じて以下のような分類を使用する。

```text
db/
├── error/
├── mapper/
├── model/
└── repository/
```

ただし、すべてのInfrastructureで同じ構造を強制するわけではない。

例えばCSVでModelが不要なら、`model/`を作成しない。

**実際に必要な責務だけディレクトリを作る。**

---

# 5. Repository

Repositoryには、外部データソースへのアクセスを担当するコードを配置する。

DBの場合：

```text
db/
└── repository/
    ├── market_holiday.py
    └── sqlalchemy_market_holiday.py
```

現在は、

```python
class MarketHolidayRepository(Protocol):
    ...
```

と、

```python
class SqlAlchemyMarketHolidayRepository:
    ...
```

を配置している。

ただし、Repository Protocolについては将来的にSchema / Contract側へ移動する可能性がある。

この判断はBusinessCalendarなどの実装を進めながら、依存関係を確認して決定する。

---

# 6. Mapper

DB ModelとSchemaの変換を担当するMapperは、DB固有の処理であるため、

```text
db/
└── mapper/
```

に配置する。

例：

```text
db/
└── mapper/
    └── market_holiday.py
```

現在のMapperは、

```text
SQLAlchemy Model
        ↕
Pydantic Schema
```

を変換する。

DB以外のMapperが必要になった場合は、それぞれのInfrastructure配下に配置する。

例えば、

```text
db/mapper/
csv/mapper/
archive/mapper/
```

のようにする。

---

# 7. DB Error

DB固有のErrorは、

```text
db/error/
```

に配置する。

例：

```text
db/
└── error/
    └── database.py
```

一方、Gyomu全体で共有するErrorはInfrastructureに配置しない。

例えば、

```python
from gyomu_schema.error import GyomuIOError
```

のようなGyomu共通ErrorはSchema側で管理する。

基本的な責務分担は、

```text
gyomu_schema.error
    ↓
Gyomu全体で共有するError

gyomu_infra.db.error
    ↓
DB固有Error
```

とする。

---

# 8. Service

業務上利用するInfrastructure Serviceは、各業務領域ごとに配置する

```text
gyomu_infra/gyomu/<業務領域>
```

に配置する。

例えばBusinessCalendar：

```text
gyomu_infra/
└── gyomu/
    └── date
        └── business_calendar.py
```

BusinessCalendarはDBそのものではなく、

```text
BusinessCalendarService
        ↓
MarketHolidayRepository
        ↓
Database
```

という依存関係を持つため、`db/` 配下には配置しない。

つまり、

> DBはBusinessCalendarの実装詳細であり、BusinessCalendarそのものはDBではない

という考え方を採用する。

---

# 9. ServiceとRepositoryの責務

基本的な依存方向：

```text
Service
    ↓
Repository Protocol
    ↓
Infrastructure implementation
    ↓
External Resource
```

例えば：

```text
BusinessCalendarService
        ↓
MarketHolidayRepository
        ↓
SqlAlchemyMarketHolidayRepository
        ↓
SQL Server
```

ServiceはConstructor InjectionによってRepositoryを受け取る。

PythonではEffectのLayer / Contextを移植せず、

```text
Protocol
+
Constructor Injection
+
Result
+
Factory / Composition Root
+
pytest
```

によって依存関係を明確にする。

---

# 10. Test Directory

Testコードは、基本的に`src`の構造に対応させる。

例えば、

```text
packages/infra/
├── src/
│   └── gyomu_infra/
│       ├── db/
│       │   ├── mapper/
│       │   ├── model/
│       │   └── repository/
│       └── gyomu/
│
└── tests/
    ├── db/
    │   ├── mapper/
    │   └── repository/
    └── gyomu/
```

という構造にする。

これにより、

```text
src/gyomu_infra/db/repository/
```

のTestを探す場合、

```text
tests/db/repository/
```

を見ればよい。

---

# 11. `conftest.py`

共通Fixtureは、

```text
tests/conftest.py
```

に配置する。

例えばSQL Server Integration Test用のDB Engine Fixtureなど、複数のTestから利用するFixtureをここで管理する。

Infrastructure固有のFixtureが増えた場合は、必要に応じて対象ディレクトリに`conftest.py`を配置する。

---

# 12. Python命名規則

Python版Gyomuでは、Pythonの一般的な命名規則を優先する。

TypeScript版のcamelCaseをそのまま移植しない。

---

## 12.1 Class / Protocol

`PascalCase`を使用する。

```python
BusinessCalendar
BusinessCalendarService
MarketHolidayRepository
SqlAlchemyMarketHolidayRepository
```

Protocolであっても、名前に`Protocol`を付けない。

```python
class BusinessCalendar(Protocol):
    ...
```

とする。

以下のようにはしない。

```python
class BusinessCalendarProtocol(Protocol):
    ...
```

---

## 12.2 Method / Function

`snake_case`を使用する。

```python
is_business_day()
business_day()
get_holidays()
find_by_market()
```

TypeScript版：

```text
isBusinessDay
businessDay
getHolidays
findByMarket
```

Python版：

```text
is_business_day
business_day
get_holidays
find_by_market
```

---

## 12.3 Variables / Arguments

`snake_case`を使用する。

```python
target_date
day_offset
start_date
end_date
market
```

例えば、

```python
def is_business_day(
    self,
    target_date: date,
) -> Result[bool, GyomuIOError]:
    ...
```

とする。

---

## 12.4 Private Member

単一の先頭アンダースコアを使用する。

```python
_repository
_holidays
_session
```

例えば、

```python
self._repository
self._holidays
self._session
```

とする。

Pythonでは先頭`_`は、内部実装であることを示す慣習として利用する。

---

## 12.5 Constants

`UPPER_SNAKE_CASE`を使用する。

```python
GYOMU_COMMON_MAINDB_CONNECTION
```

---

# 13. Boolean Method

Booleanを返すメソッドは、意味に応じて以下のprefixを使用する。

```text
is_
has_
can_
```

例えば、

```python
is_business_day()
is_valid()
has_holiday()
can_process()
```

特に`is_`はPythonで一般的な命名規則として扱う。

---

# 14. Public / Private API

Public API：

```python
is_business_day()
business_day()
get_holidays()
```

Internal implementation：

```python
_calculate_business_day()
_is_holiday()
_load_holidays()
```

というように、外部へ公開するAPIには原則として先頭`_`を付けない。

内部実装には必要に応じて先頭`_`を付ける。

---

# 15. Date引数の命名

TS版では、

```typescript
getHolidays(from, to);
```

としていたが、Pythonでは`from`が予約語であるため使用しない。

Python版では、

```python
get_holidays(
    start_date: date,
    end_date: date,
)
```

を基本とする。

また、

```python
target_date
day_offset
```

など、意味を明確にした名前を使用する。

---

# 16. BusinessCalendarの命名

TS版：

```text
BusinessCalendar
isBusinessDay
businessDay
getHolidays
```

Python版：

```text
BusinessCalendar
is_business_day
business_day
get_holidays
```

Pythonでは、TS版との機械的な命名一致よりもPythonの慣習を優先する。

ただし、ドメイン上の名称そのものは可能な限りTS版・C#版・既存Python版と共通化する。

つまり、

> **ドメイン名はGyomu全体で揃え、プログラミング言語固有の命名規則は各言語に従う。**

---

# 17. Infrastructure第一階層の設計原則

今後Infrastructureが拡張された場合も、原則として、

```text
gyomu_infra/
├── db/
├── csv/
├── archive/
├── http/
├── filesystem/
└── gyomu/
```

という考え方を維持する。

第一階層では、

> 「何の技術・外部リソースを扱っているか」

を表現する。

その内部で、

```text
repository/
mapper/
model/
error/
```

などの技術的責務を分類する。

---

# 18. 今回の設計思想

Python版Gyomuでは、コードの分類について以下を基本原則とする。

```text
第一階層
    ↓
外部リソース・技術境界

第二階層以降

Infrastructureの業務領域コード
    ↓
Gyomuの業務領域

その業務領域内部
    ↓
必要な責務
```

例えばDBなら、

```text
db/
├── model/
├── mapper/
├── repository/
└── error/
```

となる。

これにより、Infrastructureが将来、

```text
DB
CSV
Archive
HTTP
FileSystem
```

などへ拡張されても、どのコードがどの外部リソースに依存しているかをディレクトリ構造から把握できるようにする。

---

# 19. 現時点の推奨構造

現時点では概ね以下を基準とする。

```text
packages/
└── infra/
    ├── src/
    │   └── gyomu_infra/
    │       ├── __init__.py
    │       ├── py.typed
    │       │
    │       ├── db/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   │
    │       │   ├── error/
    │       │   │   ├── __init__.py
    │       │   │   └── database.py
    │       │   │
    │       │   ├── mapper/
    │       │   │   ├── __init__.py
    │       │   │   └── market_holiday.py
    │       │   │
    │       │   ├── model/
    │       │   │   ├── __init__.py
    │       │   │   └── market_holiday.py
    │       │   │
    │       │   └── repository/
    │       │       ├── __init__.py
    │       │       ├── market_holiday.py
    │       │       └── sqlalchemy_market_holiday.py
    │       │
    │       └── gyomu/
    │           ├── __init__.py
    |           └── date/
    │               ├── market_holiday.py
    │               ├── business_calendar.py
    |               └── business_calendar_factory.py
    │
    └── tests/
        ├── conftest.py
        ├── db/
        │   ├── mapper/
        │   └── repository/
        └── gyomu/
            └── date/
```

今後、実際のコード量や依存関係が増えた場合には、この原則を維持した上で必要に応じて細分化する。

---

# 20. まとめ

Python版Gyomuでは、以下を基本ルールとする。

1. **Pythonの命名規則を優先する**
2. Class / Protocolは`PascalCase`
3. Function / Method / Variableは`snake_case`
4. Constantは`UPPER_SNAKE_CASE`
5. Private memberは`_name`
6. Protocol名に`Protocol`を付けない
7. `is_` / `has_` / `can_`をBoolean APIに使用する
8. Infrastructure第一階層は外部リソース・技術境界とする
9. DB関連コードは`gyomu_infra/db/`配下にまとめる
10. `model` / `mapper` / `repository` / `error`は各Infrastructure内部に配置する
11. Business Serviceは`gyomu_infra/gyomu/<業務領域コード>/`に配置する
12. Testディレクトリはsrc構造に対応させる
13. TS/C#/Pythonでドメイン名は可能な限り共通化する
14. ただし、各言語の命名規則は各言語の慣習に従う
15. Infrastructureの構造は、将来のCSV / Archive / HTTP / FileSystem等の追加を前提として設計する

このルールをPython版GyomuのInfrastructureおよび関連コードの基本的なディレクトリ・命名規約とする。
