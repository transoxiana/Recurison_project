import socket
import threading
import uuid
from datetime import datetime, timedelta
from collections import deque

# ==============================
# グローバルなルーム管理用辞書
# ==============================
chat_rooms = {}

# ==============================
# TCP サーバ: ルーム作成・参加を担当
# ==============================


def send_tcp_response(conn, operation, state, payload: bytes):
    """
    共通レスポンス送信関数
    [RoomNameSize(1)][Operation(1)][State(1)][PayloadSize(29)] + Payload
    """
    roomname_bytes = b""  # 応答ではルーム名は不要
    header = bytearray()
    header.append(len(roomname_bytes))
    header.append(operation & 0xFF)
    header.append(state & 0xFF)
    header.extend(len(payload).to_bytes(29, "big"))
    conn.sendall(header)
    if roomname_bytes:
        conn.sendall(roomname_bytes)
    if payload:
        conn.sendall(payload)


def handle_tcp_client(conn, addr):
    try:
        # --- ヘッダ受信 ---
        header = conn.recv(32)
        if len(header) < 32:
            print("[TCP] Invalid header size")
            return

        roomname_length = header[0]
        operation = header[1]
        state = header[2]
        payload_size = int.from_bytes(header[3:32], "big")

        # --- ルーム名受信 ---
        roomname = conn.recv(roomname_length).decode("utf-8")

        # --- ペイロード受信 ---
        payload = conn.recv(payload_size) if payload_size > 0 else b""

        # ペイロードは "username:password" 形式
        username, password = "unknown", ""
        if payload:
            parts = payload.decode("utf-8").split(":", 1)
            username = parts[0]
            if len(parts) > 1:
                password = parts[1]

        print(
            f"[TCP] op={operation}, state={state}, room={roomname}, user={username}, from={addr}")

        # --- state=0 リクエスト処理 ---
        if state == 0:
            if operation == 1:  # 新規ルーム作成
                if roomname in chat_rooms:
                    send_tcp_response(conn, operation, 1, b"ERROR:RoomExists")
                else:
                    send_tcp_response(conn, operation, 1, b"OK")
                    token = str(uuid.uuid4()).encode()[:255]
                    chat_rooms[roomname] = {
                        "host": token,
                        "password": password,
                        "members": {token: addr}
                    }
                    send_tcp_response(conn, operation, 2, token)
                    print(f"[CREATE] Room '{roomname}' created by {username}")

            elif operation == 2:  # 既存ルーム参加
                if roomname not in chat_rooms:
                    send_tcp_response(conn, operation, 1,
                                      b"ERROR:RoomNotFound")
                else:
                    room_info = chat_rooms[roomname]
                    if room_info["password"] and room_info["password"] != password:
                        send_tcp_response(conn, operation, 1,
                                          b"ERROR:WrongPassword")
                    else:
                        send_tcp_response(conn, operation, 1, b"OK")
                        token = str(uuid.uuid4()).encode()[:255]
                        room_info["members"][token] = addr
                        send_tcp_response(conn, operation, 2, token)
                        print(f"[JOIN] {username} joined room '{roomname}'")

            else:
                send_tcp_response(conn, operation, 1,
                                  b"ERROR:UnsupportedOperation")

    except Exception as e:
        print("[TCP] Error:", e)
    finally:
        conn.close()


def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen()
    print("[TCP] Listening on port 5000...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(
            conn, addr), daemon=True).start()

# ==============================
# UDP サーバ: メッセージリレー
# ==============================


class Message:
    def __init__(self, username, message, updatetime, roomname, token):
        self.username = username
        self.message = message
        self.time = updatetime
        self.roomname = roomname
        self.token = token


def udp_server():
    active_address = {}
    time_management_queue = deque()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 6000))
    print("[UDP] Listening on port 6000...")

    while True:
        data, address = sock.recvfrom(4096)
        try:
            idx = 0
            roomlen = data[idx]
            idx += 1
            roomname = data[idx:idx+roomlen].decode()
            idx += roomlen
            tokenlen = data[idx]
            idx += 1
            token = data[idx:idx+tokenlen]
            idx += tokenlen
            userlen = data[idx]
            idx += 1
            username = data[idx:idx+userlen].decode()
            idx += userlen
            message = data[idx:].decode()
        except Exception as e:
            print("[UDP] Invalid packet:", e)
            continue

        if roomname not in chat_rooms:
            continue
        members = chat_rooms[roomname]["members"]
        if token not in members or members[token] != address:
            continue

        now = datetime.now()
        active_address[username] = [address, now]
        time_management_queue.append(
            Message(username, message, now, roomname, token))

        for t, member_addr in members.items():
            if member_addr != address:
                relay_text = f"{username}: {message}"
                sock.sendto(relay_text.encode(), member_addr)

        TIMEOUT_SECONDS = 300
        while time_management_queue and time_management_queue[0].time < now - timedelta(seconds=TIMEOUT_SECONDS):
            msg_item = time_management_queue.popleft()
            if msg_item.username in active_address and msg_item.time == active_address[msg_item.username][1]:
                active_address.pop(msg_item.username)
                room = chat_rooms.get(msg_item.roomname)
                if room and msg_item.token == room["host"]:
                    for _, member_addr in room["members"].items():
                        sock.sendto(
                            b"[SERVER] Host has left. Room closed.", member_addr)
                    del chat_rooms[msg_item.roomname]
                    print(
                        f"[CLOSE] Room '{msg_item.roomname}' closed because host left.")


# ==============================
# メイン
# ==============================
if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    udp_server()
