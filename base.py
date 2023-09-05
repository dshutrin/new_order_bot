from MySQLdb import connect


class Base:
	def __init__(self, host, base, user, password):
		self.con = connect(host=host, database=base, user=user, password=password)
		self.cur = self.con.cursor()
		self.post("create table if not exists users(id int primary key auto_increment, vk_id int unique, warnings int);")
		self.post("create table if not exists msgs(from_id int, m_date text, foreign key(from_id) references users (vk_id));")

	def post(self, query):
		self.cur.execute(query)
		self.con.commit()

	def get(self, query):
		self.cur.execute(query)
		a = self.cur.fetchall()
		return [x[0] for x in a]

	def add_warning(self, user_id):
		self.post(f'update users set warnings = warnings + 1 where vk_id = {user_id};')

	def get_warnings(self, user_id):
		return self.get(f'select warnings from users where vk_id = {user_id};')

	def add_user(self, user_id):
		self.post(f'insert into users(vk_id, warnings) values({user_id}, 0);')

	def get_user(self, user_id):
		a = self.get(f'select warnings from users where vk_id = {user_id};')
		if a:
			return int(a[0])
		return None

	def add_message(self, uid, tme):
		self.post(f'insert into msgs(from_id, m_date) values({uid}, "{tme}");')

	def get_messages(self, uid):
		return [float(x) for x in self.get(f'select m_date from msgs where from_id={uid};')]


if __name__ == '__main__':
	b = Base('localhost', 'new_db', 'root', 'Ltkmnf-02')
	print(b.get_user(111))
