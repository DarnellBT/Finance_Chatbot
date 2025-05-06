"""
BCG X Flask Chatbot
"""
from flask import Flask, jsonify, render_template, request, Response, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import math
import pandas as pd
import sqlite3
import typing
from werkzeug.security import generate_password_hash, check_password_hash

dataframe: pd.DataFrame = pd.read_csv('analysis.csv')
companies: list[str] = dataframe['Company'].unique().tolist()
dataframe['Revenue Growth (%)']: pd.Series = dataframe.groupby(['Company'])['Total Revenue'].pct_change() * 100
dataframe['Net Income Growth (%)']: pd.Series = dataframe.groupby(['Company'])['Net Income'].pct_change() * 100
dataframe['Asset Growth (%)']: pd.Series = dataframe.groupby(['Company'])['Total Assets'].pct_change() * 100
dataframe['Liability Growth (%)']: pd.Series = dataframe.groupby(['Company'])['Total Liabilities'].pct_change() * 100
dataframe['Cash Flow from Operating Activities Growth (%)']: pd.Series = dataframe.groupby(['Company'])['Cash Flow from Operating Activities'].pct_change() * 100

app: Flask = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'SECRET_KEY'
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
CSRFProtect(app)


def generate_text_answer(user_query: str) -> str:
    """
    Generates text response from input text.
    :param user_query: input text.
    :return: response text
    """

    response: str
    matched_company: bool = dataframe['Company'] == session['company']
    matched_year: bool = dataframe['Year'].astype(str) == session['year']
    company_dataframe: pd.DataFrame = dataframe[matched_company & matched_year]

    def generate_growth_question_answer(column: str, metric_name: str) -> str:
        """
        Generates text response from input text.
        :param column:
        :param metric_name:
        :return:
        """

        string: str
        answer: str
        growth: float = company_dataframe[column].tolist()[0]
        if math.isnan(growth):
            answer = 'Sorry, I do not have this information for that year.'
        else:
            if growth < 0:
                string = 'decreased'
            else:  # includes 0
                string = 'increased'
            answer = f'The {metric_name} {string} by {growth:.3f}% over the last year.'

        return answer

    predefined_responses: dict[str, str] = {
        'What is the total revenue?': f'The total revenue is {company_dataframe['Total Revenue'].tolist()[0]:,} million USD.',
        'What is the net income?': f'The net income is {company_dataframe['Net Income'].tolist()[0]:,} million USD.',
        'What are the total assets?': f'The total assets are {company_dataframe['Total Assets'].tolist()[0]:,} million USD.',
        'What are the total liabilities?': f'The total liabilities are {company_dataframe['Total Liabilities'].tolist()[0]:,} million USD.',
        'What is the cash flow from operating activities?': f'The total cash flow from operating activities are {company_dataframe['Cash Flow from Operating Activities'].tolist()[0]:,} million USD.',
        'How has total revenue changed over the last year?': generate_growth_question_answer('Revenue Growth (%)', 'total revenue has'),
        'How has net income changed over the last year?': generate_growth_question_answer('Net Income Growth (%)', 'net income has'),
        'How have total assets changed over the last year?': generate_growth_question_answer('Asset Growth (%)', 'total assets have'),
        'How have total liabilities changed over the last year?': generate_growth_question_answer('Liability Growth (%)', 'total liabilities have'),
        'How has cash flow from operating activities changed over the last year?': generate_growth_question_answer('Cash Flow from Operating Activities Growth (%)', 'cash flow from operating activities has'),
        'Can I look at a different year?': 'Sure! Which year would you like analysis for?',
        'Can I look at a different company?': 'Sure! Which company would you like analysis for?'
    }

    if user_query == 'Can I look at a different year?':
        session['year'] = None
    elif user_query == 'Can I look at a different company?':
        session['company'] = session['year'] = None

    response = predefined_responses.get(user_query, 'Sorry, I can only provide information on predefined queries.')

    return response


@app.after_request
def set_secure_headers(response: Response) -> Response:
    """
    Sets secure headers.
    :param response: response after request.
    :return: Response with secure headers.
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    return response


@app.route('/', methods=('GET',))
def index() -> str:
    """
    Renders index page.
    :return: rendered index template.
    """

    return render_template('index.html')


@app.route('/process', methods=('POST',)) # broken?
def process() -> Response:
    """
    Processes input data.
    :return: Response data
    """
    answer: str = ''
    connection: sqlite3.Connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    database_cursor: sqlite3.Cursor = connection.cursor()
    user_query: str = request.form['userQuery']
    # Set initial response to an error before testing for all other cases.
    # If none of the following If statements are true then the response will be this error.
    response: Response = jsonify({
        'error': 'Missing query'
    })

    if session.get('company', False):
        if session.get('year', False):
            if user_query:
                answer = generate_text_answer(user_query)
        else:
            matched_company: bool = dataframe['Company'] == session['company']
            years: list[str] = dataframe[matched_company]['Year'].astype(str).values.tolist()

            if user_query in years:
                session['year'] = user_query
                answer = f'What would you like to know about {session['company']} in the year {session['year']}?'
            else:
                answer = 'I do not have information for that year. Which other year would you like analysis for?'
    else:
        if user_query in companies:
            session['company'] = user_query
            answer = f'What year are you interested in for {session['company']}?'
        else:
            answer = 'Sorry, I do not know that company. Which other company would you like analysis for?'

    if session.get('company', False):
        database_cursor.execute('''
            UPDATE Chats
            SET company = ?
            WHERE chatId = ?;
        ''', (session['company'], session['chat']))
    else:
        database_cursor.execute('''
            UPDATE Chats
            SET company = NULL
            WHERE chatId = ?;
        ''', (session['chat'],))

    if session.get('year', False):
        database_cursor.execute('''
            UPDATE Chats
            SET year = ?
            WHERE chatId = ?;
        ''', (session['year'], session['chat']))
    else:
        database_cursor.execute('''
            UPDATE Chats
            SET year = NULL
            WHERE chatId = ?;
        ''', (session['chat'],))

    if answer:
        database_cursor.execute('''
            INSERT INTO Messages(type, content, chatId)
            VALUES ('userQuery', ?, ?);
        ''', (user_query, session['chat']))
        database_cursor.execute('''
            INSERT INTO Messages(type, content, chatId)
            VALUES ('answer', ?, ?);
        ''', (answer, session['chat']))

        response = jsonify({
            'answer': answer
        })

    connection.commit()
    connection.close()

    return response


@app.route('/login', methods=('GET', 'POST'))
def login() -> Response:
    username: str = request.form['username']
    password: str = request.form['password']
    connection: sqlite3.Connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    database_cursor: sqlite3.Cursor = connection.cursor()

    record: tuple[int, str, str] = database_cursor.execute('''
        SELECT * FROM Users
        WHERE username = ?;
    ''', (username,)).fetchone()

    if record:
        if check_password_hash(record[2], password):
            chat_id: int
            chat_company: str
            chat_year: str
            chat_id, chat_company, chat_year = database_cursor.execute('''
                SELECT chatId, company, year FROM Chats
                WHERE userId = ?;
            ''', (record[0],)).fetchone()
            messages: list[tuple[int, str, str, int]] = database_cursor.execute('''
                SELECT * FROM Messages
                WHERE chatId = ?;
            ''', (chat_id,)).fetchall()

            # Initialises session data on login.
            session['user_id'] = record[0]
            session['username'] = record[1]
            session['chat'] = chat_id
            session['company'] = chat_company
            session['year'] = chat_year

            # Populates chat with any previous chat logs.
            history: list[dict[str, str]] = []
            for row in range(0, len(messages), 2):
                history.append({messages[row][1]: messages[row][2], messages[row + 1][1]: messages[row + 1][2]})

            response = jsonify({
                'success': 'login successful!',
                'history': history
            })
        else:
            response: Response = jsonify({
                'error': 'Authentication error.'
            })
    else:
        database_cursor.execute('''
            INSERT INTO Users(username, password)
            VALUES (?, ?);
        ''', (username, generate_password_hash(password)))
        user_id: int = database_cursor.lastrowid
        database_cursor.execute('''
            INSERT INTO Chats(company, year, userId)
            VALUES (NULL, NULL, ?);
        ''', (user_id,))

        # Initialises session data onv first login.
        chat_id: int = database_cursor.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        session['chat'] = chat_id

        response = jsonify({
            'success': 'login successful!'
        })

    connection.commit()
    connection.close()

    return response


@app.route('/logout', methods=('GET',))
def logout() -> Response:

    session_keys: typing.KeysView[str] = dict(session).keys()
    for key in session_keys:
        if key != 'csrf_token':
            session.pop(key)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, threaded=True, debug=True)
