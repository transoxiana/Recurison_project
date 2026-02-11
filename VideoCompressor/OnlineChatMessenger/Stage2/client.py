import socket
import threading

# ==============================
# TCP 部分: ルーム作成/参加
# ==============================

def build_tcp_header(roomname: str, operation: int, state: int, payload: bytes) -> bytes:
    """
    TCPヘッダを32バイト固定で構築する。
    [RoomNameSize(1)][Operation(1)][State(1)][OperationPayloadSize(29)]
    """
    room_bytes = roomname.encode("utf-8")
    if len(room_bytes) > 28:
        raise ValueError("Room name too long (max 28 bytes)")

    payload_size = len(payload)
    if payload_size > 229:
        raise ValueError("Payload too long (max 229 bytes)")

    header = bytearray()
    header.append(len(room_bytes))                   # ルーム名長
    header.append(operation & 0xFF)                  # 操作コード (1=作成, 2=参加)
    header.append(state & 0xFF)                      # 状態コード (0=リクエスト, 1=応答, 2=完了)
    header.extend(payload_size.to_bytes(29, "big"))  # ペイロードサイズ

    return bytes(header), room_bytes, payload


def recv_tcp_response(sock):
    """
    サーバからのレスポンスを受信して解析する。
    - 32バイトのヘッダを受信
    - state と payload を返す
    """
    header = sock.recv(32)
    if len(header) < 32:
        raise Exception("Invalid TCP response header")

    roomname_length = header[0]
    operation = header[1]
    state = header[2]
    payload_size = int.from_bytes(header[3:32], "big")

    # 応答ではルーム名は通常空なので読み飛ばし
    if roomname_length > 0:
        sock.recv(roomname_length)

    payload = sock.recv(payload_size) if payload_size > 0 else b""
    return operation, state, payload


def tcp_create_room(server_ip, server_port, username, roomname, password=""):
    """
    新規チャットルームを作成する。
    - state=0 でリクエスト送信
    - state=1 で応答を受信 (OK/ERROR)
    - state=2 でトークンを受信
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    payload = f"{username}:{password}".encode("utf-8")
    header, room_bytes, payload = build_tcp_header(roomname, 1, 0, payload)

    # --- リクエスト送信 ---
    s.sendall(header)
    s.sendall(room_bytes)
    s.sendall(payload)

    # --- 応答受信 (state=1) ---
    op, state, payload = recv_tcp_response(s)
    if state != 1 or not payload.startswith(b"OK"):
        s.close()
        raise Exception("Room creation failed: " + payload.decode(errors="ignore"))

    # --- 完了受信 (state=2, token) ---
    op, state, payload = recv_tcp_response(s)
    s.close()
    if state == 2:
        token = payload
        return roomname, token
    else:
        raise Exception("Room creation failed at completion stage")


def tcp_join_room(server_ip, server_port, username, roomname, password=""):
    """
    既存チャットルームに参加する。
    - state=0 でリクエスト送信
    - state=1 で応答を受信 (OK/ERROR)
    - state=2 でトークンを受信
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    payload = f"{username}:{password}".encode("utf-8")
    header, room_bytes, payload = build_tcp_header(roomname, 2, 0, payload)

    # --- リクエスト送信 ---
    s.sendall(header)
    s.sendall(room_bytes)
    s.sendall(payload)

    # --- 応答受信 (state=1) ---
    op, state, payload = recv_tcp_response(s)
    if state != 1 or not payload.startswith(b"OK"):
        s.close()
        raise Exception("Room join failed: " + payload.decode(errors="ignore"))

    # --- 完了受信 (state=2, token) ---
    op, state, payload = recv_tcp_response(s)
    s.close()
    if state == 2:
        token = payload
        return roomname, token
    else:
        raise Exception("Room join failed at completion stage")


# ==============================
# UDP 部分: チャット送受信
# ==============================
def build_udp_packet(roomname: str, token: bytes, username: str, message: str) -> bytes:
    """
    UDPで送信するパケットを構築。
    [RoomNameLen][RoomName][TokenLen][Token][UserLen][Username][Message]
    """
    room_bytes = roomname.encode("utf-8")
    user_bytes = username.encode("utf-8")
    msg_bytes = message.encode("utf-8")

    packet = bytearray()
    packet.append(len(room_bytes))
    packet.extend(room_bytes)
    packet.append(len(token))
    packet.extend(token)
    packet.append(len(user_bytes))
    packet.extend(user_bytes)
    packet.extend(msg_bytes)
    return bytes(packet)


def receiver(sock: socket.socket):
    """
    サーバからのメッセージを常時受信するスレッド。
    - 通常のチャットメッセージを表示
    - [SERVER] Host has left. Room closed. を受け取ったら終了
    """
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            msg = data.decode()
            if msg.startswith("[SERVER] Host has left"):
                print("\n[INFO] ルームが閉じられました。クライアントを終了します。")
                exit(0)
            print("\n[RECV]", msg, "\n> ", end="")
        except Exception as e:
            print("[Receiver Error]", e)
            break


def udp_chat(roomname: str, token: bytes, username: str, server_ip="127.0.0.1", server_port=6000):
    """UDPチャット本体"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 0))

    print(f"[UDP CLIENT] Connected to {server_ip}:{server_port}")
    print("Type messages and press Enter to send. Ctrl+C to quit.")

    threading.Thread(target=receiver, args=(sock,), daemon=True).start()

    try:
        while True:
            text = input("> ")
            if not text.strip():
                continue
            packet = build_udp_packet(roomname, token, username, text)
            sock.sendto(packet, (server_ip, server_port))
    except KeyboardInterrupt:
        print("\n[UDP CLIENT] Exiting...")
    finally:
        sock.close()


# ==============================
# メイン処理
# ==============================
if __name__ == "__main__":
    server_ip = "127.0.0.1"
    tcp_port = 5000
    udp_port = 6000

    username = input("ユーザー名: ")
    mode = input("create / join ? ")

    if mode == "create":
        roomname = input("新しいルーム名: ")
        password = input("ルームパスワード（任意、空欄可）: ")
        roomname, token = tcp_create_room(server_ip, tcp_port, username, roomname, password)
        print(f"Room '{roomname}' created. Token={token.decode(errors='ignore')}")
    else:
        roomname = input("参加するルーム名: ")
        password = input("ルームパスワード（必要なら入力）: ")
        roomname, token = tcp_join_room(server_ip, tcp_port, username, roomname, password)
        print(f"Joined room '{roomname}'. Token={token.decode(errors='ignore')}")

    udp_chat(roomname, token, username, server_ip, udp_port)