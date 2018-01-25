--
-- Файл сгенерирован с помощью SQLiteStudio v3.1.1 в Ср янв 24 14:17:06 2018
--
-- Использованная кодировка текста: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: Command
CREATE TABLE Command (
    config_id INTEGER REFERENCES Config (id) ON DELETE CASCADE,
    name      STRING,
    time      STRING,
    days      INTEGER
);

INSERT INTO Command (config_id, name, time, days) VALUES (1, 'hw', '18:30, 19:20', '2,4,6');
INSERT INTO Command (config_id, name, time, days) VALUES (1, 'about', '14:00', 2);
INSERT INTO Command (config_id, name, time, days) VALUES (2, 'hw', '9:00, 10:00', '5,6,6');
INSERT INTO Command (config_id, name, time, days) VALUES (2, 'help', '16:00', 4);
INSERT INTO Command (config_id, name, time, days) VALUES (1, 'ege', '9:00', 7);

-- Таблица: Config
CREATE TABLE Config (
    user_id INTEGER REFERENCES User (id) ON DELETE CASCADE
                                         ON UPDATE CASCADE
                    NOT NULL
                    UNIQUE,
    id      INTEGER PRIMARY KEY AUTOINCREMENT
                    NOT NULL
);

INSERT INTO Config (user_id, id) VALUES (194234, 1);
INSERT INTO Config (user_id, id) VALUES (6785673, 2);

-- Таблица: User
CREATE TABLE User (
    id         INTEGER PRIMARY KEY
                       NOT NULL,
    domain,
    first_name STRING,
    last_name  STRING,
    personal   TEXT,
    role       STRING
);

INSERT INTO User (id, domain, first_name, last_name, personal, role) VALUES (194234, 'thuko', 'Karim', 'Azimov', NULL, 'moder');
INSERT INTO User (id, domain, first_name, last_name, personal, role) VALUES (6785673, 'lordandrewww1', 'Андрей', 'Володин', NULL, NULL);

-- Индекс: MemberInfo
CREATE UNIQUE INDEX MemberInfo ON User (
    id,
    domain,
    first_name,
    last_name
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
