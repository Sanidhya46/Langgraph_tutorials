from langgraph.graph import StateGraph , START , END
from typing import TypedDict
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint , HuggingFacePipeline
import os 


api_key = os.getenv('HUGGINGFACEHUB_API_KEY')

llm = HuggingFaceEndpoint(
    repo_id = "google/gemma-2-2b-it",
    task="text-generation",
    huggingfacehub_api_token=api_key,  # ✅ THIS IS CRITICAL!

)

model = ChatHuggingFace(llm = llm)

# STRUCTURE OF THE STATE
class BMISTATE(TypedDict):
    weight_kg: float
    height_m: float
    bmi: float
    category: str

# CALCULATION OF BMI
def calculate_bmi(state: BMISTATE) -> BMISTATE:
   weight = state['weight_kg']
   height = state['height_m']

   bmi = weight/(height**2)

   state['bmi'] = round(bmi, 2)

   return state

# label of bmi -- core algorithm
def label_bmi(state: BMISTATE) -> BMISTATE:

    bmi = state['bmi']

    if bmi < 18.5:
        state["category"] = "Underweight"
    elif 18.5 <= bmi < 25:
        state["category"] = "Normal"
    elif 25 <= bmi < 30:
        state["category"] = "Overweight"
    else:
        state["category"] = "Obese"

    return state

# define graph 
graph =  StateGraph(BMISTATE)  # creates graph based workflow
graph.add_node("calculate_bmi" , calculate_bmi)
graph.add_node("label_bmi" , label_bmi)

#add edges to the graph determine flow of the graph 
graph.add_edge(START , "calculate_bmi")
graph.add_edge("calculate_bmi","label_bmi")
graph.add_edge("label_bmi", END )

workflow = graph.compile()

initial_state = {'weight_kg' : 80, 'height_m': 1.73}
final_state = workflow.invoke(initial_state)

print(final_state)

