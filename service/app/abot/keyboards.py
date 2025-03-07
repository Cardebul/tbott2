from typing import Literal, Optional
from uuid import UUID, uuid4

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.models import Cart, Category
from asgiref.sync import sync_to_async
from django.db.models import QuerySet

CATALOG_B = 'Каталог'
CART_B = 'Корзина'
PROFILE_B = 'Профиль'
FAQ_B = 'FAQ'

def _main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    [kb.button(text=CATALOG_B), kb.button(text=CART_B), kb.button(text=FAQ_B), kb.button(text=PROFILE_B), kb.adjust(2)]
    return kb.as_markup(resize_keyboard=True)


class BaseCallbackFactory(CallbackData, prefix="base"): action: Literal['back', 'close']


def _add_base_buttons(builder: InlineKeyboardBuilder, with_back: bool = True):
    if with_back:
        builder.button(
            text="⬅️ Назад",
            callback_data=BaseCallbackFactory(action="back")
        )
    builder.button(
        text="✖️ Закрыть",
        callback_data=BaseCallbackFactory(action="close")
    )
    return builder


class CategoryCallbackFactory(CallbackData, prefix="category"): uid: UUID


async def _category_kb():
    builder = InlineKeyboardBuilder()

    categories = await sync_to_async(list)(Category.objects.all())
    for category in categories: builder.button(
        text=category.name, callback_data=CategoryCallbackFactory(uid=category.id)
    )
    _add_base_buttons(builder, with_back=False)
    builder.adjust(2)
    return builder.as_markup()


class ProductCallbackFactory(CallbackData, prefix="product"): uid: UUID


def _product_kb(products):
    builder = InlineKeyboardBuilder()

    
    for product in products: builder.button(
        text=product.name, callback_data=ProductCallbackFactory(uid=product.id)
    )
    _add_base_buttons(builder, with_back=True)
    builder.adjust(1)
    return builder.as_markup()


class ChoiceCallbackFactory(CallbackData, prefix="choise"):
    instance_uid: UUID
    
    solution_type: Literal[
        'ok', 'clear', 'calc', 'add'
    ] = 'calc'
    val: Optional[int] = None


def _choice_kb(instance_uid = None):
    if not instance_uid: instance_uid = uuid4()
    builder = InlineKeyboardBuilder()
    for i in range(1, 10): builder.button(
        text=f"{i}", callback_data=ChoiceCallbackFactory(
            val=i, instance_uid=instance_uid
        )
    )
    builder.button(
        text='OK', callback_data=ChoiceCallbackFactory(solution_type='ok', instance_uid=instance_uid))
    builder.button(
        text='0', callback_data=ChoiceCallbackFactory(val=0, instance_uid=instance_uid))
    builder.button(
        text='Clear', callback_data=ChoiceCallbackFactory(solution_type='clear', instance_uid=instance_uid))
    _add_base_buttons(builder, with_back=False)
    builder.adjust(3)
    return builder.as_markup(), instance_uid

def _add_to_cart_kb(quantity, cost, instance_uid):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Добавить в корзину {quantity}шт за {cost}',
        callback_data=ChoiceCallbackFactory(solution_type='add', instance_uid=instance_uid)
    )
    _add_base_buttons(builder, with_back=True)
    builder.adjust(1)
    return builder.as_markup()


class CartItemCallbackFactory(CallbackData, prefix="cart_item"):
    action: Literal['view', 'remove', 'make_order']
    cart_uid: Optional[UUID] = None


def _cart_kb(cart_items: QuerySet[Cart]):
    builder = InlineKeyboardBuilder()
    total = 0
    for item in cart_items:
        total += item.total_cost
        builder.button(
            text=f'{item.product.name} {item.quantity}шт {item.total_cost}',
            callback_data=CartItemCallbackFactory(action='view', cart_uid=item.pk)
        )
        builder.button(text=f'❌ удалить', callback_data=CartItemCallbackFactory(action='remove', cart_uid=item.pk))
    if cart_items: builder.button(
        text=f'Оформить за {total}', callback_data=CartItemCallbackFactory(action='make_order')
    )

    builder.adjust(2)
    return builder.as_markup()