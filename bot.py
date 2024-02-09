TOKEN = "6379715678:AAF2Ifbr94Qze--ztz2u6O1Bo6uPlx6dIgU"
import os

import asyncio
from aiogram import Bot, Dispatcher, F

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import FSInputFile, Message
from get_dice_result import get_result_text

from aiogram import html
import time



bot = Bot(TOKEN)
dp = Dispatcher()

def get_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="🎰Играть!")
    return keyboard.as_markup(resize_keyboard = True)



@dp.message(F.text == '/start')
async def handler(message: Message):
  await message.reply(
      f'привет {message.from_user.first_name}! это игра однорукий бандит что бы начать играть нажми на "🎰Играть!"',
      reply_markup=get_keyboard()
  )

@dp.message(F.text == "🎰Играть!")
async def get_game(message: Message):
    result_dice = await message.answer_dice(emoji="🎰")
    await asyncio.sleep(1.7)
    points, text_for_gamer = get_result_text(result_dice.dice.value, bid=5)
    result_text = f"{text_for_gamer} Ваши очки: {points}"  # Преобразование числового значения в строку
    await message.answer(text=result_text)





if __name__ == '__main__':

  loop = asyncio.get_event_loop()
  loop.create_task(dp.start_polling(bot, skip_updates=True))
  loop.run_forever()
