import os
import queue
import uuid
from datetime import datetime
import requests
from distutils.util import strtobool

from flask import Flask, jsonify, render_template, request
import oai

recognized_text_queue = queue.Queue()
speech_recognizer = None
app = Flask(__name__)
app_data = {
    'messages': [],
    'current_topic_messages': []
}
@app.route('/')
def home():
    return render_template('index.html', messages=app_data['messages'])

@app.route('/api/send-message', methods=['POST'])
def send_message():
    message = request.form.get('message')
    userName = request.form.get('userName')
    userIcon = request.form.get('userIcon') or 'Bandit'
    userIcon = "https://api.dicebear.com/6.x/personas/svg?seed=" + userIcon
    bot = request.form.get('bot') or False

    if message:
        timestamp = datetime.now()
        app_data['messages'].append({'timestamp': timestamp, 'message': message, 'userName': userName, 'userIcon': userIcon, 'bot': bot})

        if "ちくわ大明神" in message:
            botUserIcon = "https://api.dicebear.com/6.x/thumbs/svg?seed=Snuggles"
            app_data['messages'].append({'timestamp': timestamp, 'message': "会議にそぐわない発言を検知しました。", 'userName': '検閲くん', 'userIcon': botUserIcon, 'bot': True})
            return jsonify({'success': True, 'message': 'メッセージが追加されました。'})
        
        if is_topic_changed(app_data['current_topic_messages'], message):
            summary = get_summary("\n".join([x['message'] for x in app_data['current_topic_messages']]))
            # next_action = get_next_task("\n".join([x['message'] for x in app_data['current_topic_messages']]))
            botUserIcon = "https://api.dicebear.com/6.x/thumbs/svg?seed=Boo"
            app_data['messages'].append({'timestamp': timestamp, 'message': summary, 'userName': '要約くん', 'userIcon': botUserIcon, 'bot': True})
            # app_data['messages'].append({'timestamp': timestamp, 'message': next_action, 'userName': 'タスクくん', 'userIcon': botUserIcon, 'bot': True})

            app_data['current_topic_messages'] = []

        app_data['current_topic_messages'].append({'timestamp': timestamp, 'message': message, 'userName': userName, 'userIcon': userIcon, 'bot': bot})
        return jsonify({'success': True, 'message': 'メッセージが追加されました。'})
    else:
        return jsonify({'success': False, 'message': 'メッセージが空です。'})

@app.route('/api/finish-meeting', methods=['POST'])
def finish_meething():
    all_message = "\n".join([x['message'] for x in app_data['messages'] if x['bot'] == False])
    summary = get_summary(all_message)
    next_action = get_next_task(all_message)
    botUserIcon1 = "https://api.dicebear.com/6.x/thumbs/svg?seed=Coco"
    botUserIcon2 = "https://api.dicebear.com/6.x/thumbs/svg?seed=Cali"
    timestamp = datetime.now()
    app_data['messages'].append({'timestamp': timestamp, 'message': summary, 'userName': '総括くん', 'userIcon': botUserIcon1, 'bot': True})
    app_data['messages'].append({'timestamp': timestamp, 'message': next_action, 'userName': '宿題くん', 'userIcon': botUserIcon2, 'bot': True})

    return jsonify({'success': True, 'message': 'メッセージが追加されました。'})


@app.route('/api/summarize', methods=['POST'])
def summarize():
    text = request.form.get('text')
    if text:
        try:
            summary = get_summary(text)
            return jsonify({'success': True, 'summary': summary})
        except Exception:
            return jsonify({'success': False, 'message': '要約に失敗しました。'})
    else:
        return jsonify({'success': False, 'message': 'テキストが空です。'})

@app.route('/api/messages', methods=['GET'])
def api_messages():
    return jsonify(app_data['messages'])

@app.route('/api/ai-messages', methods=['GET'])
def api_aimessages():
    messages = [
        {
            "userIcon": "https://api.dicebear.com/6.x/thumbs/svg?seed=Muffin",
            "userName": "Muffin",
            "message": "This is a test message",
            "timestamp": "10:32"
        },
    ]
    return jsonify(messages)
    
def summarize_period(start_time, end_time):
    start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S')
    period_messages = [message for message in app_data['messages'] if start_time <= message['timestamp'] <= end_time]
    text = " ".join([message['content'] for message in period_messages])
    return get_summary(text)

@app.route('/api/get-period-summary', methods=['POST'])
def get_period_summary():
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    if start_time and end_time:
        try:
            summary = summarize_period(start_time, end_time)
            translation = translate_text(summary)
            return jsonify({'success': True, 'summary': summary, 'translation': translation})
        except Exception:
            return jsonify({'success': False, 'message': '要約に失敗しました。', 'translation': '要約に失敗しました。'})
    else:
        return jsonify({'success': False, 'message': '開始時間または終了時間が空です。'})
    
# 過去の3つのメッセージと最新のメッセージの話題が共通か異なるか判定する
def is_topic_changed(current_topic_messages, latest_message: str) -> bool:
    messages = current_topic_messages
    if len(messages) < 4:
        return False
    else:
        past_messages = "\n".join([message['message'] for message in messages[-4:-1]])
        content = [
        {
            "role": "system",
            "content": """You are an AI assistant.
            Are the past messages and latest message in the above conversation on the same topic? Are they different topics?
            If they are the same topic, please return False. If they are different topics, please return True.""",
        },
        {"role": "user", "content": f"## past messages\n{past_messages}\n## latest message\n{latest_message}"},
        ]
        openai = oai.Openai()
        flag = openai.chat_completion(content)
        return strtobool(flag)
    
def get_summary(text):
    message = [
        {
            "role": "system",
            "content": """You are an AI assistant that summarize text.
            Please summarize the input text.""",
        },
        {"role": "user", "content": f"{text}"},
    ]
    openai = oai.Openai()
    summary = openai.chat_completion(message)
    return summary

def get_next_task(text):
    message = [
        {
            "role": "system",
            "content": """You are an AI assistant that extract the next task from conversations.
            List below the tasks to be performed by the next from the above conversation and who is assigned to those tasks. Please generate the text in the following format in Japanese.
            タスク: [what to do]
            担当者: [who is in charge of the task]""",
        },
        {"role": "user", "content": f"{text}"},
    ]
    openai = oai.Openai()
    summary = openai.chat_completion(message)
    return summary

def translate_text(text):
    translator_url = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'ja'
    }
    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv('TRANSLATOR_KEY'),
        'Ocp-Apim-Subscription-Region': os.getenv('SERVICE_REGION'),
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{
        'text': f'{text}'
    }]
    request = requests.post(translator_url, params=params, headers=headers, json=body)
    response = request.json()
    return response[0].get('translations')[0].get('text')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=15000)
