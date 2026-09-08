from langgraph.graph import StateGraph,START,END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import TypedDict

load_dotenv()
model = init_chat_model(model="openai/gpt-oss-20b",model_provider="groq")

class State(TypedDict):
    
    user_input :str
    symptoms : str
    doctor :str
    med : str
    final_output :str
    

def sympots(state:State) ->State:
    
    prompt = f"Extract the symptoms from : {state['user_input']}"
    result = model.invoke(prompt)
    
    return {'symptoms':result.content }


def doctor(state:State) -> State:
    
    symptoms = state['symptoms'].lower()
    
    
    if 'fever' in symptoms:
        doctor = "General physician"
        
    elif 'skin' in symptoms:
        doctor = 'Dermatologist'
        
    elif 'eye' in symptoms:
        doctor = "opthalmologist"
        
    else:
        doctor = "General Physician"
        
    return {'doctor':doctor}



# medicine suggestion

def medicine_suggestion(state:State) -> State:
    
    symptoms = state['symptoms']
    
    if 'fever' in symptoms:
        
        med = "Paracetemol"
        
    elif 'cold' in symptoms:
        
        med = "Antihistamine"
        
    else:
        med = "Consult Doctor"
        
    return {'med':med}



def final_issue(state : State) -> State:
    
    prompt = f"""
    User issue : {state['user_input']}
    Symptoms : {state['symptoms']}
    Doctor : {state['doctor']}
    Medicine : {state['med']}
    
    Create a Helpful Response.
    
    """
    
    response = model.invoke(prompt)


    return {'final_output':response.content}


graph = StateGraph(State)

graph.add_node("Symptoms",sympots)    
graph.add_node("doctor",doctor)    
graph.add_node("medicine",medicine_suggestion)
graph.add_node("final",final_issue)


graph.add_edge(START,"Symptoms")    
graph.add_edge("Symptoms","doctor")    
graph.add_edge("doctor","medicine")    
graph.add_edge("medicine","final")    
graph.add_edge("final",END)


workflow = graph.compile()

user = workflow.invoke({"user_input": "I have fever and headache"})    

print(user['final_output'])
