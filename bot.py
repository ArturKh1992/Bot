from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging
import aiohttp
import time

# Включаем логирование
logging.basicConfig(level=logging.INFO)

TOKEN = "7886695776:AAFhLbjjLmIZ3qQqJbrFOCzpNBhxoQW1DBQ"

class CalcState(StatesGroup):
    qty_jilka = State()
    line_speed = State()
    weight = State()

# Последнее время активности бота
last_message_time = time.time()

async def start_command(message: Message, state: FSMContext):
    global last_message_time
    last_message_time = time.time()  # Обновляем время последнего сообщения
    await message.answer("Привет! Я бот-калькулятор. Введите количество жилки:")
    await state.set_state(CalcState.qty_jilka)

async def process_qty_jilka(message: Message, state: FSMContext):
    global last_message_time
    last_message_time = time.time()
    
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return

    await state.update_data(qty_jilka=int(message.text))
    await message.answer("Теперь введите скорость линии:")
    await state.set_state(CalcState.line_speed)

async def process_line_speed(message: Message, state: FSMContext):
    global last_message_time
    last_message_time = time.time()
    
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return

    await state.update_data(line_speed=int(message.text))
    await message.answer("Теперь введите вес табачной палочки:")
    await state.set_state(CalcState.weight)

async def process_weight(message: Message, state: FSMContext):
    global last_message_time
    last_message_time = time.time()

    try:
        weight = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return

    data = await state.get_data()
    qty_jilka = data.get("qty_jilka")
    line_speed = data.get("line_speed")

    if line_speed == 0 or weight == 0:
        await message.answer("Ошибка: скорость линии и вес не могут быть нулевыми.")
        return

    result = (qty_jilka * 100) / (line_speed * weight) * 1000

    await message.answer(f"Результат расчета: {result:.2f}\n\nХотите рассчитать снова? Отправьте /start")
    await state.clear()

async def shutdown_check(bot: Bot):
    """ Проверяет активность бота и завершает его, если долгое время нет сообщений. """
    global last_message_time
    while True:
        await asyncio.sleep(60)  # Проверяем раз в минуту
        if time.time() - last_message_time > 300:  # 5 минут бездействия
            logging.info("⏳ Бот засыпает...")
            await bot.session.close()
            exit(0)  # Завершаем процесс (Railway его выключит)

async def main():
    connector = aiohttp.TCPConnector()
    bot = Bot(token=TOKEN, connector=connector)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.register(start_command, Command("start"))
    dp.message.register(process_qty_jilka, CalcState.qty_jilka)
    dp.message.register(process_line_speed, CalcState.line_speed)
    dp.message.register(process_weight, CalcState.weight)

    # Удаляем вебхук перед запуском
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем проверку активности в фоновом режиме
    asyncio.create_task(shutdown_check(bot))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
