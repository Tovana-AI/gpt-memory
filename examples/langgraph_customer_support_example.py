from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv()
import os

from langchain_core.messages import HumanMessage, AIMessage

from memory import MemoryManager

import uuid
from typing import Annotated, Any, Dict

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.graph import END, START
from langgraph.graph.message import MessagesState
from langgraph.graph.state import StateGraph
from langgraph.managed.shared_value import SharedValue
from langgraph.store.memory import MemoryStore

memory_manager = MemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    provider="openai",
    temperature=0.2,
    business_description="""
    You are an advanced AI analyst for a SaaS (Software as a Service) company's customer support team. Your primary functions are:

    1. Action Deduction:
   - Carefully examine the user's messages to infer what troubleshooting steps they've already taken.
   - Look for explicit mentions or implicit hints of actions such as logging out, clearing cache, restarting the application, or updating software.
   - Create a list of likely completed actions to avoid redundant suggestions.

    2. Emotional State Analysis:
   - Assess the user's emotional state throughout the conversation.
   - Identify indicators of:
     a) Frustration: use of caps, exclamation points, or words expressing anger or impatience
     b) Satisfaction: positive language, expressions of gratitude, or indications of problem resolution
     c) Confusion: questions, requests for clarification, or expressions of uncertainty
     d) Urgency: mentions of deadlines, time sensitivity, or requests for immediate assistance

    3. Service Satisfaction Evaluation:
   - Gauge the user's overall satisfaction with the support service.
   - Look for:
     a) Positive indicators: compliments about the service, expressions of relief or happiness
     b) Negative indicators: complaints about response time, mentions of considering alternative services, or threats to cancel

    4. Interaction Efficiency:
   - Evaluate how quickly and effectively the user's issue is being addressed.
   - Note any instances where the user had to repeat information or where misunderstandings occurred.

    5. Technical Proficiency Assessment:
   - Infer the user's level of technical expertise based on their language and described actions.
   - This helps tailor future responses to their level of understanding.

    6. Issue Categorization:
   - Classify the type of problem the user is experiencing (e.g., login issues, feature malfunction, billing question).
   - Identify if this is a recurring issue for the user or a first-time problem.

    Output your analysis in a structured format, including:
    - Likely completed troubleshooting steps
    - Current emotional state
    - Overall satisfaction level
    - Interaction efficiency rating
    - Assessed technical proficiency
    - Issue category and frequency

    This analysis will be used to improve our customer support strategies and personalize future interactions with the user.
    """,
    include_beliefs=True,
)


class AgentState(MessagesState):
    # We use an info key to track information
    # This is scoped to a user_id, so it will be information specific to each user
    user_id: str
    info: Annotated[dict, SharedValue.on("user_id")]


prompt = """.
You are an AI customer support assistant for a large e-commerce company. Your role is to provide helpful, friendly, and efficient support to customers.
You should:
Greet customers politely and ask how you can assist them.

Understand and address customer inquiries or issues related to orders, products, shipping, returns, and general policies.
Access and provide accurate information about products, order statuses, and company policies.

Offer solutions to common problems and guide customers through troubleshooting steps when necessary.
Use a tone that is professional, empathetic, and patient.
Apologize sincerely when appropriate, but avoid admitting fault on behalf of the company.

Escalate complex issues to human support when needed, explaining the process to the customer.
Protect customer privacy by never sharing or requesting sensitive personal information.
Conclude interactions by asking if there's anything else you can help with and thanking the customer.
Aim to resolve issues in as few interactions as possible while ensuring customer satisfaction.

Remember, your goal is to provide excellent customer service that reflects positively on the company. 
If you're unsure about any information, it's better to offer to check and get back to the customer rather than provide incorrect details."

If you feel the user is an experienced and has technical knowledge,
don't suggest anything, let them know you understand they are technical
and tell them that right away you are escalate the case to a human


Here is what you know about the user:

<info>
{info}
</info>

Help out the user.
Notice most issues will be resolved with a simple logout + clear cache + login

"""


@tool
def escalate_case(user_id: str, issue: str) -> None:
    """
    Use this function in case you want to escalate the case to a human
    :param user_id:
    :param issue:
    :return: None
    """
    print(f"decided to escalate {user_id}'s case \n {issue=} ")


def escalate_case2(state):
    print(f"decided to escalate {state['user_id']}")
    return {"messages": [AIMessage(content="Escalation tool called")]}


model = ChatOpenAI().bind_functions([escalate_case])

tool_node = ToolNode([escalate_case])


def call_model(state):
    facts = [d["fact"] for d in state["info"].values()]
    info = "\n".join(facts)
    system_msg = prompt.format(info=info)
    response = model.invoke(
        [{"role": "system", "content": system_msg}] + state["messages"]
    )
    print(f"AI: {response.content}")
    return {
        "messages": [response],
    }


def get_user_input(state: AgentState) -> Dict[str, Any]:
    information_from_stdin = str(input("\nHuman: "))
    return {"messages": [HumanMessage(content=information_from_stdin)]}


def route(state):
    num_human_input = sum(1 for message in state["messages"] if message.type == "human")
    if isinstance(state["messages"][-1], AIMessage):
        if state["messages"][-1].additional_kwargs.get("function_call"):
            return "escalate_case2"
    if num_human_input < 4:
        return "not_enough_info"
    if num_human_input == 4:
        return "enough_user_input"

    else:
        return END


def route2(state):
    if isinstance(state["messages"][-1], AIMessage):
        if state["messages"][-1].additional_kwargs.get("function_call"):
            return "escalate_case2"
    if isinstance(state["messages"][-2], AIMessage):
        if state["messages"][-2].additional_kwargs.get("function_call"):
            return "escalate_case2"
    if isinstance(state["messages"][-3], AIMessage):
        if state["messages"][-3].additional_kwargs.get("function_call"):
            return "escalate_case2"
    return "call_model"


def update_memory(state):
    memories = {}
    memory_manager.batch_update_memory(state["user_id"], state["messages"])
    memory_context = memory_manager.get_memory_context(user_id=state["user_id"])
    memories[state["user_id"]] = {"fact": memory_context}
    print(f"# Tovana memory saved.. \n # {memory_context}")
    return {"messages": [AIMessage(content="Tovana Memory Saved")], "info": memories}


memory = MemorySaver()

kv = MemoryStore()

graph = StateGraph(AgentState)
graph.add_node(call_model)
graph.add_node(escalate_case2)
graph.add_node(update_memory)
graph.add_node(get_user_input)
graph.add_edge(START, "get_user_input")

# graph.add_edge("update_memory", "call_model")
graph.add_edge(START, "get_user_input")
graph.add_edge("get_user_input", "call_model")
graph.add_conditional_edges(
    "call_model",
    route,
    {
        "not_enough_info": "get_user_input",
        "enough_user_input": "update_memory",
        "escalate_case2": "escalate_case2",
        END: END,
    },
)
graph.add_conditional_edges(
    "update_memory",
    route2,
    {
        "call_model": "call_model",
        "escalate_case2": "escalate_case2",
    },
)
graph.add_edge("escalate_case2", END)
graph = graph.compile(checkpointer=memory, store=kv)
graph.get_graph().draw_mermaid_png(output_file_path="graph_2.png")

user_id = str(uuid.uuid4())

if __name__ == "__main__":
    print("##############################################")

    config = {"configurable": {"thread_id": "1", "user_id": user_id}}
    res = graph.invoke({"user_id": user_id}, config=config)

    print(
        "################## 1 hour later... Starting new thread.... ##################"
    )
    config = {"configurable": {"thread_id": "2", "user_id": user_id}}
    res2 = graph.invoke({"user_id": user_id}, config=config)
    print(res2)
