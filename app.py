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

    def generate_stream():
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}],
                stream=True,
            )
            for chunk in stream:
              if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
              else:
                    raise ValueError("An error occurred while generating the response")
        
        except Exception as e:
            yield jsonify({"error": str(e)})

    return Response(generate_stream())

if __name__ == '__main__':
    app.run(debug=True)
