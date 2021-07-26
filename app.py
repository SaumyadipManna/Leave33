from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_mysqldb import MySQL
import MySQLdb
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'MySecretKey'
mysql = MySQL(app)


# Admin User ID ,PASSUORD
class User:
    def __init__(self, uid, username, password):
        self.uid = uid
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(uid=1, username='SaumyadipManna', password='Saumya@1234'))
users.append(User(uid=2, username='MannaSaumyadip', password='1234@Saumya'))

# database
conn = MySQLdb.connect("localhost", "root", "Saumya@1234", "leaveapp")
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Saumya@1234'
app.config['MYSQL_DB'] = 'leaveapp'

cursor = conn.cursor()

# chose="NULL"


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.uid == session['user_id']][0]
        g.user = user


@app.route('/')
def home():
    return render_template('index.htm')

# ADMIN LOGIN PAGE


@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
    try:
        if request.method == 'POST':
            session.pop('user_id', None)
            username = request.form['username']
            password = request.form['password']
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.uid
                return redirect(url_for('admin_1st_page'))
            return redirect(url_for('AdminLogin'))
    except:
        return 'Incorrect username/password!'

    return render_template('AdminLogin.htm')


# ADMIN 1st PASSWORD


@app.route('/admin_1st_page')
def admin_1st_page():
    if not g.user:
        return redirect(url_for('AdminLogin'))
    return render_template('admin_1st_page.htm')


# CREATE ACCOUNT PAGE


@app.route('/Add_EMP', methods=['GET', 'POST'])
def Add_EMP():
    if request.method == "POST":
        details = request.form
        name = details['MyName']
        email = details['MyEmail']
        pn_no = details['pn']
        dept = details['Mydept']
        age = details['Myage']
        uid = details['User']
        password = details['pass']
        cpass = details['Cpass']
        gender = details['Gender']
        if password == cpass:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO emp_table2(name, email, pn_no, dept, age, uid, password, gender) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)",
                        (name, email, pn_no, dept, age, uid, password, gender))
            mysql.connection.commit()
            cur.close()
            return 'success'
        else:
            return'CHECK PASSWORD'

    return render_template('Add_EMP.htm')

# STORE CERATE_ACCOUNT DATA IN DB

# Accept_Decline


@app.route('/Accept_Decline', methods=['GET', 'POST'])
def Accept_Decline():
    if request.method == "POST":
        details = request.form
        name = details['o']
        s_date = details['S']
        status = details['AdminChose']
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE staff SET Status=%s WHERE name=%s and stat_date=%s ", (status, name, s_date))
        mysql.connection.commit()
        cur.close()
    cursor.execute(
        "SELECT name,stat_date,end_date,reason,ScheduledBy,SubmissionDate FROM staff")
    data = cursor.fetchall()

    return render_template('Accept_Decline.htm', value=data)

# Emp_detalls


@app.route('/Emp_detalls')
def Emp_detalls():
    cursor.execute("select * from emp_table2")
    data = cursor.fetchall()  # data from database
    # return render_template("example.html", value=data)
    return render_template('Emp_detalls.htm', value=data)

# Emp_Leave_Histry for admin


@app.route('/Emp_Leave_Histry', methods=['GET', 'POST'])
def Emp_Leave_Histry():
    try:
        if request.method == "POST":
            details = request.form
            s_date = details['SDate']
            l_date = details['EDate']

        cursor.execute(
            "select * from staff where SubmissionDate between %s and %s ", (s_date, l_date))
        data = cursor.fetchall()
    except:
        cursor.execute("select * from staff")
        data = cursor.fetchall()

    #     cursor.execute("select * from staff where name=%s",(name))
    #     data = cursor.fetchall()

    # statu=janina_ki_kor6i.status
    return render_template('Emp_Leave_Histry.htm', value=data)


# staff part

@app.route('/s_l', methods=['GET', 'POST'])
def s_l():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM emp_table2 WHERE uid = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['uid']
            return redirect(url_for('StaffAfterLogin'))
        else:
            return 'Incorrect username/password!'
    return render_template('s_l.htm')

# StaffAfterLogin


@app.route('/StaffAfterLogin')
def StaffAfterLogin():
    return render_template('StaffAfterLogin.htm')


# staff_1st_page
@app.route('/staff_1st_page', methods=['GET', 'POST'])
def staff_1st_page():
    if request.method == "POST":
        details = request.form
        name = details['MyName']
        start = details['start']
        end = details['end']
        reason = details['reason']
        ScheduledBy = details['RSNBY']
        SubmissionDate = details['S_date']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO staff(name, stat_date,end_date,reason,ScheduledBy,SubmissionDate) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, start, end, reason, ScheduledBy, SubmissionDate))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('staff_1st_page.htm')


# staff_leave_history
@app.route('/staff_leave_history', methods=['GET', 'POST'])
def staff_leave_history():
    try:
        if request.method == "POST":
            details = request.form
            name = details['ByName']
        cursor.execute(
            "select * from staff where name='{name}'".format(name=name))
        data = cursor.fetchall()
    except:
        cursor.execute("select * from staff")
        data = cursor.fetchall()

    return render_template('staff_leave_history.htm', value=data)


if __name__ == "__main__":
    app.run(debug=false,host="0.0.0.0")
