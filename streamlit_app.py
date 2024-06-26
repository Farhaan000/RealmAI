import streamlit as st
from llm import LLMInvoker
from PIL import Image
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import torch

st.set_page_config(page_title="ChatAI 🤖", layout="wide")

st.title("ChatAI 🤖")
st.caption("🚀 A Streamlit chatbot powered by OpenAI with Image Recognition")

# Custom CSS for the attachment icon
st.markdown("""
<style>
    .stButton > button {
        background-color: transparent;
        border: none;
        color: grey;
        font-size: 20px;
    }
    .stButton > button:hover {
        color: white;
    }
    .file-uploader {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript to handle file selection
st.markdown("""
<script>
function selectFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            const contents = e.target.result;
            window.parent.postMessage({type: 'uploadFile', contents: contents, name: file.name}, '*');
        };
        reader.readAsDataURL(file);
    };
    input.click();
}
</script>
""", unsafe_allow_html=True)

# Initialize the image recognition model
@st.cache_resource
def load_image_model():
    model_name = "google/vit-base-patch16-224"
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModelForImageClassification.from_pretrained(model_name)
    return feature_extractor, model

feature_extractor, model = load_image_model()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "llm_instance" not in st.session_state:
    st.session_state["llm_instance"] = LLMInvoker()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Create three columns for input
col1, col2, col3 = st.columns([0.88, 0.06, 0.06])

with col1:
    prompt = st.text_input("You:", key="input")

with col2:
    # Custom attachment button
    st.markdown('<button onclick="selectFile()">📎</button>', unsafe_allow_html=True)

with col3:
    send_button = st.button("Send")

# Handle file upload using a hidden uploader
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="uploader", label_visibility="hidden")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Perform image recognition
    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    
    # Get the predicted label
    predicted_label = model.config.id2label[predicted_class_idx]
    
    # Add image recognition result to chat
    image_message = f"I see an image of {predicted_label}."
    st.session_state.messages.append({"role": "assistant", "content": image_message})
    st.chat_message("assistant").write(image_message)

if send_button and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Use the persisted instance of LLMInvoker
    llm = st.session_state["llm_instance"]

    # Invoke the function with the current prompt
    output = llm.llm_invoker(prompt)

    # Process the response to extract the relevant answer
    filtered_response_start = output.rfind("Answer:") + len("Answer:")
    response = output[filtered_response_start:].strip()

    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    print("Response: ", output)
    print("****************************" * 9)

    # Clear the input box after sending
    st.session_state.input = ""
