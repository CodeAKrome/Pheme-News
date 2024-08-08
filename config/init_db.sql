DROP DATABASE if EXISTS news;
CREATE DATABASE news;
USE news;

CREATE TABLE Source (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    type CHAR(8),
    country CHAR(2),
    affiliation VARCHAR(255)
);

CREATE TABLE Object (
    id INT PRIMARY KEY,
    text VARCHAR(255)
);

CREATE TABLE ObjectMap (
    id INT PRIMARY KEY,
    object_id INT,
    FOREIGN KEY (object_id) REFERENCES Object(id)
);

CREATE TABLE Kind (
    id INT PRIMARY KEY,
    text VARCHAR(255)
);

CREATE TABLE Entity (
    id INT PRIMARY KEY,
    kind INT,
    text VARCHAR(255),
    FOREIGN KEY (kind) REFERENCES Kind(id)
);

CREATE TABLE EntityMap (
    id INT PRIMARY KEY,
    entity_id INT,
    sentiment ENUM('positive','negative'),
    objectivity FLOAT,
    FOREIGN KEY (entity_id) REFERENCES Entity(id)
);

CREATE TABLE Image (
    id INT PRIMARY KEY,
    copy_id INT,
    file VARCHAR(255),
    objects INT,
    FOREIGN KEY (objects) REFERENCES ObjectMap(id)
);


CREATE TABLE Copy (
    id INT PRIMARY KEY,
    story_id INT,
    image_id INT,
    text VARCHAR(255),
    entitymap_id INT,
    sentiment ENUM('positive','negative'),
    objectivity FLOAT,
    summary BOOLEAN,
    image BOOLEAN,
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (entitymap_id) REFERENCES EntityMap(id)
);



CREATE TABLE Story (
    id INT PRIMARY KEY,
    source_id INT,
    title VARCHAR(255),
    byline INT,
    image_id INT,
    copy_id INT,
    summary_id INT,
    FOREIGN KEY (source_id) REFERENCES Source(id),
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (copy_id) REFERENCES Copy(id),
    FOREIGN KEY (summary_id) REFERENCES Copy(id)
);
