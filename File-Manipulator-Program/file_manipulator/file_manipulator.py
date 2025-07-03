import chardet
import codecs
import sys
import shutil


def main():
    commandlist = ["reverse", "copy",
                   "duplicate-contents", "replace-string"]
    if len(sys.argv) < 3:
        print("Invalid command!")
        return
    command = sys.argv[1].lower().strip()
    if command not in commandlist:
        print("Invalid command!")
        return
    if command == commandlist[0]:  # reverse
        if len(sys.argv) < 3:
            print("引数が足りません。usage: reverse <input> [output]")
            return
        input_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else "reversed.txt"
        reverse_lines_text(input_path, output_path)
        return
    elif command == commandlist[1]:  # copy
        if len(sys.argv) < 3:
            print("引数が足りません。usage: copy <input> [output]")
            return
        try:
            input_path = sys.argv[2]
            output_path = sys.argv[3] if len(sys.argv) > 3 else "copyed.txt"
            shutil.copy(input_path, output_path)
            print(f"コピーが完了しました。: {output_path}")
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {input_path}")
        except Exception as e:
            print(f"予期しないエラー: {e}")
        return
    elif command == commandlist[2]:  # duplicate-contents
        if len(sys.argv) < 4:
            print("引数が足りません。usage: duplicate-contents <input> <multiplier>")
            return
        input_path = sys.argv[2]
        try:
            multiplier = int(sys.argv[3])
        except ValueError:
            print("multiplierは整数で指定してください。")
            return
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(input_path, 'w', encoding='utf-8') as f:
                f.writelines(lines * multiplier)
            print("書き込み完了しました！")
        except Exception as e:
            print(f"エラー: {e}")
        return
    elif command == commandlist[3]:  # replace-string
        if len(sys.argv) < 5:
            print("引数が足りません。usage: replace-string <input> <needle> <newstring>")
            return
        input_path = sys.argv[2]
        needle = sys.argv[3]
        newstring = sys.argv[4]
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            new_text = text.replace(needle, newstring)
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(new_text)
            print("文字の置換が完了しました！")
        except Exception as e:
            print(f"エラー: {e}")
        return


def reverse_lines_text(input_path, output_path):
    min_confidence = 0.8
    num_bytes = 10000
    fallback_encoding = 'utf-8'
    try:
        with open(input_path, 'rb') as f:
            raw = f.read(num_bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        confidence = result['confidence']

        if encoding is None or confidence < min_confidence:
            print(
                f"⚠️ 文字コードの推定に自信がありません（推定: {encoding}, 信頼度: {confidence:.2f}）")
            print(f"→ フォールバックとして {fallback_encoding} を使用します。")
            encoding = fallback_encoding

    # バイナリ読み込み＋デコーダ
        with open(input_path, 'rb') as bf, \
                open(output_path, 'wb') as outb:

            reader = codecs.getreader(encoding)(bf, errors='strict')
            writer = codecs.getwriter(encoding)(outb, errors='strict')
            lines = reader.readlines()

            for raw_line in reversed(lines):
                writer.write(raw_line)
            print(f"✅ 行の順番を逆にして保存しました: {output_path}")

    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_path}")
    except UnicodeDecodeError as e:
        print(f"デコードエラー: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
    return None


if __name__ == "__main__":
    main()
