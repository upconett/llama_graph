# LLaMa-Graph
> Well, no graphs for now...  
> But that's the matter of time! ⌛

## .env file layout:
```python
# Telegram bot settings
token = "7299572537:AAFNmlzy6PEEOiXMAMPhKY5PDj3oB5S2VDo"

# Database settings
db_file = "sqlite3.db"                  # file where db is stored

# LLM settings 
llama_ip = "11.220.1.223:1224"          # ip address of llm host
temperature = 0                         # how crazy is llm (0-1)
context_window = 20                     # how many messages LLM remembers
stream = 1                              # will llm send response token by token
chunk_size = 512                        # how many tokens needed to edit message
```