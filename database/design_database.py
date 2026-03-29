import pymysql

db = pymysql.connect(
    host="79.174.95.87",
    user="ilezzov",
    password="ilezzov_top",
    port=3306,
    database="ilezzov"
)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS staff(
    user_id BIGINT,
    name TEXT,
    staff_group TEXT,
    staff_date TEXT,
    balance FLOAT,
    raything FLOAT,
    reproofs BIGINT,
    orders_all BIGINT,
    orders_did BIGINT,
    orders_no_does BIGINT,
    dialog_all BIGINT,
    dialog_did BIGINT,
    dialog_no_does BIGINT,
    can_work_designer BIGINT,
    can_work_manager BIGINT,
    blokopad_id BIGINT
)""")

#c.execute("INSERT INTO staff VALUES (501285409, 'Илья', 'admin', '12', 1000000, 5, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)")
#c.execute("INSERT INTO staff_perms VALUES (501285409, '*')")

c.execute("""CREATE TABLE IF NOT EXISTS staff_perms (
    user_id BIGINT,
    perms TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT,
    flag TEXT,
    orders BIGINT,
    message_id BIGINT,
    mailling BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS services (
    service TEXT,
    about TEXT,
    price BIGINT,
    carousel_photo TEXT,
    attachment TEXT,
    link TEXT,
    priority BIGINT, 
    alias TEXT 
)""")

c.execute("""CREATE TABLE IF NOT EXISTS check_free (
    user_id BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS orders (
    user_id BIGINT,
    service TEXT,
    status TEXT,
    number BIGINT,
    data TEXT,
    designer_id BIGINT,
    manager_id BIGINT,
    chat_id BIGINT,
    attachment TEXT,
    have_manager BIGINT,
    it_skin BIGINT,
    arms TEXT,
    attachment_no_key TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS designer_service (
    user_id BIGINT,
    service TEXT,
    bet FLOAT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS promocodes (
    promocode TEXT,
    sale FLOAT,
    used_count BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS used_promocode (
    user_id BIGINT,
    promocode TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS pay_list (
    user_id BIGINT,
    money FLOAT,
    id_form TEXT,
    designer BIGINT,
    service TEXT,
    bet FLOAT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS nalog (
    nalog FLOAT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS control_close_orders(
    user_id BIGINT,
    date_last_message TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS order_messages(
    user_id BIGINT,
    message_id BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS help_messages(
    user_id BIGINT,
    message_id BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS dialogs_count (
    manager BIGINT,
    designer BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS manager_dialog (
    user_id BIGINT,
    manager_id BIGINT,
    number_dialog BIGINT,
    chat_id BIGINT,
    date_create TEXT,
    have_manager BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS chats (
    support_chat BIGINT,
    orders_chat BIGINT,
    designer_chat BIGINT,
    review_chat BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS raything_list (
    user_id BIGINT,
    raything BIGINT,
    date TEXT,
    type TEXT,
    order_or_ticket_number BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS balance_list (
    user_id BIGINT,
    balance BIGINT,
    date TEXT,
    type TEXT,
    order_or_ticket_number BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS bet (
    manager_bet BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS date_payment_check (
    last_date TEXT,
    columns_table BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS design_settings (
    on_free_avatar BIGINT,
    reviews BIGINT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS no_mailling (
    user_id BIGINT
)""")

db.commit()
