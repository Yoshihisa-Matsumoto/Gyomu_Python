# 新規パッケージ

1. `packages`の下に作成
2. 新規フォルダに`src`/`tests`フォルダ作成し、`pyproject.toml`/`README.mdを用意`（他のpackageを参考に）
3. root folderの`pyproject.toml`の`[tool.uv.workspace]`セクションに新パッケージを追加
4. root folderの`pyrightconfig.json`の`extraPaths`に対象パッケージのsrcパスを追加
5. フォルダなどある程度用意したら、root folderにて `uv sync`
6. .vscode/tasks.jsonで、`"Gyomu: Type Check",`の変更をする。引数にパッケージsrcが並んでいるのでそこに追加する
