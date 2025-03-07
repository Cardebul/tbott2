from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from app.abot.atomic import _remove_cart
from app.abot.handlers.cart_router import quantity
from app.abot.keyboards import (CART_B, CATALOG_B, FAQ_B, PROFILE_B,
                                BaseCallbackFactory, CartItemCallbackFactory,
                                CategoryCallbackFactory,
                                ProductCallbackFactory, _cart_kb, _category_kb,
                                _main_kb, _product_kb)
from app.models import Cart, Payment, Product, User, models
from app.abot.uorder import after_payment, make_uorder
from asgiref.sync import sync_to_async


router = Router(name=__name__)


@router.message(Command('start'))
async def cmd_start(message: Message):
    await User.objects.aget_or_create(tid=message.chat.id)
    await message.answer('Привет', reply_markup=_main_kb())


@router.message(F.text == PROFILE_B)
async def profile(message: Message):
    user = await User.objects.aget(tid=message.chat.id)

    val_or_none = lambda x: x if x else 'не установлено'
    base_text = (
        f'Имя: {val_or_none(user.full_name)}\n'
        f'Телефон: {val_or_none(user.phone_number)}\n'
        f'Адрес: {val_or_none(user.address)}\n'
        f'/setprofile - заполнить данные\n'
        f'/csetprofile- выйти из режима заполнения\n'
    )

    await message.answer(text=base_text)


@router.message(F.text == CATALOG_B)
async def catalog(message: Message):
    category_kb = await _category_kb()
    await message.answer(f'{CATALOG_B}', reply_markup=category_kb)


@router.message(F.text == CART_B)
async def cart(message: types.Message):
    cart_items = await sync_to_async(list)(
        Cart.objects.select_related('product').filter(user__tid=message.chat.id, payment__isnull=True)
    )

    await message.answer(
        text='Корзина',
        reply_markup=_cart_kb(cart_items)
    )

@router.message(F.text == FAQ_B)
async def faq(message: Message):
    await message.answer('.....FQ>>>>>....')




PROD = False

@router.callback_query(CartItemCallbackFactory.filter(F.action == 'make_order'))
async def callbacks_product(
        callback: types.CallbackQuery, 
        callback_data: CartItemCallbackFactory,
):
    user = await User.objects.aget(tid=callback.message.chat.id)
    if not user.personal_data:
        await callback.answer('Заполните личные данные в Профиле')
        return
    if not await Cart.objects.filter(user=user).aexists():
        await callback.answer('Нет доступных к оформлению заказов')
        return
    
    final_cost = await Cart.objects.filter(
        user__tid=callback.message.chat.id, payment__isnull=True
    ).aaggregate(final_cost=models.Sum('total_cost'))
    final_cost = final_cost.get('final_cost')
    payment = await Payment.objects.acreate(user=user, final_cost=final_cost)
    await Cart.objects.filter(user__tid=callback.message.chat.id, payment__isnull=True).aupdate(payment=payment)
    if final_cost and (
        data:=await make_uorder(value=final_cost)
    ) and (1): pay_url, _ = data

    else: return await callback.answer('try later')
    text = (
        f'Товаров в корзине на {final_cost}\n'
        f'Произведите оплату по <a href="{pay_url}">ссылке</a>'
    )
    await callback.message.answer(
        text=text,
        parse_mode='HTML'
    )
    await callback.answer()
    if not PROD:
        await after_payment(payment.pk)
        await callback.message.answer('Успешно')
    
@router.callback_query(CartItemCallbackFactory.filter(F.action.in_(['remove', 'view'])))
async def callbacks_product(
        callback: types.CallbackQuery, 
        callback_data: CartItemCallbackFactory,
):
    if callback_data.action == 'remove':
        res = await sync_to_async(_remove_cart)(callback_data.cart_uid)
        if not res:
            await callback.answer('err')
            return
        cart_items = await sync_to_async(list)(
            Cart.objects.select_related('product').filter(user__tid=callback.message.chat.id, payment__isnull=True)
        )
        await callback.message.edit_text(
            text=callback.message.text,
            reply_markup=_cart_kb(cart_items)    
        )
        return
    
    if not (product:=await Product.objects.filter(carts__id=callback_data.cart_uid).afirst()): return await callback.answer('err')
    photo = FSInputFile(product.image.path)
    base_text = (
        f'Продукт: {product.name}\n'
        f'Цена: {product.price}\n'
        f'Описание: {product.description}\n\n'
        f''
    )
    await callback.message.answer_photo(
        photo=photo,
        caption=base_text,
    )



@router.callback_query(CategoryCallbackFactory.filter())
async def callbacks_product_list(
        callback: types.CallbackQuery, 
        callback_data: CategoryCallbackFactory,
        state: FSMContext
):
    
    products = await sync_to_async(list)(Product.objects.filter(category__pk=callback_data.uid))
    product_kb = _product_kb(products)
    await state.update_data(last_message={
        'text': callback.message.text,
        'reply_markup': callback.message.reply_markup
    })
    await callback.message.edit_text(f'Продукты:', reply_markup=product_kb)
    await callback.answer()

@router.callback_query(ProductCallbackFactory.filter())
async def callbacks_product(
        callback: types.CallbackQuery, 
        callback_data: CategoryCallbackFactory,
        state: FSMContext
):
    if not (product:= await Product.objects.filter(pk=callback_data.uid).afirst()): return
    await quantity(callback, state, product)
    await callback.answer()

@router.callback_query(BaseCallbackFactory.filter())
async def handle_base_buttons(
    callback: types.CallbackQuery,
    callback_data: BaseCallbackFactory,
    state: FSMContext
):
    if callback_data.action == 'close':
        await callback.message.delete()
    elif callback_data.action == 'back':
        previous_state = await state.get_data()
        reply_markup = previous_state['last_message']['reply_markup']
        if 'last_message' in previous_state:
            if previous_state['last_message'].get('caption'):
                print('incaption')
                await callback.message.edit_caption(
                    caption=previous_state['last_message']['text'],
                    reply_markup=reply_markup
                )
            else:
                await callback.message.edit_text(
                    text=previous_state['last_message']['text'],
                    reply_markup=reply_markup
                )
    await callback.answer()


