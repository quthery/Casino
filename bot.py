TOKEN = "6379715678:AAF2Ifbr94Qze--ztz2u6O1Bo6uPlx6dIgU"
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import FSInputFile, Message
from get_dice_result import get_result_text
from motor.motor_asyncio import AsyncIOMotorClient

from aiogram import html
import time

cluster = AsyncIOMotorClient("mongodb+srv://quthery:aboba228@cluster0.boxsq6a.mongodb.net/?retryWrites=true&w=majority")
cl = cluster.nineteen.Users

stavki = ['1','2','3','4','5','6','7','8','9','10']
bot = Bot(TOKEN)
dp = Dispatcher()

def get_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='👤Мой профиль')
    keyboard.button(text="💸Сменить ставку")
    keyboard.button(text="🎰Играть!")
    keyboard.adjust(2, 1)
    return keyboard.as_markup(resize_keyboard = True)

def get_keyboard1():
    keyboard2 = ReplyKeyboardBuilder()
    keyboard2.button(text='1')
    keyboard2.button(text="2")
    keyboard2.button(text='3')
    keyboard2.button(text='4')
    keyboard2.button(text='5')
    keyboard2.button(text='6')
    keyboard2.button(text='7')
    keyboard2.button(text='8')
    keyboard2.button(text='9')
    keyboard2.button(text='10')
    return keyboard2.as_markup(resize_keyboard = True)



class ChangeBid(StatesGroup):
    new_bid = State()


   

@dp.message(F.text == '/start')
async def handler(message: Message):
  pattern = {
     "_id": message.from_user.id,
     "name": message.from_user.full_name,
     "bid": 5,
     "balance": 1000

  }
  await message.reply(
      f'привет {message.from_user.first_name}! это игра однорукий бандит что бы начать играть нажми на "🎰Играть!"',
      reply_markup=get_keyboard()
  )
  cl.insert_one(pattern)


@dp.message(F.text == "🎰Играть!")
async def get_game(message: Message):
    result_dice = await message.answer_dice(emoji="🎰")
    bid = await cl.find_one({'_id': message.from_user.id})
    await asyncio.sleep(0.5)

    points, text_for_gamer = get_result_text(result_dice.dice.value, bid=bid["bid"])
    result_text = f"{text_for_gamer} Ваши очки: {points}"
    
    # Обновляем баланс пользователя в зависимости от результата игры
    if points < 0:
        # Отнимаем значение ставки из баланса пользователя
        await cl.update_one({'_id': message.from_user.id}, {'$inc': {'balance': -bid["bid"]}})
    else:
        # Прибавляем значение points к балансу пользователя
        await cl.update_one({'_id': message.from_user.id}, {'$inc': {'balance': points}})
    
    
    await message.answer(text=result_text, reply_markup=get_keyboard())




@dp.message(Command('bid'))
async def symma(message: Message, command: CommandObject):
    args = command.args

    try:
        args = int(args)  # Преобразование аргумента в целое число
        if args > 0:
            await cl.update_one({"_id": message.from_user.id}, {"$set": {"bid": args}})
            await message.answer(f"Теперь ваша ставка равна: {args}")
        else:
            await message.answer("Пожалуйста, введите положительное число!", reply_markup=get_keyboard())
    except ValueError:
        await message.answer("Пожалуйста, введите полное число!", reply_markup=get_keyboard())

@dp.message(F.text == '👤Мой профиль')
async def profile(message: Message):
    user_data = await cl.find_one({'_id': message.from_user.id})
    if user_data:
        

        profile_text = f"👤 Ваш профиль:\n"
        profile_text += f"📜 ID: {message.from_user.id}\n"
        profile_text += f"👒 Имя: {message.from_user.full_name}\n"
        profile_text += f"🎰 Ставка: {user_data["bid"]}\n"
        profile_text += f"💵 Баланс: {int(user_data["balance"])}\n"

        await message.answer(profile_text, reply_markup=get_keyboard())
    else:
        await message.answer("Ваш профиль не найден.", reply_markup=get_keyboard())


@dp.message(F.text=='💸Сменить ставку')
async def cmd_bid(message: Message, state: FSMContext):
    await message.answer(
        text="Введите значение ставки например:1,2,3,4,5,6,7,8,9,10",
        reply_markup=get_keyboard1()
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(ChangeBid.new_bid)

@dp.message(ChangeBid.new_bid, F.text.in_(stavki))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await cl.update_one({"_id": message.from_user.id}, {"$set": {"bid": int(message.text)}})
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} ставку.\n"
             f"приятной игры!",
             reply_markup=get_keyboard()
      
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()   



if __name__ == '__main__':
  try:
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot, skip_updates=True))
    loop.run_forever()
  except KeyboardInterrupt:
     print("Exit bot")
