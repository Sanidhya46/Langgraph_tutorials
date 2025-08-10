from langgraph.graph import StateGraph , START , END
from langchain import runnables
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint , HuggingFacePipeline
import os
from typing import TypedDict
from pydantic import BaseModel , Field
from langchain.output_parsers import StructuredOutputParser , PydanticOutputParser
import json
from langchain.prompts import PromptTemplate

api_key = os.getenv('HUGGINGFACEHUB_API_KEY')

llm = HuggingFaceEndpoint(
    repo_id = "google/gemma-2-2b-it",
    task= "text-generation",
    huggingfacehub_api_token= api_key,  # ✅ THIS IS CRITICAL!

)

model = ChatHuggingFace(llm = llm)


from typing import Literal 
class Schema(BaseModel):

    sentiment: Literal["positive","negative"] = Field(description='Tell me the review is negative or positive....')
    score: int = Field(descripxtion='Score out of 10 how worst the review the more worst is 10 out of 10', ge=0, le=10)

parser = PydanticOutputParser(pydantic_object = Schema)

template = PromptTemplate(
    template= 'give the review and clarify the review  {review} and give the output in sentiment is it positive or negative and what is worst review score \n {format_instruction}',
    input_variables= ['review'],
    partial_variables = {'format_instruction' : parser.get_format_instructions()}
)

prompt = template.invoke({'your product is worst i ever used ....  '})

sentiment_chain = template | model | parser

final_result = sentiment_chain.invoke(prompt)

class Finalstate(TypedDict):
    sentiment: str      # ✅ Add this
    score: int  
    review : str
    issue_type : str
    tone : str
    urgency : str
    result : str

def find_sentiment(state: Finalstate):
    review_text = state['review']
    prompt_input = {'review': review_text}

    result = sentiment_chain.invoke(prompt_input)  # returns a Pydantic object (Schema)
    print("Result type:", type(result))
    print("Result content:", result)

    return {
        'sentiment': result.sentiment,  # ✅ object attribute access
        'score': result.score
    }
   


def run_diagnosis(state: Finalstate):
    prompt = f"""
    Analyze the following customer review and answer these three things:

    1. Issue Type – is it about product quality, delivery, price, etc.?
    2. Tone – is the tone aggressive, soft, neutral, unsatisfied, etc.?
    3. Urgency – does the user express urgency or not?

    Review: {state['review']}

    Respond in this JSON format:
    {{
      "issue_type": "<type>",
      "tone": "<tone>",
      "urgency": "<urgency>"
    }}
    """

    result = model.invoke(prompt)  # Make sure 'model' is defined globally or passed in
    return {'result': result}

def run_diagnosis(state: Finalstate):
    prompt = f"""
    Analyze the following customer review and answer these three things:

    1. Issue Type – is it about product quality, delivery, price, etc.?
    2. Tone – is the tone aggressive, soft, neutral, unsatisfied, etc.?
    3. Urgency – does the user express urgency or not?

    Review: {state['review']}

    Respond in this JSON format:
    {{
      "issue_type": "<type>",
      "tone": "<tone>",
      "urgency": "<urgency>"
    }}
    """

    result = model.invoke(prompt)  # Make sure 'model' is defined globally or passed in
    return {'result': result}

def negative_response(state: Finalstate):
    prompt = f"""
    Analyze the following customer review and answer these three :
    Generate the particular
    

    Review: {state['review']}

    Respond in this JSON format:
    {{
      "issue_type": "<type>",
      "tone": "<tone>",
      "urgency": "<urgency>"
    }}
    """

    result = model.invoke(prompt)  # Make sure 'model' is defined globally or passed in
    return {'result': result}

def positive_response(state: Finalstate):

    prompt = f"""
    Analyze the following customer review and answer these three things:
     
    Give the reply for positive experience in the polite way as polite as possible ... and tell them on next time we take care about this 
     

    Review: {state['review']}

    Respond in this JSON format:
    {{
      
      "reply": "<reply>"
    }}
    """

    result = model.invoke(prompt)  # Make sure 'model' is defined globally or passed in
    return {'result': result}

def generate_reply(state: Finalstate):
    prompt = f"""
You are a helpful customer support assistant. Based on the extracted feedback details below, write a professional and empathetic reply to the customer.

Details:
- Issue Type: {state['result']['issue_type']}
- Tone: {state['result']['tone']}
- Urgency: {state['result']['urgency']}

Guidelines:
- If tone is angry/frustrated/disappointed → start with an apology.
- If urgency is urgent → offer quick help or escalation.
- Mention the issue type in the reply.
- Keep it clear, respectful, and reassuring.

Return only the customer reply message. No formatting, no extra text.
"""

    result = model.invoke(prompt)
    return {'reply': result}

def check_condition(state: Finalstate) -> Literal["run_diagnosis", "positive_response"]:

    if state['sentiment'] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"
    
graph = StateGraph(Finalstate)

graph.add_node("find_sentiment" , find_sentiment)
graph.add_node("run_diagnosis", run_diagnosis)
graph.add_node("negative_response" , negative_response)
graph.add_node("positive_response", positive_response)

graph.add_edge(START , "find_sentiment")
graph.add_conditional_edges("find_sentiment", check_condition)
graph.add_edge("run_diagnosis", "negative_response")
graph.add_edge("negative_response", END)
graph.add_edge("positive_response", END)

workflow = graph.compile()
initial_state = {"review": "your product is very good ...."}

final_result = workflow.invoke(initial_state)

print(final_result)

print("Sentiment:", final_result['sentiment'])
print("Score:", final_result['score'])