import asyncio, aiohttp

import config
from database import DBMessage
from utils import format_context


class LLM:
    context = []

    def __init__(self, llm_ip: str):
        self.api_url = f'http://{llm_ip}'


    async def get_response(self, json_data: dict) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url+'/generate', json=json_data) as response:
                if response.status != 200:
                    # print(await response.json())
                    raise Exception(f"Error: {response.status}")
                return await response.json()
            
        
    async def post_chat_completion(self, json_data: dict) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url+'/v1/chat/completions', json=json_data) as response:
                if response.status != 200:
                    raise Exception(f"Error: {response.status}")
                return await response.json()

                
    async def ask_with_context(self, message: str, context: list[DBMessage]) -> str:
        answer = await self.post_chat_completion(
            {
                'messages': format_context(context),
                'model': "meta-llama/Meta-Llama-3.1-8B-Instruct"
            }
        )
        return answer['choices'][0]['message']['content']
                
    async def ask(
        self, message: str, choice: list[str] = None, schema: dict[str] = None,
        stop: str = None, max_tokens: int = 10_000, regex: str = None, 
        temperature: float = 0
        ) -> str:
        answer = await self.get_response(
            {
                "prompt": message,
                "stop": stop,
                "max_tokens": max_tokens,
                "choice": choice,
                "schema": schema,
                "regex": regex,
                "temperature": temperature,
            }
        )
        return answer

    
    async def get_theme(self, message: str) -> str:
        return await self.ask(
            ("### ТВОЯ ЗАДАЧА ###\n"
            "Далее я напишу тебе сообщение, ты должен обобщить и выделить тему этого сообщения.\n"
            "Пришли ответ в двух словах (не более 3х слов!): \n"
            "### СООБЩЕНИЕ ###\n"
            ) + message)

if __name__ == '__main__':
    llm = LLM(config.LLAMA_IP)
    answer = asyncio.run(
        llm.ask(
            message="Привет! чепочем"
        )
    )
    print(answer)
