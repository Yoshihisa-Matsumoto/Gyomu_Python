# Python Analysis ロードマップ案

## Phase 1 — Module / Declaration / Semantic Analysis

### ゴール

**1ファイルを読み込み、そのファイルの構造を`ModuleAnalysis`として正確に表現できるようにする。**

対象：

```
Python Source
    ↓
Griffe
    ↓
Module
 ├── ImportAnalysis
 └── SymbolAnalysis
       ├── Variable
       ├── Class
       └── Function
```

この段階ではProject解析は行わない。

---

### 1. Module Analysis

```python
class ModuleAnalysis(BaseModel):
    path: str
    name: str
    docstring: DocstringAnalysis | None
    imports: tuple[ImportAnalysis, ...]
    symbols: tuple[SymbolAnalysis, ...]
```

解析対象：

- module name
- file path
- module docstring
- imports
- top-level symbols

---

### 2. Import Analysis

```python
class ImportAnalysis(BaseModel):
    module: str
    imported_name: str | None
    alias: str | None
    is_relative: bool
    relative_level: int
```

対象：

```python
import foo
import foo.bar
import foo as f

from foo import Bar
from foo import Bar as B

from .foo import Bar
from ..foo import Bar
```

ここではまだProject全体のDependency Graphは作らない。

ただし、**後のDependencyAnalysisに使えるSemantic情報は可能な限り抽出する。**

---

### 3. Symbol Analysis

まずTop-level Symbolを抽出。

```
Variable
Class
Function
```

`Method`はClass内部のmemberとして扱う。

ここで重要なのは、今回決めた、

> Symbol = 外部から直接参照される可能性のあるModule-level declaration

という考え方。

したがって、

```python
class User:
    name: str

    def save(self):
        ...
```

なら、

```
Module
└── Symbol
    └── Class User
         ├── Variable name
         └── Method save
```

とする。

`name`や`save`自体をModuleの`symbols`には入れない。

---

### 4. Visibility

Pythonでは`export`ではなく、

```
_foo
foo
__foo
```

などの命名規則を基準にする。

初期ルール：

```
先頭 "_" → private
それ以外 → public
```

ただし、

```python
__foo__
```

のようなdunderは単純なprivate扱いとは意味が違うため、`Visibility`だけでなく、将来的にSymbolの性質として別途扱える余地を残す。

Phase 1では過度に複雑化しない。

---

## Phase 1-B — Declaration / Type Analysis

Phase 1の中で、Symbolを認識したらその内容まで解析する。

### Variable

```python
class VariableAnalysis(...):
    kind: Literal[SymbolKind.VARIABLE]
    type: TypeAnalysis | None
    value_source: str | None
    dependencies: tuple[DependencyAnalysis, ...]
```

対象：

```python
count: int = 10
name = "foo"
user: User
```

---

### Class

```python
class ClassAnalysis(...):
    kind: Literal[SymbolKind.CLASS]

    bases: tuple[TypeAnalysis, ...]
    variables: tuple[ClassVariableAnalysis, ...]
    methods: tuple[MethodAnalysis, ...]
    dependencies: tuple[DependencyAnalysis, ...]
```

ここはPython版ではかなり重要。

ClassはTypeScriptよりも責務が広いため、

```
Class
├── bases
├── class variables
├── instance-related declarations
├── methods
├── decorators
├── docstring
└── dependencies
```

を解析する。

---

### Method

```python
class MethodAnalysis(BaseModel):
    name: str
    visibility: Visibility
    location: SourceLocation
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]

    parameters: tuple[ParameterAnalysis, ...]
    return_type: TypeAnalysis | None

    dependencies: tuple[DependencyAnalysis, ...]
```

Class専用に限定する。

ただし将来、

```
Class Method
Static Method
Instance Method
Property
Callable object
```

などを区別できるようにする。

---

### Function

```python
class FunctionAnalysis(SymbolAnalysisBase):
    kind: Literal[SymbolKind.FUNCTION]

    parameters: tuple[ParameterAnalysis, ...]
    return_type: TypeAnalysis | None
    dependencies: tuple[DependencyAnalysis, ...]
```

---

## Phase 1-C — DocString Analysis

ここもPhase 1に入れます。

今回の目的がDocString生成だからです。

解析対象：

- raw docstring
- normalized value
- location
- style
- sections

現在はGoogle形式。

```python
class DocstringAnalysis(BaseModel):
    value: str
    style: DocstringStyle
    sections: tuple[DocstringSection, ...]
    location: SourceLocation
```

将来：

```python
class DocstringStyle(StrEnum):
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
```

などを追加可能にする。

** 実際の解析ロジックはGoogle形式から開始。**

---

### 独自Section

Gyomuでは、

```
Gyomu Context
```

のような独自セクションを持つ予定なので、

```
標準Google sections
+
Gyomu独自sections
```

を扱える設計にする。

ここは`docstring-parser`に全面依存するのではなく、

```
Docstring
    ↓
Google parser
    ↓
Gyomu custom section parser
```

のような構成を想定する。

---

## Phase 1-D — Decorator Analysis

共通モデルとして解析する。

対象：

```
@classmethod
@staticmethod
@property
@field_validator(...)
@computed_field
@custom_decorator(...)
```

など。

最初から特定Decoratorを大量にハードコードするのではなく、

```python
class DecoratorAnalysis(BaseModel):
    name: str
    arguments: ...
```

のような一般形を作る。

その上でSemantic Analyzer側で、

```
classmethod
staticmethod
property
pydantic.*
```

などを認識する。

---

## Phase 1-E — Pydantic Analysis

これはPython版ではPhase 1に含めてよいと思います。

今回のDocString生成対象としてPydanticモデルは非常に重要だからです。

### Pydantic Model

```
Class
  ↓
bases
  ↓
BaseModel
```

を検出。

例えば、

```python
class User(BaseModel):
```

なら、

```
ClassAnalysis
    semantic:
        is_pydantic_model = true
```

のような情報を持たせる。

ただし、ここは今の段階で無理に`PydanticModelAnalysis`という別の永続モデルにする必要はありません。

---

### Pydantic Field

```python
id: int = Field(
    description="Primary identifier"
)
```

から、

```
annotation
    int

value
    ExprCall
       Field(...)
```

を解析。

ここから、

```
PydanticField
├── annotation
├── default
├── description
├── alias
├── ...
```

などを将来的に抽出できるようにする。

---

## Phase 1-F — Dependency Analysis

ここが今回のTS版との大きな違いです。

**Phase 1から可能な範囲でやる。**

ただし「Graph」はまだ作らない。

Symbol単位で、

```python
dependencies: tuple[DependencyAnalysis, ...]
```

を持たせる。

---

### Local dependency

```python
class LocalFileDependency(BaseModel):
    scope: Literal["local-file"]
    local_symbol_name: str
```

例えば、

```python
class User:
    def create(self):
        return User()
```

なら、

```
create
↓
User
```

を検出する。

---

### Imported dependency

```python
class ImportedSymbolDependency(BaseModel):
scope: Literal["import"]
local_symbol_name: str
```

例えば、

```python
from pydantic import BaseModel

class User(BaseModel):
...
```

なら、

```
User
↓
BaseModel
↓
import
```

とする。

---

### Dependency Source

TS版の設計を踏襲して、

```python
class DependencySource(BaseModel):
member_path: tuple[str, ...]
```

を持たせる。

例えば、

```
user.save()
```

なら、

```python
source.member_path = ("save",)
```

のような形。

これによって、

```
User
└── save
```

のような依存元の詳細を失わない。

---

## Phase 1-G — Type Analysis

型はPhase 1で扱う。

対象：

```python
int
str
User

list[User]
dict[str, User]

User | None

Callable[[str], User]

TypeVar
Generic
Annotated
Literal
```

など。

最初からすべてのPython typing仕様を完全にモデル化する必要はない。

まず、

```
Name
Attribute
Subscript
Union
Callable
Literal
```

などの基本構造を表現できるモデルを作る。

---

## Phase 1の完成条件

最終的に、

```
sample.py
```

を渡すと、

```
ModuleAnalysis
│
├── path
├── name
├── docstring
│
├── imports
│ ├── pydantic.BaseModel
│ └── pydantic.Field
│
└── symbols
│
└── User
├── visibility
├── location
├── docstring
├── decorators
├── bases
│
├── variables
│ └── id
│ ├── type: int
│ └── Pydantic Field
│
├── methods
│ └── create
│ ├── decorator: classmethod
│ ├── parameters
│ ├── return_type: User
│ ├── docstring
│ └── dependencies
│
└── dependencies
```

まで構築できることをゴールにする。

---

## Phase 2 — DocString Semantic Analysis

TS版のPhase 3に相当。

ただしPython版ではPhase 1で**最低限のDocString取得を行うので、その拡張フェーズ**とする。

対象：

- Google style
- summary
- Args
- Returns
- Raises
- Examples
- Notes
- Attributes
- Gyomu Context
- その他Custom Section

さらに、

```
section location
```

まで解析する。

ここで、

```
DocString全体
↓
Section
↓
Section Location
```

を持てるようにする。

これが将来のSafe Updateに重要。

---

## Phase 3 — Safe DocString Update

TS版のPhase 4に相当。

ここはかなり重要なので、**LLM生成より先に実装する**のを推奨します。

ゴール：

> 既存DocStringを壊さず、指定部分だけ安全に変更できる。

例えば、

```
summary
Args
Returns
Raises
Gyomu Context
```

を個別に更新できるようにする。

```
基本原則：

既存DocString
↓
解析
↓
対象Sectionだけ変更
↓
元SourceへInjection
```

既存の、

```
# comment

空行
その他のコード
別のDocString
```

には触れない。

---

## Phase 4 — Signature / Type Analysis 強化

TS版Phase 6相当。

Phase 1の基本Type Analysisを拡張する。

対象：

- nested generic
- union
- Optional
- Callable
- TypeVar
- Generic
- Protocol
- Annotated
- Literal
- overload
- async
- positional-only
- keyword-only

など。

ここで、

```python
ParameterAnalysis
```

を充実させる。

```
Function
├── parameters
│ ├── kind
│ ├── type
│ └── default
└── return_type
```

を完全に扱えるようにする。

---

## Phase 5 — Body / Semantic Analysis

これは今回の「Phase 1ではないBody Analysisを後回し」という方針に対応します。

ここから関数本体を深く見る。

対象：

- return
- call
- attribute access
- variable reference
- assignment
- condition
- loop
- exception
- await
- yield
- context manager

など。

例えば、

```python
def create(name: str) -> User:
user = User(name=name)
return user
```

から、

```
create
├── User(...)
├── user
└── return User
```

まで理解する。

ここで初めて、

**「このFunctionは実際に何をしているのか」**

というSemantic Analysisに踏み込む。

これはDocString品質を大きく上げられる可能性があります。

---

## Phase 6 — Dependency Graph

TS版Phase 10に相当。

Phase 1では、

```
Symbol
└── dependencies
```

まで。

Phase 6で、

```
Module
↓
Module
↓
Module
```

というProject-level Graphに発展させる。

ここで初めてProjectを導入。

```
Project
├── modules
├── dependency graph
└── module hierarchy
```

を解析する。

---

## Phase 7 — Complexity Analysis

TS版Phase 8相当。

対象：

- nesting
- branching
- function length
- class size
- type complexity
- generic depth
- inheritance depth
- method count
- dependency count
- async boundary

など。

---

## Phase 8 — Documentation Scoring

TS版Phase 9相当。

ただしPythonでは、

```
public symbol
class
Pydantic model
API function
complexity
dependency
```

などを考慮して、

```
DocumentationPriority
```

を算出する。

例えば、

```
User
public class
Pydantic model
8 methods
5 dependencies
↓
High documentation priority
```

のような判断。

---

## Phase 9 — Project Analysis

最後にProjectを導入する。

```
ProjectAnalysis
├── packages
├── modules
├── module hierarchy
├── dependencies
└── symbols
```

ここから、

- README生成
- Concept生成
- Architecture解析
- Module relationship
- package dependency
- circular dependency
- architecture violation

などにつなげる。
