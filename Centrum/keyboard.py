import json

from vk_api.keyboard import VkKeyboardColor, VkKeyboard, VkKeyboardButton

def checkPay(id, title):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(label="Проверить оплату", color=VkKeyboardColor.POSITIVE, payload=json.dumps({"type": "checkStatus", "id": id, "title": title}))
    return keyboard.get_keyboard()