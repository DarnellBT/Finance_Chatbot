DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Chats;
DROP TABLE IF EXISTS Messages;

CREATE TABLE Users
(
    userId   INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(32)  NOT NULL,
    password VARCHAR(256) NOT NULL
);

CREATE TABLE Chats
(
    chatId  INTEGER PRIMARY KEY AUTOINCREMENT,
    company VARCHAR(9),
    year    VARCHAR(4),
    userId REFERENCES Users (userId)
);

CREATE TABLE Messages
(
    messageId INTEGER PRIMARY KEY AUTOINCREMENT,
    type      VARCHAR(9) NOT NULL, -- only can be "userQuery" or "answer"
    content   TEXT       NOT NULL,
    chatId REFERENCES Chats (chatId)
);
