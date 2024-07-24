from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
import os
import torch
from static.llm.llm import LLMInvoker
from static.llm.lim_llm import LIM_LLMInvoker
from static.LIM.lim import LIMInvoker
from PIL import Image
from torchvision.transforms import functional as F

app = Flask(__name__)

llm = LLMInvoker()
lim_llm = LIM_LLMInvoker()
lim = LIMInvoker()

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    print("Received data:", data)

    if 'message' in data:
        prompt = data.get('message', '')
        bot_response = llm.llm_invoker(prompt, lim_llm_invoker=lim_llm)
        lim_llm.generate_context_aware_prompt(prompt=prompt, llm_response=bot_response, llm_invoker=llm)
        return jsonify({"response": bot_response})

    return jsonify({"error": "Invalid request"}), 400

@app.route('/process-image-and-prompt', methods=['POST'])
def process_image_and_prompt():
    if 'file' not in request.files or 'prompt' not in request.form:
        return jsonify({'error': 'File or prompt not provided'}), 400

    file = request.files['file']
    prompt = request.form['prompt']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        print(f"File saved to: {file_path}")

        
        # Process the image 
        image = Image.open(file_path).convert("RGB")
        image_tensor = F.to_tensor(image).unsqueeze(0)
        lim_response = lim.lim_invoker(image= image_tensor)

        # Process the prompt
        lim_llm_response = lim_llm.lim_llm_invoker(prompt=prompt, llm_invoker=llm)

        llm.generate_context_aware_prompt(prompt=prompt, lim_llm_response=lim_llm_response, lim_llm_invoker=lim_llm)

        # Combine responses
        combined_response = f"{lim_response} Also, regarding your prompt: {lim_llm_response}"

        return jsonify({"response": combined_response})
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(port=5001)
