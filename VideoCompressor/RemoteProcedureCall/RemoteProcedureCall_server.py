import socket
import os
import math
import json


class NetworkSet:
    # ネットワーク設定
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_address = '/tmp/rpc_server.sock'
        self.unlink()  # 既存のソケットファイルを削除

    def unlink(self):
        # ソケットファイルを削除
        try:
            os.unlink(self.server_address)
        except FileNotFoundError:
            pass

    def start_server(self, service):
        # ソケットをバインドしてリッスン状態にする
        self.sock.bind(self.server_address)
        self.sock.listen(1)
        print(f"Server started and listening on {self.server_address}")
        while True:
            connection, client_address = self.sock.accept()
            try:
                # ここでクライアントからのリクエストを処理する
                data = connection.recv(4096).decode('utf-8')
                if not data:
                    continue

                try:
                    request = json.loads(data)
                    command = request.get("command", "")
                    params = request.get("params", [])
                    # サービスを実行
                    function = service.execute(command)
                    response = function(*params)  # アンパックの利用
                    connection.sendall(json.dumps(
                        {"status": "ok", "result": response}).encode('utf-8'))
                except json.JSONDecodeError:
                    connection.sendall(json.dumps(
                        {"status": "error", "message": "Invalid JSON format"}).encode('utf-8'))
                except ValueError as e:
                    connection.sendall(json.dumps(
                        {"status": "error", "message": str(e)}).encode('utf-8'))
                except Exception as e:
                    connection.sendall(json.dumps(
                        {"status": "error", "message": "internal server error"}).encode('utf-8'))
            finally:
                connection.close()


class Service:
    def __init__(self):
        self.service = {
            "floor": lambda x: math.floor(float(x)),
            "nroot": lambda n, x: float(x) ** (1 / float(n)) if float(n) != 0 and not (float(x) < 0 and int(n) % 2 == 0) else None,
            "reverse": lambda x: x[::-1] if isinstance(x, str) else None,
            "validanagram": lambda x, y: sorted(x) == sorted(y) if isinstance(x, str) and isinstance(y, str) else None,
            "sort": lambda x: ",".join(sorted(x)).replace(",", "") if isinstance(x, (str, list, tuple)) else None,
        }

    def execute(self, command):
        # コマンドの文字列が大文字でも対応
        command = command.lower().strip()
        # コマンドがサービスに存在するか確認
        if command in self.service:
            return self.service[command]
        else:
            raise ValueError(f"Command '{command}' not found incorrectly.")

# それぞれのクラスをインスタンス化


def main():
    # ネットワーク設定とサービスを初期化
    service = Service()
    network_set = NetworkSet()
    # サーバーを起動
    network_set.start_server(service)


if __name__ == "__main__":
    main()
