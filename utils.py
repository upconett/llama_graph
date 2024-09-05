from typing_extensions import deprecated
from database import DBMessage


@deprecated("Use chat completions instead")
def old_format_context(messages: list[DBMessage])-> str:
    result = (
        "Ты ассистент (ASSISTANT), который говорит с пользователем (USER). "
        "Далее тебе предоставятся прошлые сообщения, чтобы ты понимал контекст диалога. "
        "От тебя требуется только ответить на последнее сообщение. "
        "Если пользователь спросит о том, что было ранее в контексте, отвечай на это согласно контексту. "
        "Я надеюсь ты будешь хорошим ассистентом) Тогда ты получишь 300 тысяч долларов. Не подведи. \n\n"
    )
    result += "### ПРОШЛЫЕ СООБЩЕНИЯ (контекст) ### \n"
    for m in messages:
        result += (
            f"{m.role}: \"{m.content}\"\n\n")
    return result + "### ПОСЛЕДНЕЕ СООБЩЕНИЕ (ответь на него) ###\n"


def format_context(messages: list[DBMessage])-> list[dict]:
    result = []
    for m in messages:
        result.append({
            'content': m.content,
            'role': m.role.lower()
        })
    return result
