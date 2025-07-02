# file_manipulator.py

## 概要

`file_manipulator.py` は、テキストファイルに対して様々な操作（行の逆順保存、コピー、内容の複製、文字列置換）をコマンドラインから実行できるPythonスクリプトです。

## 使い方

コマンドプロンプトやPowerShellで以下のように実行します。

```
python file_manipulator.py <command> <args...>
```

### コマンド一覧

- `reverse <input> [output]`
  - 入力ファイルの行を逆順にして新しいファイルに保存します。
  - 例: `python file_manipulator.py reverse input.txt output.txt`
  - 出力ファイル省略時は `reversed.txt` になります。

- `copy <input> [output]`
  - 入力ファイルをコピーします。
  - 例: `python file_manipulator.py copy input.txt copyed.txt`
  - 出力ファイル省略時は `copyed.txt` になります。

- `duplicate-contents <input> <multiplier>`
  - 入力ファイルの内容を指定回数だけ繰り返して上書きします。
  - 例: `python file_manipulator.py duplicate-contents input.txt 3`

- `replace-string <input> <needle> <newstring>`
  - 入力ファイル内の文字列をすべて置換します。
  - 例: `python file_manipulator.py replace-string input.txt old new`

## 注意事項
- 文字コードは自動判定されますが、失敗時はUTF-8で処理します。
- `duplicate-contents` と `replace-string` は入力ファイルを上書きします。必要に応じてバックアップを取ってください。

## 必要なパッケージ
- chardet

インストール例:
```
pip install chardet pytest
```

---
