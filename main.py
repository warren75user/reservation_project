from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

HOST = 'localhost'
PORT = 8001

class BookingHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.get_html_form().encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urlparse.parse_qs(post_data.decode('utf-8'))
        message = self.process_booking(data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response = self.get_html_form(message)
        self.wfile.write(response.encode('utf-8'))

    def get_html_form(self, message=None):
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
                    width: 300px;
                    text-align: center;
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

                    <button type="submit">Reserve</button>
                </form>
            </div>
        </body>
        </html>
        """

    def process_booking(self, data):
        email = data.get('email', [''])[0]
        date = data.get('date', [''])[0]
        time = data.get('time', [''])[0]
        persons = data.get('persons', [''])[0]
        notes = data.get('notes', [''])[0]
        agreement = data.get('agreement', [None])[0]

        if agreement:
            return f'Table successfully reserved for {persons} person(s) on {date} at {time}. Confirmation will be sent to {email}.'
        else:
            return 'Please agree to the terms to make a reservation.'

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), BookingHandler)
    print(f'Server running on http://{HOST}:{PORT}...')
    server.serve_forever()
