from openai import OpenAI
import streamlit as st
from langchain_community.llms import HuggingFaceHub
import os
from urllib.request import urlretrieve
import numpy as np
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from urllib.request import urlretrieve
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

huggingface_embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device':'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

vectorstore = FAISS.load_local("faiss_index", huggingface_embeddings, allow_dangerous_deserialization= True)

relevant_doc = vectorstore.similarity_search("Who is farhaan")
context = relevant_doc[0].page_content
print(context)