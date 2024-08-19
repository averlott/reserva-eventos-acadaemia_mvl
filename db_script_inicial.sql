
create database bookingEvents;
use bookingEvents;

CREATE TABLE IF NOT EXISTS admins(
    id int AUTO_INCREMENT primary key,
    username varchar(255),
    password varchar(255)
);

CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    password varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(255),
    type varchar(50) ,
    capacity integer,
    price float
);

CREATE TABLE IF NOT EXISTS bookings (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(255),
    type varchar(50) ,
    seats integer,
    price float
);

INSERT INTO admins (username, password) VALUES ('admin', 'admin');

INSERT INTO users (name, email, password) VALUES ('user','user@user', 'user');

INSERT INTO events (name, type, capacity, price) VALUES ('charla','Charla', 40, 0);

INSERT INTO bookings (name, type, seats, price) VALUES ('charla','Charla', 5, 0);

