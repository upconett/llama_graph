from dotenv import dotenv_values

denv = dotenv_values('.env')

try:
    TOKEN: str = denv['token']
    LLAMA_IP: str = denv['llama_ip']
    DB_FILE: str = denv['db_file']
    allowed: list[int] = list(map(int, open('allowed.txt', 'r').readlines()))

except KeyError as e:
    print("❌ Config, key error:", e)
    quit()
