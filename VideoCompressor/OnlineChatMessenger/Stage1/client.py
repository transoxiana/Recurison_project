# ステージ 1
# 推奨使用言語: Python（サーバとクライアント両方で）


# 内容
# このステージでは、クライアントがサーバに接続する形式のチャットメッセンジャーサービスを作成します。
# サーバはバックグラウンドで稼働し、一方でクライアントは CLI を通じてサーバに接続します。
# 接続が確立された後、クライアントはメッセージを入力してサーバに送り、そのメッセージはサーバに接続している他の全てのクライアントにも配信されます。


# 機能要件
# サーバは CLI で起動し、バックグラウンドで着信接続を待ち受けます。
# もしサーバがオフラインであれば、それはチャットサービス自体が停止しているということです。

# サーバとクライアントは、UDP ネットワークソケットを使ってメッセージのやり取りをします。
# メッセージ送信時、サーバとクライアントは一度に最大で 4096 バイトのメッセージを処理します。
# これは、クライアントが送信できるメッセージの最大サイズです。同じく、最大 4096 バイトのメッセージが他の全クライアントに転送されます。
# セッションが開始される際には、クライアントはユーザーにユーザー名を入力させます。
# メッセージの送信プロトコルは比較的シンプルです。メッセージの最初の 1 バイト、usernamelen は、ユーザー名の全バイトサイズを示し、
# これは最大で 255バイト（28 - 1 バイト）になります。サーバはこの初めの usernamelen バイトを読み、送信者のユーザー名を特定します。
# その後のバイトは送信される実際のメッセージです。この情報はサーバとクライアントによって自由に使用され、ユーザー名の表示や保存が可能です。
# バイトデータは UTF-8 でエンコードおよびデコードされます。これは、1 文字が 1 から 4 バイトで表現される意味です。
# Python の str.encode と str.decode メソッドは、デフォルトでこの挙動を持っています。
# サーバにはリレーシステムが組み込まれており、現在接続中のすべてのクライアントの情報を一時的にメモリ上に保存します。
# 新しいメッセージがサーバに届くと、そのメッセージは現在接続中の全クライアントにリレーされます。
# クライアントは、何回か連続で失敗するか、しばらくメッセージを送信していない場合、自動的にリレーシステムから削除されます。
# この点で TCP と異なり、UDP はコネクションレスであるため、各クライアントの最後のメッセージ送信時刻を追跡する必要があります。

# 非機能要件
# チャットメッセージングシステムは、リアルタイムのデータの優先度が信頼できるデータよりも高いとされています。
# システムは、毎秒最低で 10,000 パケットの送信をサポートする必要があります。
# 例えば、1000 人が一つのチャットルームにいる場合、システムは毎秒最低でも 10 メッセージを処理できるように設計されているべきです。
# 一般的なハードウェアならこの条件を満たすことができます。

# UDPを使用する
import socket


def main():
    def protocol_format(usernamelen, username, message):
        return usernamelen.to_bytes(1, "big") + username + message

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = '127.0.0.1'
    server_port = 9001
    address = ''
    port_num = input("ポート番号を指定してください：")
    port = int(port_num)

    # 空の文字列も0.0.0.0として使用できます。
    sock.bind((address, port))

    # セッション開始時にユーザーネームを入力させる
    print("ようこそ、オンラインチャットへ自由につぶやいてください！")
    userName = input("usernameを入力してください:")
    username_byte = str.encode(userName)
    usernamelen = len(username_byte)
    if usernamelen > 255:
        raise ValueError("usernameが長すぎます")

    try:
        while True:
            # メッセージを入力
            inputMessage = input("メッセージを入力してください：")
            message = str.encode(inputMessage)
            if len(message) > 4095 - usernamelen:
                raise ValueError("messageが長すぎます")

            # メッセージの送信
            request = protocol_format(usernamelen, username_byte, message)
            # サーバへのデータ送信
            sent = sock.sendto(request, (server_address, server_port))
            print('Send {} bytes'.format(sent))

            # 応答を受信
            print('waiting to receive')
            data, server = sock.recvfrom(4096)
            data = data.decode('utf-8')
            print('received {!r}'.format(data))

    finally:
        print('closing socket')
        sock.close()


if __name__ == "__main__":
    main()
