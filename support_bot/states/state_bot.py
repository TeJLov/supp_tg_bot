from aiogram.fsm.state import State, StatesGroup

class FSMMenu(StatesGroup):
    mmenu = State()         # старт меню
    where = State()         # Направление
    menu_supp_1 = State()   # тема чаво
    menu_supp_2 = State()   # чаво
    menu_mentor = State()   # выбор ментора (направление)
    them_mentor = State()   # тема обращения
    question = State()      # Вопрос
    dialog = State()        # диалог
    work_eval = State()     # Оценка диалога
    feedback = State()      # Отзыв/Предложение

class FSMMenuStaff(StatesGroup):
    mmenu = State()         # меню работников
    list_referens = State() # список обращений
    pagin = State()
    dialog = State()
    statistic = State()
