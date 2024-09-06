import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

import config, utils
from create_bot import bot, llm, db


router = Router(name='main')


@router.message(Command('clear_context'))
async def on_clear_context(message: Message):
    chat = message.chat
    user = message.from_user

    await db.update_user(user)
    
    if chat.id != user.id: return

    await db.new_dialog(user)
    async with ChatActionSender.typing(bot=bot, chat_id=chat.id):
        await message.answer(
            text=await llm.ask(prompt='Напиши мне, что контекст диалога обновлен! (используй смайлик)'),
        )

@router.message(Command('info'))
async def on_info(message: Message):
    chat = message.chat
    user = message.from_user

    await db.update_user(user)

    if chat.id != user.id: return

    async with ChatActionSender.typing(bot=bot, chat_id=chat.id):
        await message.answer(
            text=await llm.ask(
                prompt=(
                    "### ЭТО ТВОИ ХАРАКТЕРИСТИКИ ### \n"
                    f'IP АДРЕСС LLMки: {config.LLAMA_IP},\n'
                    f'ТЕМПЕРАТУРА LLM: {config.TEMPERATURE}'
                    f'ОКНО КОНТЕКСТА (сколько сообщений ты помнишь): {config.CONTEXT_WINDOW},\n'
                    f'STREAM (последовательная отправка токенов): {"включен" if config.STREAM else "отключен, нет его!"},\n'
                    'РАЗМЕР ЧАНКА (сколько токенов нужно чтобы редактировать сообщение в телеграмме, работет только при stream):'
                    f'{config.CHUNK_SIZE if config.CHUNK_SIZE else "нисколько, потому что стрим выключен, так и напиши"},\n'
                    f'КОЛ-ВО СООБЩЕНИЙ В ТЕКУЩЕМ ДИАЛОГЕ: {await db.count_messages(user)},\n'
                    "### ПРЕЗЕНТУЙ ИХ МНЕ В ФОРМАТЕ ОПИСАНИЯ, А НЕ СПИСКА (своими словами), КРАТКО, разделяя строки ###"
                    "НЕ ИСПОЛЬЗУЙ МАРКДАУН, ОБЯЗАТЕЛЬНО ВКЛЮЧИ ВСЕ ДАННЫЕ ЧТО Я ДАЛ В ОТВЕТ"
                )
            )
        )


@router.message()
async def on_message(message: Message):
    chat = message.chat
    user = message.from_user

    await db.update_user(user)

    if chat.id != user.id: return
    
    if not await db.get_active_dialog(user):
        await db.new_dialog(user)

    await db.add_message(
        user, 'USER', message.text, 
        await utils.get_theme(message.text)
    )

    async with ChatActionSender.typing(bot=bot, chat_id=chat.id):
        if config.STREAM:
            response = await utils.reply_via_stream(message, config.CHUNK_SIZE)
        else:
            response = await utils.reply_with_single_message(message)

    await db.add_message(
        user, 'ASSISTANT', response, 
        'bot_talk'
    )
