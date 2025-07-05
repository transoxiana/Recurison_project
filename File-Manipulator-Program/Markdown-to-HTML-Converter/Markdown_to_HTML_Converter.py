# マークダウンを HTML に変換するプログラムを作成し、
# シェルを通して python3 file-converter.py markdown inputfile outputfile というコマンドを実行させる

import sys
import markdown
# Markdown to HTML Converter


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 file-converter.py markdown inputfile outputfile")
        sys.exit(1)

    input_file = sys.argv[2]
    output_file = sys.argv[3]

    convert_markdown_to_html(input_file, output_file)


def convert_markdown_to_html(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        html = markdown.markdown(markdown_text)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
