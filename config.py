from dotenv import dotenv_values

denv = dotenv_values('.env')

try:
    TOKEN: str = denv['token']
    LLAMA_IP: str = denv['llama_ip']
    DB_FILE: str = denv['db_file']
    # allowed: list[int] = list(map(int, open('allowed.txt', 'r').readlines()))

    # LLM settings
    TEMPERATURE: float = float(denv['temperature'])
    CONTEXT_WINDOW: int = int(denv['context_window'])
    STREAM: bool = bool(int(denv['stream']))
    CHUNK_SIZE: int = int(denv['chunk_size'] if STREAM else 0)

except KeyError as e:
    print("❌ Config, key error:", e)
    quit()
