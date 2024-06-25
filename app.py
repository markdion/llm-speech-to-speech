import base64
import io
from flask import Flask, json, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(organization='org-FL8rWQd8qtgQQDDizdaPnf7p')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' in request.files:
        audio_file = request.files['audio']
        conversation_history = request.form['conversationHistory']

        try:
            conversation_history = json.loads(conversation_history)

            audio_bytes = audio_file.read()

            if not audio_file.filename.endswith(('.flac', '.m4a', '.mp3', '.mp4', '.mpeg', '.mpga', '.oga', '.ogg', '.wav', '.webm')):
                return jsonify({"error": "Invalid file format"}), 400
            audio_io = io.BytesIO(audio_bytes)
            audio_io.name = "audio.wav"

            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_io
            )
            user_input = transcription_response.text
            conversation_history.append({"role": "user", "content": user_input})

            text_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history,
            )
            text_response = text_response.choices[0].message.content

            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text_response,
            )
            speech_bytes = b''.join(chunk for chunk in speech_response.iter_bytes())

            conversation_history.append({"role": "assistant", "content": text_response})

            speech_base64 = base64.b64encode(speech_bytes).decode('utf-8')

            print("Response: " + text_response)
            return jsonify({
                "conversationHistory": conversation_history,
                "audioResponse": speech_base64
            })
        
        except Exception as e:
            return jsonify({"message": "An error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
