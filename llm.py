from langchain_community.llms import HuggingFaceHub
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import re

load_dotenv()

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
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            model_kwargs={"temperature": 0.1, "max_length": 1000})

        self.vectorstore = FAISS.load_local("faiss_index", self.huggingface_embeddings, allow_dangerous_deserialization=True)

    def generate_context_aware_prompt(self, prompt: str) -> str:
        # print("self.human_ai_history: ", self.human_ai_history)
        # print("-----------------------------------------------------------------")

        # Use re.findall() to find all matches in the text
        regex_history = re.findall(r"Question:\n.*?\?", self.human_ai_history, re.DOTALL)

        # Join the extracted questions into a single string
        extracted_questions = "\n".join(regex_history)

        print("Extracted Questions:", extracted_questions)
        print("-----------------------------------------------------------------")
        
        context_aware_template = (
            "Here is the history of questions user has asked:\n\n"
            "History:\n{extracted_questions}\n\n"
            "If this new question '{question}' is a follow-up question to the history of questions, "
            "then replace pronouns with nouns by utilizing the history of questions . If this new question '{question}' is a standalone question, repeat the same new question as it is. "
            "Make sure there is no explanation in AI-prompt\n"
            "AIprompt:"
        )

        # print("context_aware_template: ", context_aware_template)
        
        formatted_template = context_aware_template.format(
            extracted_questions=extracted_questions,
            question=prompt
        )
        
        context_aware_prompt = self.llm(formatted_template)
        return context_aware_prompt

    def llm_invoker(self, prompt: str):
        # Generate a context-aware prompt
        context_aware_prompt = self.generate_context_aware_prompt(prompt)
        
        # Get relevant document from vectorstore using context-aware prompt
        print("RelevantDoc ContextAwarePrompt:", context_aware_prompt)
        print("-----------------------------------------------------------------")
        partitioned_prompt = context_aware_prompt.rpartition(
            "is a follow-up question to the history of questions, then construct an AI-prompt accordingly. "
            "If it is a standalone question, repeat the same new question as it is. Make sure there is no explanation in AI-prompt"
        )[-1]

        start_index = partitioned_prompt.find("AIprompt:") + len("AIprompt:")
        context_aware_prompt_part = partitioned_prompt[start_index:].strip()
        print(f"context_aware_prompt_part: {context_aware_prompt_part}")
        print("-----------------------------------------------------------------")

        relevant_doc = self.vectorstore.similarity_search(context_aware_prompt_part)
        context = relevant_doc[0].page_content

        # Format the template with the query and current `self.human_ai_history`
        formatted_template = self.template.format(context=context, history=self.human_ai_history, question=prompt)

        # Get response from LLM
        response = self.llm(formatted_template)

        # Extract `self.human_ai_history` from `response`
        formatted_response = response.find("</hs>\n------") + len("</hs>\n------")
        new_history = response[formatted_response:].strip()

        # Append new interaction to `self.human_ai_history`
        if self.human_ai_history:
            self.human_ai_history += f"\n{new_history}"
        else:
            self.human_ai_history = new_history

        return response
