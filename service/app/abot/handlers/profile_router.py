from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.models import User
from geopy.geocoders import Nominatim
import re

geolocator = Nominatim(user_agent="myteleapp_v1")
router = Router(name=__name__)


class Form(StatesGroup):
    name = State()
    phone = State()
    address = State()


def validate_address(address: str):
    d = address.split(', ')
    print(d)
    if len(d) < 2: return
    if ('.' not in d[0]) or ('.' not in d[1]): return

    return d[0], d[1]

def validate_phone(phone):
    pattern = r'^\+7[9][0-9]{9}$'
    
    if re.match(pattern, phone):
        return True
    return False

def validate_name(name): return len(name) < 1000

@router.message(Command("setprofile"))
async def cmd_setprofile(message: Message, state: FSMContext):
    user = await User.objects.aget(tid=message.chat.id)

    if user.personal_data: ...

    await state.set_state(Form.name)
    await message.answer('Добавьте имя')

@router.message(Command("csetprofile"))
async def cmd_csetprofile(message: Message, state: FSMContext):
    await state.clear()    
    await message.answer('Вы вышли из создания профиля')

@router.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    if not validate_name(name):
        await message.reply('err Больше 1000 символов')
        return
    user = await User.objects.filter(tid=message.chat.id).afirst()
    user.full_name = name
    await user.asave()
    await message.reply(f"Имя {name} успешно добавлено")

    if user.phone_number and user.address: return
    if not user.phone_number:
        await state.set_state(Form.phone)
        await message.answer('Введите номер телефона в формате +79999999999')
        return
    elif not user.address:
        await state.set_state(Form.address)
        await message.answer('Введите адрес в формате 52.509669, 13.376294')
        return

@router.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not validate_phone(phone):
        await message.reply('err Телефон не соответствует шаблону +79999999999')
        return
    user = await User.objects.filter(tid=message.chat.id).afirst()
    user.phone_number = phone
    await user.asave()
    await message.reply(f"Телефон {phone} успешно добавлен")


    if user.full_name and user.address: return
    if not user.full_name:
        await state.set_state(Form.name)
        await message.answer('Введите Имя')
        return
    elif not user.address:
        await state.set_state(Form.address)
        await message.answer('Введите адрес в формате 52.509669, 13.376294')
        return

@router.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    address = message.text
    if not (data:=validate_address(address)):
        await message.reply('err Адрес не соответствует шаблону 52.509669, 13.376294')
        return
    location = geolocator.reverse(f"{data[0]}, {data[1]}")
    if not location:
        await message.reply('err Адрес не найден попробуйте отправить геолокацию')
        return
    user = await User.objects.filter(tid=message.chat.id).afirst()
    user.address = location
    await user.asave()
    await message.reply(f"Адрес {location} успешно добавлен")
    await state.clear()

@router.message(F.location)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    location = geolocator.reverse(f"{lat}, {lon}")
    await message.reply(f'Ваше гео {location}')