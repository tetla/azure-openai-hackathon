import requests

url = 'http://127.0.0.1:15000/api/send-message'

# いくつかのメッセージを送信
messages = [
    {"message": "こんにちは、みなさん！", "userName": "Alice"},
    {"message": "今日はいい天気ですね！", "userName": "Bob"},
    {"message": "これはbotのメッセージです", "userName": "Bot", "bot": True},
    {"message": "新しいプロジェクトに取り組んでいます。", "userName": "Carol"}
]

for msg in messages:
    response = requests.post(url, data=msg)
    print(response)

    if response.json()['success']:
        print("メッセージが追加されました。")
    else:
        print("メッセージ追加に失敗しました。")