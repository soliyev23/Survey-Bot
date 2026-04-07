from aiogram.fsm.state import StatesGroup, State

class SurveyState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    question = State()
    extra_comment = State()

class AdminState(StatesGroup):
    waiting_for_question_number = State()
    waiting_for_admin_id = State()
    waiting_for_remove_admin_id = State()

