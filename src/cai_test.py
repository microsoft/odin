from chains.evaluator import evaluator_chain
from graph.state import GraphState
from cai_chat.cai_chat import run_agent
from nodes.retrieve import retrieve
from nodes.conversate import conversate
from nodes.route import route
from nodes.retrieve import retrieve
from nodes.generate import generate

##################
# Test Router
##################

def run_router(state):
    return route(state)['task']

def test_router():
    # test conversate route
    state = GraphState({'question': 'Hi, what can you help me with?',
         'chat_history': [],
         'documents': None,
         'claimnumber': '1234'})
    response = run_router(state)
    assert response == 'conversate'
    # Test rag route
    state['question'] = 'Has the claimant had any surgery?',
    response = run_router(state)
    assert response == 'medical_records'

##################
# Test Conversate
##################

def eval_conversate(state, context):
    question = state['question']
    answer = conversate(state)['generation']
    return evaluator_chain.invoke({"question": question, "answer": answer, 'context': context})

def test_conversate():
    state = GraphState({'question': 'Hi, what can you help me with?',
         'chat_history': [],
         'documents': None,
         'claimnumber': '1234'})
    context = "a claims manager asking how a claims AI assistant can help"
    response = eval_conversate(state, context)
    print(response.Thought)
    assert response.Evaluation == True

##################
# Test RAG
##################

def retrieve_docs(state):
    return retrieve(state)['documents']

def eval_generation(state, context):
    question = state['question']
    answer = generate(state)['generation']
    return evaluator_chain.invoke({"question": question, "answer": answer, 'context': context})

def test_rag():
    state = GraphState({'question': 'Has the claimant had any surgery?',
         'chat_history': [],
         'documents': None,
         'claimnumber': '1234'})
    docs = retrieve_docs(state)
    assert isinstance(docs, list)
    state['documents'] = docs
    context = 'a user asking for information about any surgeries a claimant has had'
    response = eval_generation(state, context)
    print(response.Thought)
    assert response.Evaluation == True

##################
# TestAgent
##################

def eval_agent(question, context):
    answer = run_agent(query=question, claimnumber='1234', chat_history=[])['generation']
    return evaluator_chain.invoke({"question": question, "answer": answer, 'context': context})

def test_agent():
    context = 'a user asking for information about any surgeries a claimant has had'
    response = eval_agent('Has the claimant had any surgery?', context)
    print(response.Thought)
    assert response.Evaluation == True