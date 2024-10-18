-- A SQL script that creates a table called users with the following conditions
-- id, integer, never null, auto increment and primary key
-- email, string (255 characters), never null and unique
-- name, string (255 characters)
-- If the table already exists, your script should not fail
-- The script can be executed on any database
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	email varchar(255) NOT UNIQUE,
	name vachar(255) 
)
