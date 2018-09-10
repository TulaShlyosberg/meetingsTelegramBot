DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS lectures;
DROP TABLE IF EXISTS lectors;
DROP TABLE IF EXISTS time_table;
DROP TABLE IF EXISTS org_adresses;
DROP TABLE IF EXISTS organizations;

CREATE TABLE org_adresses(
office_id INTEGER PRIMARY KEY AUTOINCREMENT,
org_name VARCHAR(100),
org_url VARCHAR(100),
phone VARCHAR(16),
city VARCHAR(30) NOT NULL,
adress VARCHAR(100) NOT NULL,
seat_limit INTEGER DEFAULT -1,
rate DEFAULT 0,
UNIQUE (office_id, seat_limit)
);

CREATE INDEX city_ind ON org_adresses(city);
CREATE INDEX org_name_ind ON org_adresses(org_name);

CREATE TABLE time_table(
lecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
office_id INTEGER,
lecture_date DATE NOT NULL,
time_begin VARCHAR(5) NOT NULL,
time_end VARCHAR(5) NOT NULL,
busy_seats INTEGER DEFAULT 0,
theme VARCHAR(50) NOT NULL,
price INTEGER DEFAULT -1,
url VARCHAR(200) DEFAULT 'https://my.timepad.ru/all/categories/nauka/events?approved=true&date=&mode=&online=true&paid=true',
FOREIGN KEY (office_id)
REFERENCES org_adresses(office_id)
ON DELETE SET NULL
ON UPDATE CASCADE
);