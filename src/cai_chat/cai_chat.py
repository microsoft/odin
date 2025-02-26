from graph.graph import app
from typing import List, Any, Dict
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def run_agent(query: str, claimnumber: str, chat_history: List[Dict[str, Any]] = []):
    #  https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry
    with tracer.start_as_current_span("call_open_ai") as span:
        # span.set_attribute("langsmith.span.kind", "LLM")
        # span.set_attribute("langsmith.metadata.user_id", "user_123")
        span.set_attribute("gen_ai.system", "az.ai.inference")
        # span.set_attribute("gen_ai.request.model", model)
        # span.set_attribute("llm.request.type", "chat")
        # for i, message in enumerate(messages):
        #     span.set_attribute(f"gen_ai.prompt.{i}.content", str(message["content"]))
        #     span.set_attribute(f"gen_ai.prompt.{i}.role", str(message["role"]))

        result = app.invoke(
            {
                "question": query,
                "chat_history": chat_history,
                "documents": None,
                "claimnumber": claimnumber,
            }
        )

        # span.set_attribute("gen_ai.response.model", completion.model)
        # span.set_attribute("gen_ai.completion.0.content", str(completion.choices[0].message.content))
        # span.set_attribute("gen_ai.completion.0.role", "assistant")
        # span.set_attribute("gen_ai.usage.prompt_tokens", completion.usage.prompt_tokens)
        # span.set_attribute("gen_ai.usage.completion_tokens", completion.usage.completion_tokens)
        # span.set_attribute("gen_ai.usage.total_tokens", completion.usage.total_tokens)

        return result
