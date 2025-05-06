# BCG X Financial Chat bot

---

## Running App

To run the chatbot you would run the following in a terminal in the same directory as app.py:

### Setup Environment

```shell
python -m venv .venv
cd .venv
cd Scripts
python ativate_this.py
cd ..
cd ..
```

### Install Requirements

```shell
pip install -r requirements.txt
```

### Run App

```shell
python app.py
```

After this the chatbot should be running on http://127.0.0.1:5000/ which can be viewed in a web browser.

## Logging In

The website fill first ask for a username and password so that a user can save their chats. Each chat will have its own username and password.

---

## Choosing Company

This chatbot will first ask the user what company they would like information on. The user has the options to answer with either:

+ Apple
+ Microsoft
+ Tesla

---

## Choosing Year

The chatbot will ask the user what year of statistics they would like to see for the previously chosen company. Each company can be asked about the following years:

| Company   | Years            |
|-----------|------------------|
| Apple     | 2021, 2022, 2023 |
| Microsoft | 2022, 2023, 2024 |
| Tesla     | 2021, 2022, 2023 |

---

## Analysis

The chatbot will ask if the user has any questions about the chosen company for the selected year. The user can ask one of the following questions:

+ What is the total revenue?
+ What is the net income?
+ What are the total assets?
+ What are the total liabilities?
+ What is the cash flow from operating activities?
+ How has total revenue changed over the last year?
+ How has net income changed over the last year?
+ How have total assets changed over the last year?
+ How have total liabilities changed over the last year?
+ How has cash flow from operating activities changed over the last year?

---

## Change Company/Year

If at any point the user would like to change the company being analysed or the year. The user can ask the following:

+ Can I look at a different year?
+ Can I look at a different company?

---

## Limitations

Some limitations of the chatbot are that it can only talk about preset topics and that data for each company are only from three different years for each.
