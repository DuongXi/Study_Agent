from typing import Annotated,Sequence, TypedDict
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage 
from langgraph.graph.message import add_messages # Hàm thêm message vào state của agent
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int

class Agent():
    def __init__(self, tools, model, prompt):
        self.tools_by_name = {tool.name: tool for tool in tools}
        self.sys_message = SystemMessage(content=prompt)
        self.model = model.bind_tools(tools)
        
    # Node thực hiện các công việc
    def tool_node(self, state: AgentState):
        outputs = []
        for tool_call in state["messages"][-1].tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
    
    # Node gọi mô hình
    def call_model(self, state: AgentState, config: RunnableConfig):
        response = self.model.invoke([self.sys_message] + state["messages"], config)
        return {"messages": [response]}
    
    # Node kiểm tra có nên tiếp tục không
    def should_continue(self, state: AgentState):
        messages = state["messages"]
        if not messages[-1].tool_calls:
            return "end"
        return "continue"

    # Tạo quy trình thực hiện cho một agent
    def create_agent_workflow(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        workflow.add_edge("tools", "agent")
        
        graph = workflow.compile()
        return graph
    
