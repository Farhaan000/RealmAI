from langchain_community.llms import HuggingFaceHub
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS

class LLMInvoker:
    def __init__(self):
        self.human_ai_history = ""
        self.template = """
Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
------
<ctx>
{context}
</ctx>
------
<hs>
{history}
</hs>
------
Question:
{question}
Answer:
"""
        
        # Initialize embeddings and LLM once
        self.huggingface_embeddings = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True})

        self.llm = HuggingFaceHub(
            repo_id="mistralai/mixtral-8x7b-instruct-v0.1",
            huggingfacehub_api_token="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",
            model_kwargs={"temperature": 0.1, "max_length": 1000})

        self.vectorstore = FAISS.load_local("faiss_index", self.huggingface_embeddings, allow_dangerous_deserialization=True)

    def llm_invoker(self, prompt: str):
        # Get relevant document from vectorstore
        relevant_doc = self.vectorstore.similarity_search(prompt)
        context = relevant_doc[0].page_content

        # Format the template with the query and current `self.human_ai_history`
        formatted_template = self.template.format(context=context, history=self.human_ai_history, question=prompt)

        # Get response from LLM
        response = self.llm(formatted_template)

        # Extract `self.human_ai_history` from `response`
        formatted_response = response.find("</hs>\n------") + len("</hs>\n------")
        new_history = response[formatted_response:]

        # Append new interaction to `self.human_ai_history`
        if self.human_ai_history:
            self.human_ai_history += f"\n{new_history}"
        else:
            self.human_ai_history = new_history

        return response
