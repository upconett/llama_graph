from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import Message

from typing_extensions import deprecated
from database import DBMessage


from create_bot import bot, llm, db


@deprecated("Don't use, it is bullshit")
def old_format_context(messages: list[DBMessage])-> str:
    """ Don't use, it is bullshit """
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


async def get_theme(message: str) -> str:
    """ Get theme of a message """
    return await llm.ask(prompt=(
        "### ТВОЯ ЗАДАЧА ###\n"
        "Далее я напишу тебе сообщение, ты должен обобщить и выделить тему этого сообщения.\n"
        "Пришли ответ в двух словах (не более 3х слов!): \n"
        "### СООБЩЕНИЕ ###\n"
        ) + message)
    
    
async def reply_with_single_message(message: Message) -> str:
    user = message.from_user

    context = await db.get_context(user)
    response = await llm.ask(context=context) 

    await message.reply(text=response)
    return response


async def reply_via_stream(message: Message, chunk_size: int = 64) -> str:
    """ 
    Use CAREFULLY
    ---
    FLOOD ERROR IS LIKELY
    """
    user = message.from_user
    
    final_response = ''

    response = ''
    whole_response = ''
    last_response = ''

    to_edit = (await message.reply('...')).message_id

    context = await db.get_context(user)
    async for word in llm.ask_stream(context=context):
        response += word
        final_response += word
        if len(response) > chunk_size:
            whole_response += response
            if len(whole_response) > 4096:
                to_edit = (await message.reply(response+'...')).message_id
                whole_response = ''
                response = ''
                return
            response = ''
        if whole_response:
            if last_response == whole_response:
                continue
            else: last_response = whole_response
            try:
                await bot.edit_message_text(
                    text=whole_response+'...',
                    chat_id=user.id,
                    message_id=to_edit
                )
            except Exception as e:
                print(e)

    whole_response += response
    try:
        await bot.edit_message_text(
            text=whole_response,
            chat_id=user.id,
            message_id=to_edit
        )
    except Exception as e:
        print(e)
    return final_response
