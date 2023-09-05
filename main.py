import vk_api
import time
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from config import *
from base import *


class Bot:
	def __init__(self):
		self.session = vk_api.VkApi(token=token)
		self.longpoll = VkBotLongPoll(self.session, group_id=g_id)
		self.bad_words = self.get_bad_words()
		self.base = Base(host, db_name, user, password)

	@staticmethod
	def get_bad_words():
		with open('words.txt', 'r', encoding='utf-8') as file:
			return [x.replace('\n', '') for x in file.readlines()]

	def sender(self, chat, text):
		self.session.method('messages.send', {'chat_id': chat, 'message': text, 'random_id': 0})

	def kick_user(self, uid, chat):
		self.session.method('messages.removeChatUser', {'user_id': uid, 'chat_id': chat})

	def run(self):
		for event in self.longpoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:

				text = event.obj['message']['text']
				chat = event.chat_id

				uinf = {
					'name': self.session.method('users.get', {'user_id': event.obj['message']['from_id']})[0]['first_name'],
					'id': event.obj['message']['from_id']
				}

				self.base.add_message(uinf['id'], time.time())

				if self.base.get_user(uinf['id']) == None:
					self.base.add_user(uinf['id'])

				bad = False
				for word in self.bad_words:
					if word.lower() in text.lower():
						bad = True
				if bad and uinf['id'] != admin_id:
					self.base.add_warning(uinf['id'])
					self.sender(chat, '[id' + str(uinf['id']) + '|' + uinf['name'] + f'], вы получаете предупреждение за использование нецензурной речи!\nВсего предупреждений: {self.base.get_user(uinf["id"])}')

					if self.base.get_user(uinf['id']) >= max_warns:
						self.kick_user(uinf['id'], event.chat_id)

				if uinf['id'] == admin_id:
					if 'reply_message' in event.obj['message']:
						r_id = event.obj["message"]["reply_message"]["from_id"]
						if r_id != admin_id:
							if text == 'варн':
								self.base.add_warning(r_id)
								self.sender(chat, '[id' + str(r_id) + '|' + self.session.method('users.get', {'user_id': r_id})[0]['first_name'] + f'], вы получаете предупреждение от админа!\nВсего предупреждений: {self.base.get_user(uinf["id"])}')
								if self.base.get_user(uinf['id']) >= max_warns:
									self.kick_user(uinf['id'], event.chat_id)

				else:
					u_msgs = self.base.get_messages(uinf['id'])
					bad_messages = [x for x in u_msgs if x > time.time() - 60]

					if len(bad_messages) > max_msgs_per_minutes:
						self.base.add_warning(uinf['id'])
						self.sender(chat, '[id' + str(uinf['id']) + '|' + uinf[
							'name'] + f'], вы получаете предупреждение за спам!\nВсего предупреждений: {self.base.get_user(uinf["id"])}')

						if self.base.get_user(uinf['id']) >= max_warns:
							self.kick_user(uinf['id'], event.chat_id)


if __name__ == '__main__':
	Bot().run()
