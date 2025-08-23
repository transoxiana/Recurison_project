# RemoteProcedureCall

このディレクトリには、Unixドメインソケットを使った簡易的なRPCサーバー実装（Python）と、クライアント用のサンプル（JavaScript）が含まれています。
## 概要

- サーバー: `RemoteProcedureCall_server.py` — Unixドメインソケット上でJSON形式のリクエストを受け取り、登録済みの関数を実行して結果を返します。
サーバーが現在サポートするコマンド（サービス）:

- `floor`: 引数1つ。数値を切り下げして整数を返します。例: `{ "command": "floor", "params": ["3.7"] }`
- `nroot`: 引数2つ。`n`乗根を計算します（例: n=2,x=9 -> 3）。例: `{ "command": "nroot", "params": ["2", "9"] }`
- `reverse`: 引数1つ。文字列を逆順にします。例: `{ "command": "reverse", "params": ["hello"] }`
- `validanagram`: 引数2つ。2つの文字列がアナグラム（並べ替えで同一）かを真偽で返します。例: `{ "command": "validanagram", "params": ["abc", "bca"] }`
- `sort`: 引数1つ。文字列や配列の要素をソートして返します（文字列の場合は文字ごとにソートして結合）。例: `{ "command": "sort", "params": ["dcba"] }`

各リクエストはJSONで、サーバーはJSONでレスポンスを返します。
成功レスポンスの例:

{
	"status": "ok",
	"result": <関数の返り値>
}
エラーレスポンス例:

{
	"status": "error",
	"message": "エラー内容"
}
## 実行要件

- Python 3.x
- （サンプルクライアント）Node.jsがあれば `RemoteProcedureCall_client.js` を動かせます。
- UNIX上で動作を意図しています。

注意: サーバー実装はUnixドメインソケット（`/tmp/rpc_server.sock`）を使用しています。Windows上で直接実行するとソケット型がサポートされないか既存の環境によっては動かない可能性があります。Windowsで実行する場合は次のいずれかを推奨します。
1. WSL（Linuxサブシステム）内で実行する。
2. サーバーをAF_INET（TCP/IP）へ書き換える。簡単な変更箇所は `NetworkSet` クラスのソケット作成部分です。

## サーバーの実行（例）
1. リポジトリの該当ディレクトリへ移動。
2. 以下でサーバーを起動します（Linux/WSL推奨）:

```powershell
python RemoteProcedureCall_server.py
```
サーバー起動後は `/tmp/rpc_server.sock` を監視して待機します。

## クライアントの利用例
クライアントはソケットへ次のようなJSONを送信します（1リクエスト/1接続を想定）。

例 — 文字列反転:

```json
{"command": "reverse", "params": ["hello"]}
```
サンプルの `RemoteProcedureCall_client.js` を参照して、送信方法や受信処理を確認してください。

## UNIX 上での使用方法

以下は Linux / macOS / WSL 環境での具体的な利用例です。

1. サーバーを起動（バックグラウンドや別ターミナルでも可）:

```bash
python3 RemoteProcedureCall_server.py
```

2. Node.js (JavaScript) を使ったクライアント例:

```bash
node RemoteProcedureCall_client.js　（コマンド名）　（引数１）　（引数２（あれば））
```


