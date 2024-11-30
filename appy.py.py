import random
import string
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ����� �� ����� ���� SQLite
conn = sqlite3.connect('hmstr_mining_project.db', check_same_thread=False)
cursor = conn.cursor()

# ��� ����� (���� ����� �� ����� ����)
class User:
    def __init__(self, user_id, has_paid, invite_link=None, invite_count=0):
        self.user_id = user_id
        self.has_paid = has_paid
        self.invite_link = invite_link
        self.invite_count = invite_count

    def process_payment(self):
        if not self.has_paid:
            self.has_paid = True
            self.invite_link = generate_invite_link(self.user_id)
            print(f"Payment successful. Your invite link: {self.invite_link}")
        else:
            print("You have already paid.")

    def increment_invites(self):
        self.invite_count += 1
        print(f"Your invite count is now: {self.invite_count}")

# ���� ���� ����� ��� ���� ����� �� ���
def generate_invite_link(user_id):
    return f"https://example.com/invite/{user_id}/{generate_random_string(6)}"

# ���� ���� ����� ���� ������ ���� ���
def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# ���� ������ ����� ���� �� ����� ����
def add_user_to_db(user_id):
    cursor.execute("INSERT INTO users (user_id, has_paid, invite_link, invite_count) VALUES (?, ?, ?, ?)",
                   (user_id, False, None, 0))
    conn.commit()

# ���� ������ ������� ����� �� ����� ����
def get_user_from_db(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    return User(user_data[0], user_data[1], user_data[2], user_data[3])

# ���������� ����� ������ � ��� ���� �����
def update_payment_and_invite_link(user_id):
    user = get_user_from_db(user_id)
    user.process_payment()
    cursor.execute("UPDATE users SET has_paid = ?, invite_link = ? WHERE user_id = ?",
                   (user.has_paid, user.invite_link, user.user_id))
    conn.commit()

# ���������� ����� ���ʝ��
def update_invite_count(user_id):
    user = get_user_from_db(user_id)
    user.increment_invites()
    cursor.execute("UPDATE users SET invite_count = ? WHERE user_id = ?",
                   (user.invite_count, user.user_id))
    conn.commit()

# ����� ���� ������� �� ����� ���� (ǐ� ���� ������ ����)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    has_paid BOOLEAN,
    invite_link TEXT,
    invite_count INTEGER
)
''')
conn.commit()

# ���� ���� (�������� ���� �����)
@app.route('/')
def index():
    # ��� �흘��� �� ����� ����� �� ���� URL ������ ��� ����
    user_id = request.args.get('user_id', type=int, default=1)  # ��� �� ��� ��� �� 1 ����� ����� ���
    user = get_user_from_db(user_id)
    return render_template('index.html', user=user)

# ���� ������
@app.route('/pay/<int:user_id>', methods=['GET', 'POST'])
def pay(user_id):
    if request.method == 'POST':
        # ������ 400 ���
        update_payment_and_invite_link(user_id)
        return redirect(url_for('index', user_id=user_id))
    return render_template('pay.html', user_id=user_id)

# ���� ���� �� ������ (�������� ���� ����)
@app.route('/invite/<int:user_id>')
def invite(user_id):
    user = get_user_from_db(user_id)
    return render_template('invite.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
