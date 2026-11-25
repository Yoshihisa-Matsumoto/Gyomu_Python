# Python Gyomu：LSPによるリネームの調査結果

## 1. 背景と目的

Python GyomuのHelper Inventoryにおいて、既存Helper関数が不要になった可能性のあるケースをDelete Candidateとして検出する。

Delete Candidateは、対応する対象クラスが存在しなくなった場合や、Helper生成対象としての適格性を失った場合などを指す。

既存Helper関数がほかの箇所から参照されている可能性があるため、無条件に削除してはならない。

今回、将来のリファクタリング機能を検討するため、Language Server Protocol（LSP）を利用したシンボルのリネームについて調査した。

## 2. Delete Candidateの当面の方針

**Delete Candidateを検出しても、自動的な削除・リネームは行わない。**

検出した場合は、対象の関数名とファイル名をユーザーに表示する。必要に応じて、ユーザーが手動でリネームなどを行う。

この方針の理由は以下のとおり。

- Delete Candidateが大量に発生するとは想定していない。
- 一度ユーザーがリネームなどで対応すれば、同じ候補が継続的に発生する可能性は低い。
- 参照関係を確認せずに自動削除・リネームするリスクに対して、自動化のメリットが小さい。

したがって、Delete Candidate対応のためだけに、現時点でLSPによるリネーム機能を実装する必要はない。

## 3. LSPによるリネームの基本構造

### 3.1 LSPとは

Language Server Protocol（LSP）は、エディターなどの開発ツールと、プログラミング言語を解析するLanguage Serverとの通信仕様である。

LSP自体がPythonなどのコードを解析するわけではない。実際のシンボル解決やリネーム候補の生成は、Language Serverが担当する。

主な役割は以下のとおり。

- **LSPクライアント**：要求を送信し、応答を受信する。ドキュメント状態などを管理する。
- **LSPサーバー**：コードを解析し、要求に対応する結果を返す。
- **Gyomu**：変更対象を判断し、変更案を検査・適用し、必要な品質検証を実行する。

VS CodeはLSPクライアントとして動作し、Python向けにはPyrightを基盤とするPylanceなどが利用される。

### 3.2 リネーム要求の流れ

たとえば、`create_test_func` を `create_test_func_legacy` に変更する場合、概念的には以下の処理が必要になる。

1. 対象ファイルとシンボルの位置を特定する。
2. Language Serverに必要なドキュメント情報を同期する。
3. 対応している場合、`textDocument/prepareRename` で事前確認する。
4. `textDocument/rename` を送信する。
5. `WorkspaceEdit` などの応答を受け取る。
6. 変更対象のファイルと編集内容を検査する。
7. 変更案を適用する。
8. 必要に応じてmypy、Ruff、pytestで検証する。

`textDocument/prepareRename` は必須ではなく、サーバーの対応状況に依存する。

`WorkspaceEdit` は変更案を表す。LSPサーバーが変更案を返すことと、実際にファイルへ適用することは別の責務である。

### 3.3 安全性に関する注意点

LSPを利用しても、すべての参照を完全に検出できるとは限らない。

特に注意が必要なケースは以下のとおり。

- 未保存の編集内容と、ディスク上のファイルの不一致
- 動的な属性アクセスやリフレクション
- 文字列による関数名の参照
- 外部設定ファイルや別リポジトリからの参照
- 変更案を受け取った後のファイル更新や競合

Gyomuから直接LSPを利用する場合は、変更案を無条件に適用せず、対象ファイル・編集内容・ファイル状態などを検査する必要がある。

## 4. GyomuからLSPを利用する方式

将来的な実現方式として、以下の3つを検討した。

### 4.1 VS Codeにリネームを任せる

ユーザーがVS Code上でRename Symbolを実行する。

- 実装コストが低い。
- LSPクライアントや変更適用処理をGyomu側で実装する必要がない。
- 自動ワークフローとの統合には制約がある。

### 4.2 Gyomuが直接LSPクライアントになる

GyomuがLanguage Serverを起動し、LSP要求を直接送信する。

- 自動化ワークフローに統合しやすい。
- VS Codeへの依存を減らせる。
- サーバーの起動・初期化、JSON-RPC通信、ドキュメント同期、位置情報の変換、`WorkspaceEdit`の検査・適用、エラー処理などが必要になる。

ただし、JSON-RPCやLSP型をすべて自作する必要はない。既存のクライアントライブラリを利用できる。

### 4.3 Gyomu独自の静的解析で変更する

Gyomuが持つASTやGriffeなどの解析情報を活用し、参照箇所を特定して変更する。

- 既存の解析基盤を活用できる。
- LSPサーバーへの依存を避けられる。
- シンボルの参照解決、編集範囲の特定、動的参照への対応などをGyomu自身が設計する必要がある。

単純な文字列置換では、無関係な文字列の変更や、参照箇所の更新漏れが発生する可能性がある。

## 5. LSPクライアントのパッケージ調査

### 5.1 Python

#### `lsp-client`

- LSPクライアントとしてのAPIや型付きのインターフェースが候補になった。
- しかし、メンテナンス状況を踏まえ、候補から除外する。

#### `pygls` + `lsprotocol`

- `pygls`：LSP通信を扱うためのライブラリ。
- `lsprotocol`：LSPの仕様に基づく型定義を提供するライブラリ。
- 型定義と通信処理を再利用できる可能性がある。
- `pygls` はLanguage Serverの実装も主要な用途としているため、Gyomuから外部Language Serverを利用する場合の適合性を確認する必要がある。

参考：
- https://github.com/openlawlibrary/pygls
- https://github.com/microsoft/lsprotocol

### 5.2 TypeScript

LSP処理をTypeScriptで実装することにも合理性がある。

主な利点は以下のとおり。

- LSPのNode.js向けライブラリ群を利用できる。
- TypeScriptの型システムを要求・応答モデルに活用できる。
- Node.jsの子プロセス管理やストリーム処理と統合できる。
- 将来的にTS版・Python版Gyomuで共通のLSPブリッジを利用できる可能性がある。

ただし、TypeScriptの型定義だけでは、実行時に受け取ったJSONの妥当性は保証されない。また、TypeScriptを使うこと自体がリネームの解析精度を高めるわけではない。

#### Microsoft公式のLSPライブラリ群

第一候補となる基盤。

- `vscode-jsonrpc`：JSON-RPC通信
- `vscode-languageserver-protocol`：LSPのプロトコル定義
- `vscode-languageserver-types`：LSPのデータ型
- `vscode-languageclient`：VS Code拡張機能向けのクライアント

GyomuがVS Codeの外で動作する場合、`vscode-languageclient`をそのまま利用できるとは限らない。JSON-RPCとLSPプロトコルのライブラリを組み合わせる構成も検討する。

参考：
- https://github.com/microsoft/vscode-languageserver-node

#### `ts-lsp-client`

- 独立したLSPクライアントとして候補に挙がった。
- メンテナンス状況を踏まえ、候補から除外する。

#### `lspeasy`

- LSPクライアントAPI、JSON-RPC通信、スキーマ検証などを提供するSDK。
- 比較的新しい候補であり、保守状況、リリースの安定性、リネーム対応の範囲などを確認する必要がある。

参考：
- https://github.com/pradeepmouli/lspeasy

## 6. TS版・Python版のどちらでLSP処理を実装するか

**現時点では決定しない。**

将来、実際のRenameユースケースが現実的になった段階で、改めて判断する。

その際は、以下の点を比較する。

- TS版・Python版で共通の機能として提供する価値があるか。
- TypeScript製のLSPブリッジを別プロセスとして動作させるメリットがあるか。
- Python版にネイティブのLSPクライアントを用意する方が単純ではないか。
- 既存のLanguage ServerとLSPクライアントライブラリの保守状況・対応機能は十分か。
- `WorkspaceEdit`の安全な適用や、競合・失敗への対処をどの層が担うか。

TypeScriptを共通基盤にする案は有力だが、Python版から利用するためにプロセス間通信が増える点も考慮する。

## 7. 将来の設計方針

将来的にLSPによるリファクタリング機能を実装する場合、以下の責務を分離することを検討する。

- **Gyomuの業務ロジック**：変更対象と変更後の名前を判断する。
- **LSPアダプター**：Gyomu内部のモデルとLSPの型を相互変換する。
- **LSPクライアント**：JSON-RPC通信、LSP要求・応答、ドキュメント同期を担当する。
- **変更適用処理**：`WorkspaceEdit`の検査・適用、競合検出、失敗時の処理を担当する。
- **品質検証**：mypy、Ruff、pytestなどを実行する。

LSPライブラリを変更しても、Helper Inventoryやワークフローへの影響を抑えられる構成が望ましい。

## 8. 今後の作業

今回のLSP調査はここで終了する。現時点ではコードを書かず、LSP関連の依存パッケージも追加しない。

Delete Candidateは、対象の関数名・ファイル名を表示するだけとし、自動削除・自動リネームは行わない。

次は、Helper InventoryのUpdate側の分析へ進む。

まず既存の実装と呼び出し関係を確認し、以下を順に検討する。

1. Update Candidateの定義・検出方法
2. 既存Helperと期待されるHelperの差分表現
3. 関数本体の更新とimportの追加・整理
4. ファイル変更を担当するレイヤー
5. 既存テストを踏まえたUnit Test・結合テストの進め方

コードの現状を確認せずに、大規模なリファクタリングや実装案を先に決めない。
