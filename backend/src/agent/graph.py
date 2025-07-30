import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState

from src.agent.prompt import *
from src.agent.react_agent import Agent
from src.agent.model_config import LLM_MODELS
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"]=os.getenv("GEMINI_API_KEY")

# Langsmith tracing để kiểm thử
os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"]="study-agent"

class GraphState(MessagesState):
    chat_history: list
    summary: str
    
class Graph():
    def __init__(self, model, tools):
        self.llm_json_mode = ChatGroq(model="llama-3.3-70b-versatile", temperature=0).with_structured_output(method="json_mode", include_raw=True)
        if model in LLM_MODELS["google-gemini"]:
            self.llm = ChatGoogleGenerativeAI(model=model,temperature=0.5)
        elif model in LLM_MODELS["groq"]:
            self.llm = ChatGroq(model=model, temperature=0.5,)
        else:
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7,)
        self.toolkit = tools
        self.setup_agent()

    # Cuộc hội thoại thông thường
    def normal_conversation(self, state: GraphState) -> Dict[str, Any]:
        summary = state.get("summary", "")
        question = [state["messages"][-1].content]
        if summary:
            summary_message = f"Tóm tắt cuộc hội thoại từ trước: {summary}"

            messages = [SystemMessage(content = summary_message + NORMAL_CONV_INSTRUCTION)] + question
        else:
            messages = [SystemMessage(content = NORMAL_CONV_INSTRUCTION)] + question

        generation = self.llm.invoke(messages)
        return {"messages": generation}

    # Lựa chọn nguồn thông tin
    def route_question(self, state: GraphState) -> str:
        summary = state.get("summary", "")
        router_instruction_formatted = ROUTER_INSTRUCTION.format(summary=summary)
        route_question = self.llm_json_mode.invoke(
            [SystemMessage(content=router_instruction_formatted)]
            + [state["messages"][-1].content]
        )
        source = json.loads(route_question["raw"].content)["source"]
        if source == "assistant":
            return "assistant"
        elif source == "normal-conversation":
            return "normal_conversation"
        else:
            return END

    # Tóm tắt cuộc hội thoại
    def summarize_conversation(self, state: GraphState) -> Dict[str, Any]:
        summary = state.get("summary", "")

        if summary:
            summary_message = (f"""
                               Đây là tóm tắt cuộc hội thoại cho đến hiện tại: {summary}\n\n
                               Mở rộng bản tóm tắt bằng cách lưu ý đến các thông điệp mới ở trên và cả hiện tại, không cần nói gì thêm:
                               """)
        else:
            summary_message = "Tạo một bản tóm tắt của cuộc hội thoại trên và không cần nói gì thêm: "

        messages = state["messages"] + [HumanMessage(content=summary_message)]
        response = self.llm.invoke(messages)

        if len(state["messages"]) > 6:
            delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
            return {"summary": response.content, "messages": delete_messages}
        
        return {"summary": response.content}
    
    # Kiểm tra cần tóm tắt cuộc hội thoại không
    def should_summary(self, state: GraphState):

        messages = state["messages"]
        
        if len(messages) > 2:
            return "summarize_conversation"
        
        return END

    # Tạo quy trình thực hiện cho trợ lý ảo
    def setup_agent(self):
        if len(self.toolkit) == 1:
            assistant = Agent(tools=self.toolkit, model=self.llm, prompt=NORMAL_AGENT_INSTRUCTION).create_agent_workflow()
        else:
            assistant = Agent(tools=self.toolkit, model=self.llm, prompt=AGENT_INSTRUCTION).create_agent_workflow()

        graph = StateGraph(GraphState)
        graph.add_node("normal_conversation", self.normal_conversation)
        graph.add_node("assistant", assistant)
        graph.add_node("summarize_conversation", self.summarize_conversation)
        
        graph.set_conditional_entry_point(
            self.route_question,
            {
                "normal_conversation": "normal_conversation",
                "assistant": "assistant",
                END:END
            },
        )

        graph.add_conditional_edges("normal_conversation", self.should_summary, ["summarize_conversation", END])
        graph.add_conditional_edges("assistant", self.should_summary, ["summarize_conversation", END])
        graph.add_edge("summarize_conversation", END)
        memory = MemorySaver()
        self.compiled_graph = graph.compile(checkpointer=memory)

if __name__ == "__main__":
    graph = Graph(model="gemini-2.5-flash-preview-04-17",tools=[])
    message = "Xin chào"
    config = {"configurable": {"thread_id": "1"}}
    for chunk in graph.compiled_graph.stream({
            "messages": [{
                "role": "user",
                "content": "xin chàooo"
                }]},
            stream_mode="updates",
            config=config,
            subgraphs=True
        ):
            message = list(chunk[1].values())[0]
            if list(message.keys()) == ['messages']:
                if type(message["messages"]) == list:
                    print(message["messages"][0].content)
                else:
                    print(message["messages"].content)