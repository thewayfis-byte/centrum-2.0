from keyboards.design_keyboard import back_to_menu, services_list, closeTicket, categoris

help = {
  "main": {
    "message": "Виу-виу 🚨 Помощь уже в пути!\n\nНапишите ваш вопрос, а я перенаправлю его менеджеру",
    "keyboard": back_to_menu()
  },
  "help": {
    "message": "Ваше сообщение отправлено менеджеру  😎 Вам ответят в течении 10 минут рабочего времени студии:\n\nпн-пт: 07:00 — 22:00\nсб-вс: 12:00 — 22:00\n\n⛔ Не закрывайте тикет, пока Вы не получите ответ!",
    "keyboard": closeTicket()
  }
}

order = {
  "main": {
  "message": "Выберите нужную категорию услуги 🔥",
  "keyboard": categoris()
  }
}