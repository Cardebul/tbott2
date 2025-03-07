from uuid import UUID

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from app.abot.atomic import _add_to_cart
from app.abot.keyboards import (ChoiceCallbackFactory, _add_to_cart_kb,
                                _cart_kb, _choice_kb)
from app.models import Cart, Product, User
from asgiref.sync import sync_to_async

router = Router(name=__name__)


class Order(StatesGroup):
    choosing_quantity = State()

    instance_uid: UUID
    product_uid: UUID
    quantity: int
    max_quantity: int
    base_text: str
    price: int


async def quantity(
        callback: types.CallbackQuery, state: FSMContext,
        product: Product
):
    markup, instance_uid = _choice_kb()
    photo = FSInputFile(product.image.path)
    base_text = (
        f'Продукт: {product.name}\n'
        f'Цена: {product.price}\n'
        f'Доступное ко-во: {product.quantity}\n'
        f'Описание: {product.description}\n\n'
    )
    full_text = f'{base_text}Количество: 0'
    
    await callback.message.answer_photo(
        photo=photo,
        caption=full_text,
        reply_markup=markup
    )
    await state.clear()
    await state.set_state(Order.choosing_quantity)
    await state.update_data(
        instance_uid=instance_uid, product_uid=product.id,
        quantity=0, max_quantity=product.quantity,
        base_text=base_text, price=product.price
    )


@router.callback_query(Order.choosing_quantity, ChoiceCallbackFactory.filter(F.solution_type == 'calc'))
async def quantity_chosen(
        callback: types.CallbackQuery, 
        callback_data: ChoiceCallbackFactory,
        state: FSMContext
):
    data = await state.get_data()
    quantity = data['quantity']
    instance_uid = data['instance_uid']
    

    if instance_uid != callback_data.instance_uid:
        await callback.answer('Устарело')
        return
    
    if (callback_data.val == 0 ) and (quantity == 0):
        await callback.answer()
        return
    
    update = int(f'{quantity}{callback_data.val}') if quantity != 0 else callback_data.val
    if update > data['max_quantity']:
        await callback.answer(text='max')
        return

    await state.update_data(quantity=update)
    full_text = f'{data.get('base_text')}Количество: {update}\nИтоговая стоимость: {update*data.get('price')}'
    await callback.message.edit_caption(
        caption=full_text, 
        reply_markup=callback.message.reply_markup
    )
    await callback.answer()


@router.callback_query(Order.choosing_quantity, ChoiceCallbackFactory.filter(F.solution_type.in_(['clear', 'ok'])))
async def solution_chosen(
        callback: types.CallbackQuery, 
        callback_data: ChoiceCallbackFactory,
        state: FSMContext
):
    data = await state.get_data()
    instance_uid = data['instance_uid']

    if instance_uid != callback_data.instance_uid:
        await callback.answer('Устарело')
        return


    base_text = data['base_text']
    quantity = data['quantity']
    price = data['price']
    if callback_data.solution_type == 'clear':
        await state.update_data(quantity=0)
        full_text = f'{base_text}Количество: 0'
        await callback.message.edit_caption(
            caption=full_text, 
            reply_markup=callback.message.reply_markup
        )
        return

    if quantity != 0:
        full_text = f'{base_text}Количество: {quantity}\nИтоговая стоимость: {quantity*data.get('price')}'
        await state.update_data(last_message={
            'text': full_text,
            'reply_markup': callback.message.reply_markup,
            'caption': True
        })
        await callback.message.edit_caption(
            caption=full_text,
            reply_markup=_add_to_cart_kb(quantity, price*quantity, instance_uid)
        )
        await callback.answer()
        return
    await callback.answer(text='skip')


@router.callback_query(Order.choosing_quantity, ChoiceCallbackFactory.filter(F.solution_type == 'add'))
async def solution_chosen(
        callback: types.CallbackQuery, 
        callback_data: ChoiceCallbackFactory,
        state: FSMContext
):
    data = await state.get_data()
    instance_uid = data['instance_uid']
    if instance_uid != callback_data.instance_uid:
        await callback.answer('Устарело')
        return


    product_uid = data['product_uid']
    quantity = data['quantity']
    user = await User.objects.aget(tid=callback.message.chat.id)
    res = await sync_to_async(_add_to_cart)(user, product_uid, quantity)

    if not res:
        await callback.answer('bad')
        return

    cart_items = await sync_to_async(list)(
        Cart.objects.select_related('product').filter(user__tid=callback.message.chat.id, payment__isnull=True)
    )
    await callback.message.answer(
        text='Корзина',
        reply_markup=_cart_kb(cart_items)    
    )
    await callback.answer()

    