from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel,Field
from langchain.chat_models import init_chat_model
from typing import TypedDict,Literal
from dotenv import load_dotenv



load_dotenv()

model = init_chat_model(model="openai/gpt-oss-safeguard-20b",model_provider="groq")

class SentimentSchema(BaseModel):

    sentiment : Literal['positive','negative'] = Field(description='sentiment of the review')


structured_model = model.with_structured_output(SentimentSchema)


p = "what is the sentiment of the following review - software very good"
response = structured_model.invoke(p).sentiment


class ReviewState(TypedDict):
    
    review : str
    sentiment : Literal['positive','negative']
    dignosis: dict
    response : str


class DiagnosisSchema(BaseModel):
    issue_type:Literal['UX',"Performance","Bug","Support","Other"] = Field(description='The category of issue mentioned in the review') 
    tone:Literal['angry',"frusted","disappointed","calm"] = Field(description='The emothional tone expressed by the user') 
    urgency:Literal['Low',"medium","high"] = Field(description='How urgent or critical the issue appears to be') 
    
    
    
def find_sentiment(state : ReviewState):
    
    prompt = f"For the following review find out the sentiment \n {state['review']} "
    sentiment = structured_model.invoke(prompt).sentiment
    
    return {'sentiment':sentiment}


def check_sentiment(state: ReviewState) ->Literal["positive_response",'run_diagnosis']:
    
    if state['sentiment'] == 'positive':
        return "positive_response"


    else:
        return "run_diagnosis"

def positive_respones(state:ReviewState):
    prompt = f"""
        Write a warm thank-you message in response to this review:
        \n\n\"{state['review']}\"\n
    Also, kindly ask the user to leave feedback on our website."""
    

    response = model.invoke(prompt).content
    
    return {'reponse':response}


def run_diagnosis(state:ReviewState):
    
    prompt = f"""Diagnosis this negative review : \n\n {state['review']}\n Return issue_type ,tone,and urgency."""

    response = structured_model2.invoke(prompt)
    
    return {'diagnosis':response.model_dump()}


def negative_response(state:ReviewState):
    
    prompt = f"""You are a support assistant.
                The user had a'diagnosis['issue_type'] issue,sounded '{dignosis['tone']}',and marked urgence
    """


graph = StateGraph(ReviewState)

graph.add_node("find_sentiment",find_sentiment)

graph.add_edge(START,"find_sentiment")
graph.add_edge("find_sentiment",END)


workflow = graph.compile()


initial_state = {
    'review':'The Product was really good'
}

response = workflow.invoke(initial_state)

print(response)
