import telebot
from telebot import types
import datetime
import enum
import config
bot_token = config.Token
bot = telebot.TeleBot(bot_token, parse_mode=None)
Users = dict()


class UserStatus(enum.Enum):
	start = 0
	in_main_menu = 1
	getting_number_of_deleting_task = 2
	getting_task_description = 3
	asking_for_importance = 4
	asking_for_deadline = 5
	setting_deadline = 6


class User(object):
	users_tasks = list()
	communication_instance = UserStatus.start

	def __init__(self):
		self.users_tasks = list()
		self.communication_instance = 'start'

	def get_users_tasks(self):
		list_of_tasks = list()
		str_counter = 1
		for task in self.users_tasks:
			task_info = list()
			task_info.append(str(str_counter))
			task_info.append(str(task.task_text))
			task_info.append(str(task.task_importance))
			if task.have_deadline:
				task_info.append(task.task_deadline)
			list_of_tasks.append(task_info)
			str_counter += 1
		return list_of_tasks


class Task(object):
	task_text = ''
	task_deadline = ''
	task_importance = 0
	have_deadline = False

	def __init__(self, text, importance=1, deadlineble=False, deadline=''):
		self.task_text = text
		self.task_importance = importance
		self.have_deadline = deadlineble
		self.task_deadline = deadline


def is_right_format(deadline):
	date_format = '%d:%m-%H:%M'
	format_checker = True
	try:
		datetime.datetime.strptime(deadline, date_format)
	except ValueError:
		format_checker = False
	return format_checker


def starting_chat(user_id, keyboard):
	sending_message_text = 'Hey, this is your task manager bot.\nChoose what you want to do with bot.\n '
	keyboard.add('Add new task', 'Show my tasks', 'Delete task')
	bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
	Users[user_id].communication_instance = UserStatus.in_main_menu


def choosing_in_main_menu(user_id, got_message, keyboard):
	if got_message == 'Add new task':
		sending_message_text = 'Describe your task(50 symbols maximum)'
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.getting_task_description
	elif got_message == 'Show my tasks':
		if len(Users[user_id].users_tasks) == 0:
			sending_message_text = 'You have no tasks to complete!'
			bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		else:
			got_tasks = Users[user_id].get_users_tasks()
			sending_message_text = ''
			for task in got_tasks:
				sending_message_text += '-----------------------------------\n'
				sending_message_text += str(task[0]) + ' : '
				sending_message_text += str(task[1]) + '\n'
				sending_message_text += 'Task importance: ' + str(task[2]) + '\n'
				if len(task) > 3:
					sending_message_text += 'Task deadline: ' + str(task[3])
				sending_message_text += '-----------------------------------\n'
			bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
			Users[user_id].communication_instance = UserStatus.in_main_menu
	elif got_message == 'Delete task':
		got_tasks = Users[user_id].get_users_tasks()
		sending_message_text = got_tasks
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		sending_message_text = 'Print number of task to delete.'
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.getting_number_of_deleting_task


def getting_task_description(user_id, got_message, keyboard):
	if len(got_message) > 50:
		sending_message_text = 'Task description is too long!'
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
	else:
		sending_message_text = 'How important is the task?'
		Users[user_id].users_tasks.append(Task(got_message))
		print(Users[user_id].users_tasks)
		keyboard.add('1', '2', '3', '4', '5')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.asking_for_importance


def getting_task_importance(user_id, got_message, keyboard):
	if '1' <= got_message <= '5' and len(got_message) == 1:
		Users[user_id].users_tasks[len(Users[user_id].users_tasks) - 1].task_importance = int(got_message)
		sending_message_text = 'Do you want to set deadline?'
		keyboard.add('Yes', 'No')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.asking_for_deadline
	else:
		sending_message_text = 'Wrong task importance'
		keyboard.add('1', '2', '3', '4', '5')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)


def getting_task_deadline(user_id, got_message, keyboard):
	if got_message == 'Yes':
		Users[user_id].users_tasks[len(Users[user_id].users_tasks) - 1].have_deadline = True
		sending_message_text = 'To set deadline print date in format #DD:MM-HH:MM#'
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.setting_deadline
	elif got_message == 'No':
		sending_message_text = 'Task successfully added!'
		keyboard.add('Add new task', 'Show my tasks', 'Delete task')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.in_main_menu


def setting_task_deadline(user_id, got_message, keyboard):
	if is_right_format(got_message):
		sending_message_text = 'Task successfully added!'
		keyboard.add('Add new task', 'Show my tasks', 'Delete task')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].users_tasks[len(Users[user_id].users_tasks) - 1].task_deadline = got_message
		Users[user_id].communication_instance = UserStatus.in_main_menu
	else:
		sending_message_text = 'Wrong deadline format. Please try again'
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)


def deleting_task(user_id, number_of_task, keyboard):
	if int(number_of_task) - 1 >= len(Users[user_id].users_tasks) or int(number_of_task) < 1:
		sending_message_text = 'You have no task with number ' + str(number_of_task)
		keyboard.add('Add new task', 'Show my tasks', 'Delete task')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.in_main_menu
	elif len(Users[user_id].users_tasks) == 0:
		sending_message_text = 'You have no tasks to delete'
		keyboard.add('Add new task', 'Show my tasks', 'Delete task')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.in_main_menu
	else:
		Users[user_id].users_tasks.pop(int(number_of_task) - 1)
		sending_message_text = 'Task deleted successfully'
		keyboard.add('Add new task', 'Show my tasks', 'Delete task')
		bot.send_message(user_id, sending_message_text, reply_markup=keyboard)
		Users[user_id].communication_instance = UserStatus.in_main_menu


@bot.message_handler(content_types=['text'])
def chatting(message):
	user_id = message.chat.id
	got_message = message.text
	keyboard = types.ReplyKeyboardMarkup(True, True)
	if user_id in Users:
		instance = Users[user_id].communication_instance
		if instance == UserStatus.in_main_menu: choosing_in_main_menu(user_id, got_message, keyboard)
		elif instance == UserStatus.getting_number_of_deleting_task: deleting_task(user_id, got_message, keyboard)
		elif instance == UserStatus.getting_task_description: getting_task_description(user_id, got_message, keyboard)
		elif instance == UserStatus.asking_for_importance: getting_task_importance(user_id, got_message, keyboard)
		elif instance == UserStatus.asking_for_deadline: getting_task_deadline(user_id, got_message, keyboard)
		elif instance == UserStatus.setting_deadline: setting_task_deadline(user_id, got_message, keyboard)
	else:
		Users[user_id] = User()
		starting_chat(user_id, keyboard)


bot.infinity_polling()
