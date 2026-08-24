# Python版Gyomu — DocString / Knowledge記述規約

## 1. 基本方針

Python版Gyomuでは、**Google Style DocStringを基本形式として採用する**。

DocStringは、単なるAPIドキュメントではなく、将来的にコードからKnowledgeを生成する際の情報源としても利用する。

そのため、

> **人間が読むための説明と、将来機械的に抽出する設計知識の両方を意識してDocStringを記述する。**

---

## 2. 標準形式はGoogle Style

基本的なDocStringにはGoogle Styleを使用する。

代表的なセクション：

- `Args:`
- `Returns:`
- `Raises:`
- `Attributes:`
- `Examples:`

例：

```python
def find_by_market(
    market: str,
) -> Result[list[MarketHoliday], GyomuIOError]:
    """Find holidays for a market.

    Args:
        market: Market identifier.

    Returns:
        Holidays registered for the specified market.

    Raises:
        DatabaseError: If a database access error occurs.
    """
```

---

## 3. API情報と設計知識を分離する

DocStringには、性質の異なる2種類の情報がある。

### API情報

コードの構造から比較的機械的に生成・更新できる情報。

```python
Args:
Returns:
Raises:
Attributes:
```

### 設計知識

単純な型情報やシグネチャからは判断できない、設計上の意味やルール。

```python
Gyomu Context:
```

などのGyomu固有セクションに記述する。

---

## 4. 自動生成される情報に設計知識を依存させない

将来的にDocStringの一部を自動生成する可能性がある。

例えば、

```python
Args:
Returns:
Raises:
```

などは、関数シグネチャやASTから生成できる。

そのため、

> **自動生成によって変更される可能性のある場所だけに、重要な設計知識を記述してはいけない。**

例えば、単なる引数説明を超えた設計上の意味を、

```python
Args:
    value: ...
```

だけに記述することは避ける。

---

## 5. Gyomu固有の設計知識には独自セクションを使用する

Google Styleの標準セクションでは表現しにくい、Gyomu固有の設計知識については独自セクションを使用する。

現在の標準となる独自セクション：

```python
Gyomu Context:
```

これは単なる補足情報ではなく、

> **Gyomuにおける設計上の意味・ルールを記述するためのセクション**

とする。

---

## 6. `Note`を設計知識の格納場所として使用しない

`Note`は一般的な補足説明として扱う。

したがって、

```python
Note:
    Important design rule ...
```

のように、Knowledge生成時に保持したい重要な設計知識をNoteへ記述することは避ける。

設計知識については、意味を明確に識別できるGyomu固有セクションを使用する。

```python
Gyomu Context:
    ...
```

---

## 7. 独自セクションには明確な意味を持たせる

独自セクションを追加する場合は、単に「好きな名前のコメント欄」を増やすのではなく、

> **そのセクションから何のKnowledgeを抽出できるのか**

を明確にする。

例えば、

```python
Gyomu Context:
```

であれば、

```python
Gyomu固有の設計・意味論
```

を記述する。

将来的には必要に応じて、

```python
Gyomu Contract:
Gyomu Design:
```

などを検討できる。

ただし、**必要になるまで独自セクションは増やさない。**

---

## 8. ClassとMethodのDocStringの役割を分ける

Classに設計上の重要な情報がある場合は、Class DocStringを主要な情報源とする。

```python
class Example:
    """Example implementation.


    Gyomu Context:
        ...
    """


    def __init__(self, ...) -> None:
        """Initialize Example."""
```

MethodのDocStringでは、そのMethod自身に固有のAPI情報を記述する。

これにより、

```
Class DocString
    ↓
クラス全体の設計・意味論


Method DocString
    ↓
個々の操作のAPI情報
```

という構造を作る。

---

## 9. `__init__`のDocStringは必要最小限にする

Class DocStringに十分な情報がある場合、`__init__`で同じ説明を繰り返さない。

例えば、

```python
def __init__(self, ...) -> None:
    """Initialize Example."""
```

程度でよい。

特に、将来的にDocString自動生成の対象になる部分では、**設計知識を重複して記述しない。**

---

## 10. DocStringはKnowledge解析可能な構造を意識する

将来的に、

```
Python Source
      ↓
AST Analysis
      ↓
DocString Analysis
      ↓
Knowledge
```

という処理を行う可能性がある。

そのため、重要な情報を文章の中に無秩序に埋め込むのではなく、

```python
Args:
    ...


Returns:
    ...


Raises:
    ...


Gyomu Context:
    ...
```

のように、**意味のあるセクションに分けて記述する。**

---

## 11. 「説明」より「意味」を優先する

DocStringを書く際には、単にコードを言い換えるだけの説明ではなく、

> **そのコード・引数・戻り値・例外が、Gyomuにおいて何を意味するのか**

を必要に応じて記述する。

例えば、

```python
context: str | None
```

という型だけでは、

```
文字列またはNone
```

しか分からない。

その値が設計上どういう意味を持つかが重要であれば、それをDocStringの適切なセクションに記述する。

---

## 12. DocStringは「コードから失われる情報」を補う

ASTから取得できる情報：

- 名前
- 型
- 引数
- 戻り値
- 継承関係
- Decorator

などだけでは、設計上の意図までは分からない。

そのためDocStringでは、

```
なぜ存在するのか
何を意味するのか
どういうルールで使うのか
何を保証するのか
```

といった、**コード構造だけでは取得できない情報を補完する。**

これらは将来的なKnowledge生成において特に重要な情報となる。

---

## 13. BaseErrorはこの規約の一例

例えば今回のBaseErrorでは、

```python
Args:
    context:
    details:


Attributes:
    context:
    details:


Gyomu Context:
    contextの設計上の意味
    detailsの設計上の意味
    ...
```

と記述する。

ここで重要なのは、

> `context`や`details`をどう設計するか

ではなく、

> **標準API情報とGyomu固有の設計知識を分離して記述する**

というDocString上の考え方である。

---

## 14. 最終原則

Python版GyomuのDocStringについて、以下を基本原則とする。

1. **Google Style DocStringを基本形式とする**
1. 標準的なAPI情報は`Args` / `Returns` / `Raises` / `Attributes`などに記述する
1. **API情報と設計知識を分離する**
1. 自動生成・更新される可能性があるセクションだけに重要な設計知識を依存させない
1. Gyomu固有の設計知識には`Gyomu ...`形式の独自セクションを使用する
1. `Note`を重要な設計知識の格納場所として使用しない
1. ClassとMethodでDocStringの責務を分ける
1. `__init__`などの自動生成されやすいDocStringは必要最小限にする
1. **DocStringを将来的なKnowledge生成の入力情報として扱う**
1. ASTだけでは取得できない「意味・意図・ルール・契約」をDocStringで補完する
