from flask import Flask, Response, request, jsonify, render_template
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
    data = request.json
    user_input = data.get('text')

    try:
        text_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
        )
        text_response = text_response.choices[0].message.content

        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text_response,
        )
        speech_bytes = b''.join(chunk for chunk in speech_response.iter_bytes())

        print("Response: " + text_response)
        return Response(speech_bytes, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
