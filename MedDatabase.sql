DROP DATABASE IF EXISTS `medBot`;
CREATE DATABASE `medBot`;
USE `medBot`;

-- define varchar limit below, TEXT allows for upto 65000
CREATE TABLE IF NOT EXISTS medBot.CaseReports (
	id INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    casereport TEXT NOT NULL,
    discussion VARCHAR(1024) NOT NULL,
    imageAddress VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id)
);

-- check for null in image address 
CREATE TABLE IF NOT EXISTS medBot.colonCancer (
	id INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    casereport TEXT NOT NULL,
    imageAddress VARCHAR(1024) NULL, 
    diagnosis VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medBot.lungCancer (
	id INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    casereport TEXT NOT NULL,
    imageAddress VARCHAR(1024) NULL, 
    diagnosis VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medBot.leukemia (
	id INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    casereport TEXT NOT NULL,
    imageAddress VARCHAR(1024) NULL, 
    diagnosis VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medBot.brainTumor (
	id INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    casereport TEXT NOT NULL,
    imageAddress VARCHAR(1024) NULL, 
    diagnosis VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id)
);


ALTER TABLE medBot.colonCancer MODIFY imageAddress VARCHAR(1024) NULL;
-- CREATE TABLE IF NOT EXISTS medBot.kidneyCancer (
-- 	id INT NOT NULL,
--     title VARCHAR(1024) NOT NULL,
--     casereport TEXT NOT NULL,
--     discussion VARCHAR(1024) NULL,
--     imageAddress VARCHAR(1024) NOT NULL,
--     diagnosis VARCHAR(1024) NOT NULL,
--     PRIMARY KEY (id)
-- );

Describe colonCancer;

select title from brainTumor;

SELECT casereport, discussion, imageAddress FROM caseReports ORDER BY RAND() LIMIT 1;


GRANT ALL PRIVILEGES ON medBot.* TO 'root'@'localhost';
ALTER USER 'root'@'localhost' IDENTIFIED BY 'zahab';
FLUSH PRIVILEGES;

SELECT host, user FROM mysql.user;

UPDATE mysql.user SET host='%' WHERE user='root';
FLUSH PRIVILEGES;

SELECT * FROM medBot.lungCancer;

DELETE FROM medBot.lungCancer 
WHERE id = 7;


