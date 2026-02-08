import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

@tool('get_weather', description='Get the current weather in a given location',return_direct=False)
def get_weather(location: str) -> str:
    respnse = response.get(f'https//wttr.in/{location}?format=j1')
    return respnse.json

agent = create_agent(
    model = 'gpt-4o-mini',
    tools=[get_weather],
    system_prompt='You are a helpful assistant that can get the current weather in a given location',
    verbose=True
)

response = agent.invoke({
    'messages': [
        {'role': 'user', 'content': 'What is the weather like in New York?'}
    ]
})
print(response['messages'][-1]['content'])

