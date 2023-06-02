import requests
import time

url_base = 'http://127.0.0.1:15000/api'
# いくつかのメッセージを送信
with open('./sample_text/sample_short.txt', 'r') as f:
    conversations = f.readlines()

messages = []
for conv in conversations:
    if conv == '\n':
        pass
    else:
        name, icon, msg = conv.split(':')
        messages.append({"message": msg, "userName": name, "userIcon": icon})

for msg in messages:
    print(msg)
    response = requests.post(url_base + "/send-message", data=msg)
    print(response)
    if response.json()['success']:
        print("メッセージが追加されました。")
    else:
        print("メッセージ追加に失敗しました。")
    time.sleep(5)

# ミーティングを終了
response = requests.post(url_base + "/finish-meeting")