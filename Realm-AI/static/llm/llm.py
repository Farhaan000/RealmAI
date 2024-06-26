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
        
    def generate_context_aware_prompt(self, prompt: str) -> str:
        print("self.human_ai_history: ", self.human_ai_history)
        print("-----------------------------------------------------------------")

        questions = re.findall(r"Question:", self.human_ai_history)
        answers = re.findall(r"Answer:", self.human_ai_history)

        # Check if the number of occurrences is greater than 3
        if len(questions) > 8 and len(answers) > 8:
            # Find the index of the first occurrence of "Question:" and "Answer:"
            question_index = self.human_ai_history.find("Question:")
            answer_index = self.human_ai_history.find("Answer:")
            
            # Find the end of the first "Answer:" to remove the entire Q&A pair
            end_of_first_answer = self.human_ai_history.find("Answer:", answer_index + len("Answer:")) if answer_index != -1 else -1
            
            if question_index != -1 and end_of_first_answer != -1:
                # Remove the first Q&A pair
                self.human_ai_history = self.human_ai_history[end_of_first_answer:].strip()


        print("self.human_ai_history after trnucation: ", self.human_ai_history)
        ("-----------------------------------------------------------------")
        regex_history = re.findall(r"Question:(.*?)(?:Question:|Answer:|$)", self.human_ai_history, re.DOTALL)

        # Join captured groups into formatted questions
        extracted_questions = "\n".join(f"Question:{question.strip()}" for question in regex_history)

        print("extracted_questions :", extracted_questions)
        print("-----------------------------------------------------------------")
        
        context_aware_template = (
            "Here are the previous questions user has asked:\n\n"
            "Previous-Questions:\n{extracted_questions}\n\n"
            "In this current question '{question}' , "
            "replace pronoun with noun by utilizing the Previous-Questions and provide context aware new question. if there is no Previous-Questions repeat the new question as it is."
            "AI-Question:"
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
            "replace pronoun with noun by utilizing the Previous-Questions and provide context aware new question. if there is no Previous-Questions repeat the new question as it is."
        )[-1]
        print("partitioned_prompt: ", partitioned_prompt)
        ("-----------------------------------------------------------------")
        # Find the starting index of the AI-Question
        start_index = partitioned_prompt.find("AI-Question:\n") + len("AI-Question:\n")
        print("start_index:", start_index)
        # Find the ending index of the AI-Question section
        end_index = partitioned_prompt.find("\n\n", start_index)
        print("end_index:", end_index)
        # Extract the AI-Question part
        context_aware_prompt_part = partitioned_prompt[start_index:end_index].strip()

        print("Context aware prompt part:", context_aware_prompt_part)
        print("-----------------------------------------------------------------")

        if self.vectorstore is None:
            return "No relevant documents found. FAISS index is not available."
        
        relevant_doc = self.vectorstore.similarity_search(context_aware_prompt_part)
        context = relevant_doc[0].page_content

        # Format the template with the query and current `self.human_ai_history`
        formatted_template = self.template.format(context=context, history=self.human_ai_history, question=prompt)

        num_tokens = self.count_tokens(formatted_template)
        print(f"Number of tokens: {num_tokens}")

        # Get response from LLM
        llm_response = self.llm(formatted_template)

        filtered_response_start = llm_response.rfind("Answer:") + len("Answer:")
        response = llm_response[filtered_response_start:].strip()

        # Extract `self.human_ai_history` from `response`
        formatted_response = response.find("</hs>\n------") + len("</hs>\n------")
        new_history = response[formatted_response:].strip()

        # Append new interaction to `self.human_ai_history`
        if self.human_ai_history:
            self.human_ai_history += f"\n{new_history}"
        else:
            self.human_ai_history = new_history

        return response
