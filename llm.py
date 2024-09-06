import aiohttp, json
from typing import AsyncGenerator

from database import DBMessage


def format_context(context: list[DBMessage])-> list[dict]:
    """
    Formats context to appropriate for request form
    """
    result = []
    for m in context:
        result.append({
            'content': m.content,
            'role': m.role.lower()
        })
    return result


class LLM:
    """
    Main class for LLM usage \\
    Utilises LLama that is hosted in Innopolis :)
    """
    def __init__(self, llm_ip: str, temperature: float):
        self.api_url = f'http://{llm_ip}'
        self.temperature = temperature


    async def post(self, json_data: dict) -> str:
        """ Retreive data from LLM """

        if 'messages' in json_data:
            url = self.api_url + '/v1/chat/completions'
        else:
            url = self.api_url + '/generate'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                if response.status != 200:
                    print(response.text)
                    raise Exception(f"Error: {response.status}")
                if 'messages' in json_data:
                    return (await response.json())['choices'][0]['message']['content']
                else: 
                    return await response.json()

       
    async def post_stream(self, json_data: dict) -> AsyncGenerator[str, str]:
        """ Retreive data from LLM as a stream """

        if 'messages' in json_data:
            url = self.api_url + '/v1/chat/completions'
        else:
            url = self.api_url + '/generate'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                if response.status != 200:
                    raise Exception(f"Error: {response.status}")
                async for line in response.content.iter_chunks():
                    try:
                        chunk = json.loads(line[0][6:-2])
                        if 'messages' in json_data:
                            yield chunk['choices'][0]['delta']['content']
                        else:
                            yield chunk
                    except:
                        pass


    async def ask(
            self, prompt: str = None, context: list[DBMessage] = None,
            choice: list[str] = None, schema: str = None,
            stop: str = None, max_tokens: int = 10_000, regex: str = None,       
        ) -> str:
        """
        Ask LLM a question, get answer as a single message
        You can use EITHER:
        - prompt (to send single message)
        - context (to send the whole context, prompt wont be used!)
        """

        json_data = {
            "stop": stop,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }

        if context:
            json_data.update({
                'messages': format_context(context),
                'model': "meta-llama/Meta-Llama-3.1-8B-Instruct",
            })
        else:
            json_data.update({
                'prompt': prompt,
                "choice": choice,
                "schema": schema,
                "regex": regex,
            })
        answer = await self.post(json_data)
        return answer


    async def ask_stream(
            self, prompt: str = None, context: list[DBMessage] = None,
            choice: list[str] = None, schema: dict[str] = None,
            stop: str = None, max_tokens: int = 10_000, regex: str = None,       
        ) -> AsyncGenerator[str, str]:
        """
        Ask LLM a question, get answer as a stream
        You can use EITHER:
        - prompt (to send single message)
        - context (to send the whole context, prompt wont be used!)
        """

        json_data = {
            "stop": stop,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            'stream': True,
            'stream_options': {
                'include_usage': False,
                'continuous_usage_stats': False
            },
        }

        if context:
            json_data.update({
                'messages': format_context(context),
                'model': "meta-llama/Meta-Llama-3.1-8B-Instruct",
            })
        else:
            json_data.update({
                "prompt": prompt,
                "choice": choice,
                "schema": schema,
                "regex": regex,
            })
        async for answer in self.post_stream(json_data):
            yield answer
