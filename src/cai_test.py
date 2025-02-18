from chains.conversation import conversation_chain
from chains.tester import evaluator_chain
from cai_chat.cai_chat import run_agent

def eval_agent(question):
    answer = run_agent(query=question, claimnumber='1234', chat_history=[])['generation']
    return evaluator_chain.invoke({"question": question, "answer": answer})

def eval_conversate(question):
    answer = conversation_chain.invoke({"question": question, "chat_history": []})
    return evaluator_chain.invoke({"question": question, "answer": answer})

def test_conversate():
    # Simple assertion test
    response = eval_conversate('Hi, what can you help me with?')
    print(response.Thought)
    assert response.Evaluation == True


def test_agent():
    # Simple assertion test
    response = eval_agent('Has the claimant had any surgery?')
    print(response.Thought)
    assert response.Evaluation == True

print(run_agent(query="Has the claimant had any surgery?", claimnumber='1234', chat_history=[]))
    