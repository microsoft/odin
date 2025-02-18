from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from llms.llms import llm_4o


llm = llm_4o


class EvalBool(BaseModel):
    """Evaluate the validity of an answer to a question"""

    Thought: str = Field(
        json_schema_extra={'description':"think about your response"}
        )
    
    Evaluation: bool = Field(
        json_schema_extra={"description": "Is the answer valid, given the question?. Evaluation shoud be True or False"}
    )

structured_llm_evaluator = llm.with_structured_output(EvalBool)


system = """ 
You are an AI that evaluates the validity of answers to questions
Given the question: {question}
And the answer: {answer}

Your job is to decide if the answer is valid. 
Your evaluation should only be 'False' if the answer makes no sense within the context of the question.


Begin!
""" 
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
    ]
)

evaluator_chain = route_prompt | structured_llm_evaluator


