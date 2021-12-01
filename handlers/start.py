from loader import dp, viber
from viberio.types.messages import TextMessage, KeyboardMessage
from viberio.types.messages.keyboard_message import Keyboard, ButtonsObj
from viberio.types.requests import ViberConversationStartedRequest, ViberSubscribedRequest, ViberUnsubscribedRequest


@dp.conversation_started_handler()
async def start(request: ViberConversationStartedRequest, data: dict):
    repo = data['repo']
    await repo.add_user_from_message(request.user.id, request.user.name, request.user.country,
                                     request.user.api_version, request.user.language)
    text = 'Здарова! Это приветственное сообщение. Нажми кнопку старт, и погнали'
    await viber.send_message(request.user.id,
                             KeyboardMessage(text=text, keyboard=Keyboard(
                                 Type="keyboard",
                                 Buttons=[
                                     ButtonsObj(Text="START", Rows=1, Columns=6, ActionBody="START", ActionType="reply")
                                 ])))
    return True


@dp.subscribed_handler()
async def subscribed(request: ViberSubscribedRequest, data: dict):
    await viber.send_message(request.user.id, TextMessage(text='Thanks for subscription!'))
    return True


@dp.unsubscribed_handler()
async def unsubscribed(request: ViberUnsubscribedRequest, data: dict):
    await viber.send_message(request.user_id, TextMessage(text='Bye!'))
    return True
