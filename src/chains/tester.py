from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from llms.llms import llm_4o


llm = llm_4o


from pydantic import BaseModel, Field

class EvalBool(BaseModel):
    """Evaluate the validity of an answer to a question."""
    
    Thought: str = Field(
        json_schema_extra={
            "description": "Provide an explanation of your reasoning for this evaluation."
        }
    )
    
    Evaluation: bool = Field(
        json_schema_extra={
            "description": "Return True if the answer addresses the question; otherwise, return False."
        }
    )

structured_llm_evaluator = llm.with_structured_output(EvalBool)

system = """
You are an AI evaluator tasked with analyzing whether a provided answer properly addresses a given question.
Here are the inputs:
- Question: {question}
- Answer: {answer}

Please think through the context and details of the question and answer. In your response:
1. Explain your reasoning in the "Thought" field.
2. Set "Evaluation" to True if the answer is reasonable and relevant; otherwise, set it to False.

Begin your analysis now!
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
    ]
)

evaluator_chain = route_prompt | structured_llm_evaluator


