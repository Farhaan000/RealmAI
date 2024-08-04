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
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

def DocSplitter():
    # loader = PyPDFDirectoryLoader("./Docs_Pdf/")
    loader = DirectoryLoader("./Docs_Word/")
    print("Loader: ", loader)
    docs_before_split = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 700,
        chunk_overlap  = 50,
    )
    docs_after_split = text_splitter.split_documents(docs_before_split)
    print("docs_after_split :", docs_after_split)
    return docs_after_split

def Embeddings(splitted_doc):
    huggingface_embeddings = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device':'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    vectorstore = FAISS.from_documents(splitted_doc, huggingface_embeddings)
    vectorstore.save_local("faiss_index")
    print("fiass_index created successfully")

splitted_doc = DocSplitter()
Embeddings(splitted_doc)