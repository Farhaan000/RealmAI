# import streamlit as st
# from langchain_community.llms import HuggingFaceHub
# import os
# from urllib.request import urlretrieve
# import numpy as np
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# from langchain_community.llms import HuggingFacePipeline
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory
# from langchain_community.vectorstores import FAISS
# from urllib.request import urlretrieve


# st.title("💬 Chatbot")
# st.caption("🚀 A Streamlit chatbot powered by OpenAI")
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

# if prompt := st.chat_input():


#     client = HuggingFaceHub(
#                 repo_id="mistralai/mixtral-8x7b-instruct-v0.1",
#                 huggingfacehub_api_token = "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",
#                 model_kwargs={"temperature":0.1, "max_length":1000000})

#     st.session_state.messages.append({"role": "user", "content": prompt})
#     st.chat_message("user").write(prompt)
#     response = client.invoke(prompt)
#     trim_response = response.find(prompt) + len(prompt)
#     response = response[trim_response:]
#     st.session_state.messages.append({"role": "assistant", "content": response})
#     st.chat_message("assistant").write(response)

#     print("Response: ", response);
















import streamlit as st
from llm import LLMInvoker

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "llm_instance" not in st.session_state:
    st.session_state["llm_instance"] = LLMInvoker()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
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


