from langgraph.graph import START,END,StateGraph
from langchain.chat_models import init_chat_model
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langchain.messages import HumanMessage,AIMessage,SystemMessage
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()
model = init_chat_model(model="openai/gpt-oss-20b",model_provider='groq')

from langgraph.graph.message import add_messages
class ChatState(TypedDict):
    
    messages : Annotated[list[BaseMessage],add_messages]
    
def chat_node(state:ChatState):
    # take user query from state
    messages = state['messages']
    
    
    # send to llm
    response = model.invoke(messages)
    
    # response store state
    
    return {'messages':[response]}

checkpointer = MemorySaver()


graph = StateGraph(ChatState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)


chatbot = graph.compile(checkpointer=checkpointer)


initial_state = {
    'messages':[HumanMessage(content="What is the capital of india?")]
}

# result = chatbot.invoke(initial_state)

result = chatbot.invoke(initial_state, config={'configurable': {'thread_id': '1'}})

# print(result['messages'][-1].content)

thread_id = '1'

while True:
    
    user_input = input("Type here :  ")

    if user_input.strip().lower() in ['exit','quit','bye']:
        break
    
    config = {'configurable':{'thread_id':thread_id}}
    
    response = chatbot.invoke(
    {'messages': [HumanMessage(content=user_input)]},
    config=config
    )
    
    print("AI : ",response['messages'][-1].content)
    
print(chatbot.get_state(config=config))
