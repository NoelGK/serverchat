CREATE DATABASE serverchat;
\c serverchat;

CREATE TABLE users (
    username VARCHAR(100) PRIMARY KEY,
    hassed_password BYTEA,
    salt BYTEA
);