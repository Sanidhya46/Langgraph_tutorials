from langgraph.graph import StateGraph , START , END
from typing import TypedDict
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint , HuggingFacePipeline
import os 



api_key = os.getenv('HUGGINGFACEHUB_API_KEY')

llm = HuggingFaceEndpoint(
    repo_id = "google/gemma-2-2b-it",
    task="text-generation",
    huggingfacehub_api_token= api_key,  # ✅ THIS IS CRITICAL!

)

model = ChatHuggingFace(llm = llm)

class blog(TypedDict):  # custom dictionary to define graph
    content : str
    outline : str
    title : str

def create_outline(state: blog) -> blog:
    # Create a state graph to represent the blog post
    title = state['title']
    prompt = f"create the proper outline for the blog on the topic '{title}' "

    outline = model.invoke(prompt).content
    state['outline'] = outline
    return state

def create_blog(state: blog) -> blog:
    title = state['title']
    outline = state['outline']
    prompt = f"rate the particular blog for the title from 1 to 5 dont write much just give answer '{title}' .. using the following outline '{outline}' "

    content = model.invoke(prompt).content

    state['content'] = content  # particular dictionary value comes at particcular content key
    return state

graph = StateGraph(blog)

graph.add_node("create_outline", create_outline)
graph.add_node("create_blog", create_blog)

graph.add_edge(START , "create_outline")
graph.add_edge("create_outline" , "create_blog")
graph.add_edge("create_blog" , END)

result = graph.compile()
final_result = result.invoke({ "title" : "Rise of ai in india"})

print(final_result)