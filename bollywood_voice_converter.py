from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model(
    model="openai/gpt-oss-20b",
    model_provider='groq'
)

class VoiceState(TypedDict):
    input: str
    salman_output: str
    sanju_output: str
    jakky_output: str


def salman_voice(state: VoiceState) -> VoiceState:
    prompt = f"""
Convert this sentence into Salman Khan style dialogue:
Text: {state['input']}\n\n

Make it bold, confident, filmy.
"""
    response = model.invoke(prompt)

    return {
        **state,
        "salman_output": response.content
    }


def sanju_voice(state: VoiceState) -> VoiceState:
    prompt = f"""
Convert this sentence into Sanjay Dutt (Sanju Baba) style dialogue:
Text: {state['input']}\n\n

Use Mumbai slang and raw tone.
"""
    response = model.invoke(prompt)

    return {
        **state,
        "sanju_output": response.content
    }


def jakky_voice(state: VoiceState) -> VoiceState:
    prompt = f"""
Convert this sentence into Jackie Shroff style dialogue:
Text: {state['input']}\n\n

Use "bhidu" and street vibe.
"""
    response = model.invoke(prompt)

    return {
        **state,
        "jakky_output": response.content
    }


graph = StateGraph(VoiceState)

graph.add_node('salman_voice', salman_voice)
graph.add_node('sanju_voice', sanju_voice)
graph.add_node('jakky_voice', jakky_voice)

graph.add_edge(START, 'salman_voice')
graph.add_edge('salman_voice', 'sanju_voice')
graph.add_edge('sanju_voice', 'jakky_voice')
graph.add_edge('jakky_voice', END)

workflow = graph.compile()

# result = workflow.invoke({
#     'input': "I am working hard!",
#     'salman_output': "",
#     'sanju_output': "",
#     'jakky_output': ""
# })

# print(result)


import streamlit as st

st.title("Voice Tone Generator (Langgraph Project )")
user_input = st.text_input("Enter your sentence : ")

if st.button("Generate Voice"):
    
    if user_input.strip() == "":
        st.warning("Please Enter the Text")
        
    else:
        result = workflow.invoke({
    'input': "I am working hard!",
    'salman_output': "",
    'sanju_output': "",
    'jakky_output': ""
})

    st.subheader("Salman voice")
    st.write(result['salman_output'])
    
    
    st.subheader("Sanju Voice")
    st.write(result['sanju_output'])
    
    st.subheader('Jakky Voice')
    st.write(result['jakky_output'])
