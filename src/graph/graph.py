#from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
#from chains.router import question_router, RouteQuery
from nodes.generate import generate
from nodes.retrieve import retrieve
from nodes.route import route
from nodes.conversate import conversate
from graph.state import GraphState

ROUTE = "route"
CONVERSATE = "conversate"
RETRIEVE = "retrieve"
GENERATE = "generate"


def route_question(state):
    task = state["task"]
    if task == "conversate":
        return CONVERSATE
    if task == "medical_records":
        return RETRIEVE


workflow = StateGraph(GraphState)

# nodes
workflow.add_node(ROUTE, route)
workflow.add_node(CONVERSATE, conversate)
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GENERATE, generate)

# edges
workflow.set_entry_point(ROUTE)
workflow.add_conditional_edges(
    ROUTE,
    route_question,
    {CONVERSATE: CONVERSATE, RETRIEVE: RETRIEVE},
)
workflow.add_edge(CONVERSATE, END)
workflow.add_edge(RETRIEVE, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph_image.png")