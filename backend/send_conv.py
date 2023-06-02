import requests
import time

url = 'http://127.0.0.1:15000/api/send-message'
# いくつかのメッセージを送信
with open('./sample_text/sample.txt', 'r') as f:
    conversations = f.readlines()

messages = []
for conv in conversations:
    if conv == '\n':
        pass
    else:
        name, msg = conv.split(':')
        messages.append({"message": msg, "userName": name})

for msg in messages:
    print(msg)
    response = requests.post(url, data=msg)
    print(response)
    if response.json()['success']:
        print("メッセージが追加されました。")
    else:
        print("メッセージ追加に失敗しました。")
    time.sleep(2)