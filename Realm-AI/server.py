from flask import Flask, render_template, jsonify, request
# from static.llm.llm import LLMInvoker

app = Flask(__name__)

# llm = LLMInvoker()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():

    data = request.json
    prompt = data.get('message', '')

    # bot_response = llm.llm_invoker(prompt)
    bot_response = "Heloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"

    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)