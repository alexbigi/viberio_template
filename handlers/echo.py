from db.repository import Repo
from loader import dp, viber
from viberio.types import requests
from viberio.types.messages import TextMessage, RichMediaMessage, KeyboardMessage
from viberio.types.messages.content_message import RichMedia, ContentButtons
from viberio.types.messages.keyboard_message import Keyboard, ButtonsObj
from viberio.types.requests import ViberMessageRequest


# @dp.text_messages_handler(lambda msg: msg.message.text in ['START', 'СТАРТ', 'Start'])
# async def test_message(request: requests.ViberMessageRequest, data: dict):
#     repo = data['repo']
#     await repo.add_user_from_message(request.sender.id, request.sender.name, request.sender.country,
#                                      request.sender.api_version, request.sender.language)
#     await viber.send_message(request.sender.id, TextMessage(text='Thanks !'))
#     await viber.send_message(request.sender.id,
#                              KeyboardMessage(text="123",
#                                              keyboard=Keyboard(Type="keyboard",
#                                                                Buttons=[ButtonsObj(Text="text",
#                                                                                    Rows=1,
#                                                                                    Columns=3,
#                                                                                    ActionBody="Text",
#                                                                                    ActionType="reply",
#                                                                                    BgColor="#7eceea",
#                                                                                    ),
#                                                                         ButtonsObj(Text="text2",
#                                                                                    Rows=1,
#                                                                                    Columns=3,
#                                                                                    ActionBody="Text2",
#                                                                                    ActionType="reply",
#                                                                                    BgColor="#7eceea",
#                                                                                    ),
#                                                                         ])))
#     await viber.send_message(request.sender.id,
#                              RichMediaMessage(rich_media=RichMedia(BgColor="#FFFFFF", Buttons=[
#                                  ContentButtons(ActionBody="https://www.google.com", ActionType="open-url",
#                                                 Text="sometext"),
#                                  ContentButtons(ActionBody="https://www.google.com", ActionType="open-url",
#                                                 Text="sometext")])))
#     return True


@dp.messages_handler()
async def echo(request: ViberMessageRequest, data: dict):
    # print(request)
    repo = data['repo']
    state = await repo.get_current_state(request.sender.id)
    state_vars = state['vars']
    if state['state'] == "*":
        await viber.send_message(request.sender.id, TextMessage(text="Введите имя:"))
        await repo.set_state(request.sender.id, "wait_name")

    if state['state'] == "wait_name":
        state_vars["name"] = request.message.text
        await viber.send_message(request.sender.id, TextMessage(text="Введите адрес:"))
        await repo.set_state_vars(request.sender.id, state_vars)
        await repo.set_state(request.sender.id, "wait_address")

    if state['state'] == "wait_address":
        state_vars["address"] = request.message.text
        await viber.send_message(request.sender.id, TextMessage(text="Введите возраст:"))
        await repo.set_state_vars(request.sender.id, state_vars)
        await repo.set_state(request.sender.id, "wait_age")

    if state['state'] == "wait_age":
        state_vars["age"] = request.message.text
        await viber.send_message(request.sender.id, TextMessage(text=f"Ваши данные:\nИмя: {state_vars['name']}\nАдрес: "
                                                                     f"{state_vars['address']}\n"
                                                                     f"Возраст: {state_vars['age']}"))
        await repo.set_state_vars(request.sender.id, {})
        await repo.set_state(request.sender.id, "*")

    # await viber.send_message(request.sender.id, request.message)
    return True


@dp.request_handler()
async def webhook(request: ViberMessageRequest, data: dict):
    print('Viber request', request)
    return True
