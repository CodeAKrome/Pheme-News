CREATE TABLE Source (
    id INT PRIMARY KEY,
    name STRING,
    type STRING,
    country STRING,
    affiliation STRING
);

CREATE TABLE Story (
    id INT PRIMARY KEY,
    source_id INT,
    title STRING,
    byline INT,
    image_id INT,
    copy_id INT,
    summary_id INT,
    FOREIGN KEY (source_id) REFERENCES Source(id),
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (copy_id) REFERENCES Copy(id),
    FOREIGN KEY (summary_id) REFERENCES Copy(id)
);

CREATE TABLE Object (
    id INT PRIMARY KEY,
    text STRING
);

CREATE TABLE Image (
    id INT PRIMARY KEY,
    copy_id INT,
    file STRING,
    objects INT,
    FOREIGN KEY (copy_id) REFERENCES Copy(id),
    FOREIGN KEY (objects) REFERENCES ObjectMap(id)
);

CREATE TABLE ObjectMap (
    id INT PRIMARY KEY,
    object_id INT,
    FOREIGN KEY (object_id) REFERENCES Object(id)
);

CREATE TABLE Copy (
    id INT PRIMARY KEY,
    story_id INT,
    image_id INT,
    text STRING,
    entitymap_id INT,
    sentiment BOOLEAN,
    objectivity FLOAT,
    summary BOOLEAN,
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (entitymap_id) REFERENCES EntityMap(id)
);

CREATE TABLE EntityMap (
    id INT PRIMARY KEY,
    entity_id INT,
    sentiment BOOLEAN,
    objectivity FLOAT,
    FOREIGN KEY (entity_id) REFERENCES Entity(id)
);

CREATE TABLE Entity (
    id INT PRIMARY KEY,
    kind INT,
    text STRING,
    FOREIGN KEY (kind) REFERENCES Kind(id)
);

CREATE TABLE Kind (
    id INT PRIMARY KEY,
    text STRING
);