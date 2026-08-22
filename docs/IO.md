# Gyomu-Python：DataFrame / Data Processing方針

## 1. 基本方針

Python版Gyomuは、C#/TS版の単純な移植ではなく、**Python固有のデータ処理エコシステムを活用できる設計**を目指す。

特に以下を意識する。

- Pydanticによる業務Recordの型・Validation
- returns によるResult型
- IteratorによるRecord単位のStreaming処理
- Polars / pandasによるDataFrameベースの集合処理
- 将来的なPyArrow / DuckDBとの連携

ただし、**Gyomu自体をpandas/Polarsのラッパーにはしない。**

---

## 2. Record-oriented と Data-oriented を分離する

Python版Gyomuでは、データ処理を大きく2つのモデルとして考える。

### Record-oriented

```text
Data Source
    ↓
CsvReader[T]
    ↓
Iterator[Result[T, E]]
    ↓
Business Logic
```

特徴：

- Pydantic Schemaによる型付け
- 1レコード単位のValidation
- Resultによるエラー処理
- IteratorによるStreaming
- 大量データでも全件をメモリに載せなくてよい
- 業務ロジックとの相性がよい

現在設計しているCSV Readerはこちらを中心にする。

### Data-oriented

```text
Data Source
    ↓
Polars / pandas
    ↓
DataFrame
    ↓
filter / join / group_by / aggregate
    ↓
DataFrame
```

特徴：

- データ集合全体を扱う
- 列単位の高速処理
- 集計・JOIN・ソートなどに強い
- 大量データの変換・分析に向く
- PolarsではLazy APIによるQuery Optimizationも利用できる

この2つを無理に同じ抽象化にしない。

---

## 3. PydanticとPolarsの役割を分ける

基本的には、

```text
Pydantic
    ↓
「1件の業務データは何か」
```

```text
Polars
    ↓
「大量の業務データをどう処理するか」
```

と考える。

つまり、

- Pydantic = Recordの型・制約
- Result = 処理結果・Failure
- Iterator = Record Stream
- Polars = DataFrame / Data Processing
- DuckDB = Analytical Query

という役割分担を基本とする。

---

## 4. pandasについて

pandasはPythonのデータ分析における非常に重要な標準的ライブラリであり、以下の理由から無視はしない。

- 非常に成熟している
- エコシステムが巨大
- Excel / NumPy / Jupyter / 機械学習などとの連携が強い
- 既存Pythonコードとの互換性が高い

ただし、Gyomuのコア設計にpandasを直接組み込むことは現時点では急がない。

**pandasを使いたいユーザーを排除しない設計** を意識する程度に留める。

---

## 5. Polarsを強く意識する

Python版Gyomuでは、Data Processing層についてはPolarsを第一候補として意識する。

理由：

- Rust実装
- 並列処理
- 高速なDataFrame処理
- メモリ効率
- Lazy API
- CSV / Parquetなどの高速I/O
- Arrowとの親和性
- 大量データ処理との相性
- 現在検討しているI/O → TransformationというGyomuの方向性との親和性

ただし、**現時点でGyomuの必須依存にはしない。**

---

## 6. StreamingとDataFrameは別概念

重要な設計上の注意点。

```text
Iterator[Result[T, E]]
```

と

```text
Polars DataFrame
```

は同じ「大量データ処理」でも異なる抽象化。

### Streaming

```text
CSV
 ↓
Record
 ↓
Record
 ↓
Record
 ↓
Record
```

- メモリ使用量を抑えられる
- 1件ごとにValidation可能
- 業務処理と相性がよい

### DataFrame

```text
CSV
 ↓
DataFrame
 ↓
Vectorized Processing
 ↓
DataFrame
```

- 集計・JOIN・変換に強い
- データ集合全体を効率よく処理する

### Polars Lazy

```text
Data Source
 ↓
Logical Plan
 ↓
Optimization
 ↓
Execution
```

これはさらに別のモデル。

したがって、「**Polarsを使う＝GyomuのStreaming**」とは考えない。

---

## 7. 将来的なData Processingエコシステム

Pythonでは、将来的に以下の組み合わせも考慮する。

```text
             Data Processing
                    │
        ┌───────────┼───────────┐
        │           │           │
      pandas      Polars      DuckDB
        │           │           │
        └───────────┼───────────┘
                    │
                 PyArrow
```

特にPyArrowは、

- DataFrame
- Parquet
- Columnar Data
- pandas
- Polars
- DuckDB

などをつなぐ基盤として意識しておく。

---

## 8. 現在のCSV設計への影響

現在検討している、

```python
CsvReader[T]
CsvWriter[T]
```

というGenericな設計は、そのまま進める。

特に、

```text
CsvReader[T]
    ↓
Iterator[Result[T, E]]
```

という方向は維持する。

ただし、将来的にDataFrame処理を追加できる余地を残す。

概念的には将来的に、

```text
CsvReader
 ├── records()
 │     └── Iterator[Result[T, E]]
 │
 └── dataframe()
       └── Polars DataFrame
```

のような異なる入口を持てる可能性がある。

**ただし、現段階でこのAPIを確定・実装する必要はない。**

---

## 9. 今後の設計で避けること

### 避ける1：すべてをPydantic Recordにする

大量データの集計・変換まで、

```text
1,000,000 records
 ↓
Pydantic model × 1,000,000
 ↓
Python loop
```

とすると、DataFrameライブラリの優位性を失う可能性がある。

### 避ける2：すべてをDataFrameにする

逆に、業務処理までDataFrameに寄せると、

- 型の意味が弱くなる
- Validationの責務が曖昧になる
- 業務ロジックがDataFrame操作に埋没する

可能性がある。

### 避ける3：GyomuをPolars wrapperにする

GyomuはPolarsそのものではなく、

> **業務データを安全にI/O・Validation・Transformationするための基盤**

であり、Polarsはその中で利用できるData Processing engineの一つ、と位置付ける。

---

## 10. 現時点でのGyomu-Pythonの方向性

最終的には以下を目指す。

```text
                         Gyomu-Python
                              │
              ┌───────────────┴───────────────┐
              │                               │
       Record-oriented                  Data-oriented
              │                               │
          Pydantic                         Polars
              │                            pandas
           Result                          DuckDB
              │                               │
         Iterator                         DataFrame
              │                               │
              └───────────────┬───────────────┘
                              │
                         Business Logic
```

つまり、

> **C#/TS版で培った「型安全な業務データ処理」を維持しつつ、Python版では「DataFrameによる大量データ処理」というPython固有の強みを追加する。**

これが今回の基本方針。
