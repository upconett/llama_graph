from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, User
from aiogram.utils.chat_action import ChatActionSender

import config, utils
from create_bot import bot, llm, db


router = Router(name='main')


@router.message(Command('clear_context'))
async def on_clear_context(message: Message):
    chat = message.chat
    user = message.from_user

    await db.update_user(user)
    
    if not all(x in config.allowed for x in (chat.id, user.id)):
        print(chat.id, user.id)
        return

    await db.new_dialog(user)
    await message.answer(
        text=await llm.ask('Напиши мне, что контекст диалога обновлен! (используй смайлик)'),
    )


@router.message()
async def on_message(message: Message):
    chat = message.chat
    user = message.from_user

    await db.update_user(user)

    if not all(x in config.allowed for x in (chat.id, user.id)):
        print(chat.id, user.id)
        return
    
    if not await db.get_active_dialog(user):
        await db.new_dialog(user)

    await db.add_message(
        user, 'USER', message.text, 
        await llm.get_theme(message.text)
    )
    async with ChatActionSender.typing(bot=bot, chat_id=chat.id):
        context = await db.get_context(user, 10)
        response = await llm.ask_with_context(message.text, context) 
        # response = await llm.ask(context+message.text)
        await message.reply(
            text=response,
        )
    await db.add_message(
        user, 'ASSISTANT', response, 
        await llm.get_theme(response)
    )
