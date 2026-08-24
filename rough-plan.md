7. 現時点でのPython版Infra移行方針

TS版の棚卸し結果から、Python版では以下を想定している。

# 初期から重要

fs
FileAccessService
FileSearchService
ファイル読み書き
JSON変換
Path操作

archive
まずZip
Read / Write
可能ならCompare

csv
Read / Write
Streamingを考慮
JSON / Python object変換

crypt
AES
PKI
純粋関数として提供

web
HTTPアクセス
File download
JSON
XML

shared
ParameterService
VariableTranslatorService
DBとの関係も含めて設計

hash
現時点では直接利用しない
将来Snapshot生成でSHA-256が必要になるため候補

# 将来的に必要だが初期対象外

auth
JWT sign/token/validate
将来的には必要

logger
Python側の方式を今回決定する

parser
XML parser
Web/APIとの組み合わせで必要になる可能性が高い
現時点では不要

excel
現状は非常に単純なExcel exportのみ
Pythonでは別の適切なライブラリを後で検討

holiday
MarketHoliday取得 + Web scrapingが必要

# 現時点では不要

network
Web関連固有
必要になった時に設計

ftp
sftp
ssh
過去には業務上有用だったが、現時点では不要
stream
TS Effect Stream固有の実装
PythonではPython側のStreaming方式を採用する
user
現在未使用
