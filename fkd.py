from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Humor0705%40@localhost/restaurant_booking'
db = SQLAlchemy(app)

# 数据库模型
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    persons = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(200))
    agreement = db.Column(db.Boolean, nullable=False)

# 初始化数据库
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def book_table():
    # 获取所有预订记录
    reservations = Reservation.query.all()
    message = None

    if request.method == 'POST':
        action = request.form['action']
        email = request.form['email']

        # 新增预订
        if action == 'reserve':
            date = request.form['date']
            time = request.form['time']
            persons = request.form['persons']
            notes = request.form.get('notes', '')
            agreement = 'agreement' in request.form

            if agreement:
                new_reservation = Reservation(email=email, date=date, time=time, persons=persons, notes=notes, agreement=agreement)
                db.session.add(new_reservation)
                db.session.commit()
                message = f'Table successfully reserved for {persons} person(s) on {date} at {time}. Confirmation will be sent to {email}.'
            else:
                message = 'Please agree to the terms to make a reservation.'

        # 修改预订
        elif action == 'change':
            new_date = request.form['new_date']
            new_time = request.form['new_time']
            reservation = Reservation.query.filter_by(email=email).first()
            if reservation:
                reservation.date = new_date
                reservation.time = new_time
                db.session.commit()
                message = f'Reservation updated to {new_date} at {new_time}.'
            else:
                message = 'No reservation found for this email.'

        # 取消预订
        elif action == 'cancel':
            reservation = Reservation.query.filter_by(email=email).first()
            if reservation:
                db.session.delete(reservation)
                db.session.commit()
                message = 'Reservation canceled.'
            else:
                message = 'No reservation found for this email.'

        reservations = Reservation.query.all()

    return render_template_string(get_html_form(message, reservations))


def get_html_form(message=None, reservations=None):
    # 构建预订列表的表格
    reservation_table = """
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Date</th>
                <th>Time</th>
                <th>Persons</th>
                <th>Notes</th>
                <th>Agreement</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in reservations:
        reservation_table += f"""
            <tr>
                <td>{r.id}</td>
                <td>{r.email}</td>
                <td>{r.date}</td>
                <td>{r.time}</td>
                <td>{r.persons}</td>
                <td>{r.notes}</td>
                <td>{'Yes' if r.agreement else 'No'}</td>
            </tr>
        """
    reservation_table += "</tbody></table>" if reservations else "<p>No reservations yet.</p>"

    # 返回完整HTML模板
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Table Reservation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 900px;
                text-align: center;
            }}
            .form-container {{
                margin-bottom: 20px;
            }}
            form {{
                display: flex;
                flex-direction: column;
                margin-bottom: 20px;
            }}
            label {{
                margin: 10px 0 5px;
                text-align: left;
            }}
            input, select {{
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
            }}
            button {{
                padding: 10px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
                margin-top: 10px;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            table th, table td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}
            table th {{
                background-color: #f4f4f4;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="form-container">
                <h2>Book a Table</h2>
                {f'<p>{message}</p>' if message else ''}
                <form method="POST">
                    <label for="email">Email Address:</label>
                    <input type="email" id="email" name="email" required>

                    <label for="date">Date:</label>
                    <input type="date" id="date" name="date" required>

                    <label for="time">Time:</label>
                    <select id="time" name="time" required>
                        {''.join([f'<option value="{hour}:00">{hour}:00</option><option value="{hour}:30">{hour}:30</option>' for hour in range(10, 22)])}
                    </select>

                    <label for="persons">Number of Persons:</label>
                    <select id="persons" name="persons" required>
                        {''.join([f'<option value="{i}">{i}</option>' for i in range(1, 7)])}
                    </select>

                    <label for="notes">Additional Notes:</label>
                    <input type="text" id="notes" name="notes">

                    <label>
                        <input type="checkbox" name="agreement" required> I agree to the terms and conditions
                    </label>

                    <button type="submit" name="action" value="reserve">Reserve</button>
                </form>
            </div>
            <div class="form-container">
                <h2>Change Reservation</h2>
                <form method="POST">
                    <label for="email">Email Address:</label>
                    <input type="email" id="email" name="email" required>

                    <label for="new_date">New Date:</label>
                    <input type="date" id="new_date" name="new_date" required>

                    <label for="new_time">New Time:</label>
                    <select id="new_time" name="new_time" required>
                        {''.join([f'<option value="{hour}:00">{hour}:00</option><option value="{hour}:30">{hour}:30</option>' for hour in range(10, 22)])}
                    </select>

                    <button type="submit" name="action" value="change">Change</button>
                </form>
            </div>
            <div class="form-container">
                <h2>Cancel Reservation</h2>
                <form method="POST">
                    <label for="email">Email Address:</label>
                    <input type="email" id="email" name="email" required>

                    <button type="submit" name="action" value="cancel">Cancel</button>
                </form>
            </div>
            <h2>Reservation List</h2>
            {reservation_table}
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8001)
