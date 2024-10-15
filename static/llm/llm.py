from langchain_community.llms import HuggingFaceHub
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import re
import tiktoken
from pathlib import Path

load_dotenv()

class LLMInvoker:
    def __init__(self):
        self.human_ai_history = ""
        self.extracted_prompts = ""
        self.template = """
Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question, if the answer is not found in the context and chat history say "Please ask questions relevant to Farhaan!":
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

        faiss_index_path = Path("faiss_index/index.faiss")
        if faiss_index_path.exists():
            self.vectorstore = FAISS.load_local("faiss_index", self.huggingface_embeddings, allow_dangerous_deserialization=True)
        else:
            self.vectorstore = None
            print("FAISS index file not found. Vectorstore is not initialized.")
        
        self.tokenizer = tiktoken.get_encoding("gpt2")

    def count_tokens(self, text: str) -> int:
        tokens = self.tokenizer.encode(text)
        return len(tokens)
        
    def generate_context_aware_prompt(self, prompt: str = None, lim_llm_response = None, lim_llm_contextual_question = None, lim_llm_invoker=None) -> str:
        print("prompt in LLMInvoker: ", prompt)
        print("lim_llm_response in LLMInvoker: ", lim_llm_response)
        if prompt is None:
            prompt = ""
        if lim_llm_response is not None:
            self.human_ai_history += f"\nQuestion: {prompt}\nAnswer: {lim_llm_response}"
            print("LLM self.human_ai_history after adding lim_llm_response in LLMInvoker: ", lim_llm_response)
            return
        print("lim_llm_contextual_question in LLMInvoker: ", lim_llm_contextual_question)
        if lim_llm_contextual_question is not None:
            self.extracted_prompts += f"\n{lim_llm_contextual_question}"
            print("self.extracted_prompts after adding lim_llm_contextual_question in LLMInvoker: ", lim_llm_contextual_question)
        print("LLM self.human_ai_history: ", self.human_ai_history)
        print("-----------------------------------------------------------------")
    
        questions = re.findall(r"Question:.*?(?=Answer:|$)", self.human_ai_history, re.DOTALL)
    
        # Check if the number of occurrences is greater than 8
        if len(questions) > 8:
            # Find the end of the first "Question:" to remove the entire Q&A pair
            end_of_first_question = self.human_ai_history.find("Answer:", self.human_ai_history.find("Question:")) if self.human_ai_history.find("Question:") != -1 else -1
    
            if end_of_first_question != -1:
                # Remove the first Q&A pair
                self.human_ai_history = self.human_ai_history[end_of_first_question:].strip()
    
        # print("self.human_ai_history after truncation: ", self.human_ai_history)
        print("-----------------------------------------------------------------")
    
        regex_history = re.findall(r"Question:(.*?)(?=Question:|Answer:|$)", self.human_ai_history, re.DOTALL)
    
        context_aware_template = (
            "Here are the questions user has asked:\n\n"
            "Previous-Questions:\n{extracted_questions}\n\n"
            "In this current question '{question}' , "
            "replace pronoun with noun by utilizing the Previous-Questions and provide context aware new question. if there is no Previous-Questions repeat the new question as it is."
            "AI-Question:"
        )
    
        formatted_template = context_aware_template.format(
            extracted_questions=self.extracted_prompts,
            question=prompt
        )
    
        context_aware_prompt = self.llm(formatted_template)

        print("RelevantDoc ContextAwarePrompt:", context_aware_prompt)
        # print("-----------------------------------------------------------------")
        partitioned_prompt = context_aware_prompt.rpartition(
            "replace pronoun with noun by utilizing the Previous-Questions and provide context aware new question. if there is no Previous-Questions repeat the new question as it is."
        )[-1]
        # print("partitioned_prompt: ", partitioned_prompt)
        # ("-----------------------------------------------------------------")
        start_index = partitioned_prompt.find("AI-Question:\n") + len("AI-Question:\n")
        # print("start_index:", start_index)
        end_index = partitioned_prompt.find("\n\n", start_index)
        # print("end_index:", end_index)
        context_aware_prompt_part = partitioned_prompt[start_index:end_index].strip()
        print("context_aware_prompt_part : ", context_aware_prompt_part)
        print("-----------------------------------------------------------------")
        if self.extracted_prompts:
            self.extracted_prompts += f"\n{context_aware_prompt_part}"
        else:
            self.extracted_prompts = context_aware_prompt_part
        print("LLM self.extracted_prompts which is now extracted from Context aware prompt part:", self.extracted_prompts)
        print("-----------------------------------------------------------------")
        
        if lim_llm_invoker:
            lim_llm_invoker.generate_context_aware_prompt(llm_contextual_question= context_aware_prompt_part)
        return context_aware_prompt_part

    def llm_invoker(self, prompt: str, lim_llm_invoker=None):
        context_aware_prompt_part = self.generate_context_aware_prompt(prompt, lim_llm_invoker=lim_llm_invoker)
        print("entire context_aware_prompt_part before performing similarity_search : ", context_aware_prompt_part)
        
        if self.vectorstore is None:
            return "No relevant documents found. FAISS index is not available."
        
        relevant_doc = self.vectorstore.similarity_search(context_aware_prompt_part)
        context = relevant_doc[0].page_content
        print("entire context after performing similarity_search : ", context)

        formatted_template = self.template.format(context=context, history=self.human_ai_history, question=prompt)

        num_tokens = self.count_tokens(formatted_template)
        # print(f"Number of tokens: {num_tokens}")

        # print("formatted_template :", formatted_template)

        response = self.llm(formatted_template)

        filtered_response_start = response.rfind("Answer:") + len("Answer:")
        llm_response = response[filtered_response_start:].strip()

        formatted_response = response.find("</hs>\n------") + len("</hs>\n------")
        new_history = response[formatted_response:].strip()

        if self.human_ai_history:
            self.human_ai_history += f"\n{new_history}"
        else:
            self.human_ai_history = new_history

        return llm_response
