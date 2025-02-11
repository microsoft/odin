from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import List, Tuple, Union, Dict
from langchain_core.documents import Document
from llms.llms import llm_4o


llm = llm_4o

system = """
You are an assistant specialized in question-answering tasks.  

Instructions:
1. Contextual Understanding: Use the chat history, if provided, to understand the question.  
2. Answer Scope: Only answer parts of the question that can be addressed with the given context. Do not include information beyond what is provided.  
3. Source Attribution: reference each source you used to answer the questions in a bullet point list at the end of your answer. References should include DocumentName and PageNumber 

Begin!
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history"),
        ("human", "Question: {question} \n\n Context: {context} \n\n Answer:"),
    ]
)

parser = StrOutputParser()

generation_chain = prompt | llm | parser