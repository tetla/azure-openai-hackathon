import os
import queue
import uuid
from datetime import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import oai
load_dotenv(verbose=True)
INPUT_DEVICE_ID = "{0.0.1.00000000}.{ebf92b49-bf6f-4522-9bf3-7bf803d7e509}"  # VB-Audio VoiceMeeter VAIO
recognized_text_queue = queue.Queue()
speech_recognizer = None
app = Flask(__name__)
app_data = {
    'messages': []
}
@app.route('/')
def home():
    return render_template('index.html', messages=app_data['messages'])

@app.route('/api/send-message', methods=['POST'])
def send_message():
    message = request.form.get('message')
    if message:
        timestamp = datetime.now()
        app_data['messages'].append({'timestamp': timestamp, 'content': message})
        return jsonify({'success': True, 'message': 'メッセージが追加されました。'})
    else:
        return jsonify({'success': False, 'message': 'メッセージが空です。'})
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
@app.route('/api/get-recognized-text')
def get_recognized_text():
    if not recognized_text_queue.empty():
        recognized_text = recognized_text_queue.get()
        try:
            translation = translate_text(recognized_text)
        except Exception:
            translation = "翻訳に失敗しました"
        timestamp = datetime.now()
        app_data['messages'].append({'timestamp': timestamp, 'content': recognized_text, 'translation': translation})
        return jsonify({'success': True, 'message': recognized_text, 'translation': translation})
    else:
        return jsonify({'success': False, 'message': '認識されたテキストがありません。', 'translation': '認識されたテキストがありません。'})
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
    app.run(debug=True)
