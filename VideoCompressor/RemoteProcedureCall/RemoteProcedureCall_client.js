// RPCのクライアント側のコードを書く
// RemoteProcedureCall_client.js

// 必要なモジュールをインポート
const net = require('net');
const sys = require('sys');

// サーバアドレスの設定
const SERVER_HOST = '/tmp/rpc_server.sock';

// コマンドラインから引数を取得
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Usage: node RemoteProcedureCall_client.js <arg1> <arg2> ...');
    process.exit(1);
}

// ソケットを作成
const client = net.createConnection(SERVER_HOST, () => {
    console.log('Connected to RPC server');

});

// サーバに接続
client.on('connect', () => {
    // 引数をサーバに送信
    const request = JSON.stringify({ command: args[0], params: args.slice(1) });

    //requestを送信
    client.write(request, 'utf8', () => {
        console.log('Request sent:', request);
    });

    // サーバからのレスポンスを受け取る
    client.on('data', (data) => {
        const response = JSON.parse(data.toString());
        console.log('Response received:', response);
        client.end(); // 通信終了
    });
})
.on('error', (err) => {
    console.error('Error:', err.message);
});