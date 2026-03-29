from database.design_database import c, db
from methods.design_message import messageSendUser
from config.config import admins
from keyboards.design_keyboard import start
c.execute("DELETE FROM users")
c.execute("DELETE FROM help_messages")
c.execute("DELETE FROM order_messages")
c.execute("DELETE FROM orders")
c.execute("UPDATE dialogs_count SET manager = 0, designer = 0")
c.execute("DELETE FROM control_close_orders")
c.execute("DELETE FROM pay_list")
c.execute("DELETE FROM manager_dialog")
db.commit()

messageSendUser(admins[0], "d", keyboard=start())