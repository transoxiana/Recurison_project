# Markdown to HTML Converter

このプロジェクトは、MarkdownファイルをHTMLファイルに変換するPythonスクリプトです。

## 使い方

1. 必要なパッケージをインストールします。
   ```sh
   pip install markdown
   ```


2. コマンドラインから以下の形式で実行します。
   ```sh
   python3 file-converter.py markdown 入力ファイル名.md 出力ファイル名.html
   ```

   例:
   ```sh
   python3 file-converter.py markdown sample.md sample.html
   ```

### 使用例

例えば、`README.md` というMarkdownファイルを `README.html` に変換したい場合は、以下のように実行します。

```sh
python3 file-converter.py markdown README.md README.html
```

実行後、同じディレクトリに `README.html` が生成されます。

## ファイル構成
- `Markdown_to_HTML_Converter.py` : Markdown→HTML変換スクリプト

## 注意事項
- 入力ファイルが存在しない場合や、コマンドの引数が正しくない場合はエラーになります。
- Python 3.xが必要です。

## ライセンス
このプロジェクトはMITライセンスです。
