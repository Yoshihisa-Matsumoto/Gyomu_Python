# AI Package — Future TODO

## 1. Generation Trace（将来）

### 目的

**Audit / Troubleshooting のために、1回のAI実行で何が起きたかを完全に追跡できるようにする。**

現在の `AiGenerationMetadata` は、評価・コスト把握に必要な集約情報を保持する。

一方、Audit / Troubleshooting では、

> 「このユーザー入力に対して、LLMが何を要求し、どのToolを呼び、何が返され、最終的に何を回答したのか」

という`実行履歴`そのものが必要になる。

### 将来想定するデータ

```text
AiGenerationTrace
├─ run_id
├─ conversation_id
├─ provider_response_id
│
├─ ModelRequest[]
├─ ModelResponse[]
├─ ToolCall[]
├─ ToolReturn[]
└─ ...
```

Pydantic AI / Provider 固有の情報も必要に応じて保持する。

特に、

- run_id
- conversation_id
- provider response ID

などを追跡可能にする。

### `AiGenerationMetadata` との違い

```text
AiGenerationMetadata
    ↓
評価・コスト・性能測定のための集約情報

AiGenerationTrace
    ↓
Audit / Troubleshooting のための実行履歴
```

したがって、**TraceをMetadataに詰め込むのではなく、別概念として扱う。**

### 現フェーズ

**未実装。**

現段階では `AiGenerationMetadata` に必要な Usage / Tool Call 情報までとし、詳細なRequest/Response履歴の保存は行わない。

---

## 2. Runtime Control（将来）

### 目的

**Tool Call の実行を動的に制御する。**

これは `AiToolCallGroup` などの「実行結果を記録する仕組み」とは目的が異なる。

```text
Tool Call Result
    ↓
「何が起きたか」を記録する

Runtime Control
    ↓
「次に何をしてよいか」を制御する
```

### 想定する仕組み

Tool実行前後でRuntime Stateを更新し、その状態を次のTool Callの判断に利用する。

```text
Tool Call
   ↓
prepare / args_validator
   ↓
Runtime State
   ↓
ToolFuncContext
   ↓
Tool Loop制御
```

例えば将来的に、

- 特定のToolが呼ばれたら以降のTool Callを禁止
- 特定のToolを一度だけ許可
- Toolの実行結果によって次のToolを制御
- Tool実行回数・状態をRuntime Stateとして管理

といった制御が必要になった場合に導入する。

### Pydantic AIとの対応

現時点では、Pydantic AIの

- `prepare`
- `args_validator`
- `RunContext` / `ToolFuncContext`

などを利用する可能性が高い。

ただし、**実際にRuntime Stateが必要になる要件が発生するまで導入しない。**

### 現フェーズ

**未実装。**

現在の `ToolLoopPolicyMaxSteps` など、Agent / `UsageLimits` で実現できる範囲に留める。

---

## 3. Tool Loop Policy（保留）

現在：

```text
ToolLoopPolicyMaxSteps
    ↓
Pydantic AI UsageLimits(tool_calls_limit)
```

その他：

```text
ToolLoopPolicyUntilFinished
ToolLoopPolicyUntilToolCalled
```

については、現時点では追加実装しない。

### UntilFinished

現在の実装では、実質的に

```text
「特別な制限をしない」
```

と同じ扱い。

### UntilToolCalled

今後、Tool Call / Tool Return のRuntime Controlが必要になった段階で再検討する。

特に、

> 「Tool Callされたことを検知したあと、次のLLM/Tool処理をどう終了させるか」

についてPydantic AI側の仕組みを確認した上で設計する。

したがって、現段階では無理に実装しない。
