from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from llms.llms import llm_4o

llm = llm_4o


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    Thought: str = Field(desription="think about which action to take and why")
    
    Action: str = Field(
        description="The name of the action to take",
    )

structured_llm_router = llm.with_structured_output(RouteQuery)

system = """ You are a helpful workers comp insurance claims assistant. You have access to the following actions:
{action_descriptions}

Your job is to decide what action to take next based on the input from the user.

Glossary:
EE - Employee
IW - Injured Worker

Use the chat history, if provided, to get more context about the user input.
Begin!
""" 
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
         MessagesPlaceholder("chat_history"),
        ("human", "User Input: {question}")
    ]
)

question_router = route_prompt | structured_llm_router