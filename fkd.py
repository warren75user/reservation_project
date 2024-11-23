from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Pirog123@localhost/restaurant_db'
db = SQLAlchemy(app)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    persons = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(200))
    agreement = db.Column(db.Boolean, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def book_table():
    if request.method == 'POST':
        action = request.form['action']
        email = request.form['email']

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

        elif action == 'cancel':
            reservation = Reservation.query.filter_by(email=email).first()
            if reservation:
                db.session.delete(reservation)
                db.session.commit()
                message = 'Reservation canceled.'
            else:
                message = 'No reservation found for this email.'

        return render_template_string(get_html_form(message))

    return render_template_string(get_html_form())

def get_html_form(message=None):
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
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 900px;
                text-align: center;
                display: flex;
                justify-content: space-between;
            }}
            .form-container {{
                width: 30%;
            }}
            form {{
                display: flex;
                flex-direction: column;
            }}
            label {{
                margin: 10px 0 5px;
                text-align: left;
            }}
            input[type="date"], select, input[type="text"], input[type="email"] {{
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
            input[type="checkbox"] {{
                margin-right: 5px;
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
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8001)
