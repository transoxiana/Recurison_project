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

# UDP接続を行う
import socket
from datetime import datetime
from collections import deque
from datetime import timedelta


class Message:
    def __init__(self, username, message, updatetime):
        self.username = username
        self.message = message
        self.time = updatetime


def main():
    # キーをユーザー名、valueをaddressのハッシュマップ
    active_address = {}
    # キューを作成し、時間を管理する
    time_management_queue = deque()

    # AF_INETを使用し、UDPソケットを作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))

    # ソケットを特殊なアドレス0.0.0.0とポート9001に紐付け
    sock.bind((server_address, server_port))

    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(4096)

        print('received {} bytes from {}'.format(len(data), address))
        # 1byteを取り出し、メッセージをを送る
        usernamelen = data[0]
        username = data[1:1+usernamelen].decode('utf-8')
        message = data[1+usernamelen:].decode('utf-8')

        # ハッシュマップに情報を格納する
        time = datetime.now()
        active_address[username] = [address, time]
        # キューに情報を格納する
        time_management_queue.append(Message(username, message, time))

        if message:
            for key, value in active_address.items():
                if username == key:
                    continue
                relay_text = f"{username}: {message}"
                sent = sock.sendto(relay_text.encode('utf-8'), value[0])
                print('sent {} bytes back to {}, for {}'.format(
                    sent, value[1], key))

        # メッセージの送信がないクライアントを削除する
        TIMEOUT_SECONDS = 300
        now_time = datetime.now()

        # キューを参照して、古いメッセージから追っていき削除する
        while time_management_queue and time_management_queue[0].time < now_time - timedelta(seconds=TIMEOUT_SECONDS):
            message_item = time_management_queue.popleft()
            if message_item.username in active_address and message_item.time == active_address[username][1]:
                active_address.pop(message_item.username)


if __name__ == "__main__":
    main()
