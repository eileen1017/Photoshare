CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    hometown VARCHAR(255),
    gender VARCHAR(6),
    album_num int4,
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friends (
  #count int4 AUTO_INCREMENT,
  user_id int4,
  user_id2 int4,
  PRIMARY KEY(user_id,user_id2),
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(user_id2) REFERENCES Users(user_id) ON DELETE CASCADE
  #CONSTRAINT count_pk PRIMARY KEY (count)
);

CREATE TABLE Albums (
  album_id int4 AUTO_INCREMENT,
  album_name VARCHAR(255),
  date_of_creation DATE,
  CONSTRAINT album_pk PRIMARY KEY (album_id),
  user_id int4,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Pictures
(
  picture_id int4 AUTO_INCREMENT,
  user_id int4,
  album_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  FOREIGN KEY(album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  comment_id int4,
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Tags (
  word VARCHAR(255),
  PRIMARY KEY (word)
);

CREATE TABLE  Comments (
  comment_id int4 AUTO_INCREMENT,
  text TEXT,
  user_id int4,
  date DATE,
  picture_id int4,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE,
  CONSTRAINT comment_pk PRIMARY KEY (comment_id)
);

CREATE TABLE Likes (
  picture_id int4,
  user_id int4,
  date DATE,
  PRIMARY KEY(user_id, picture_id),
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Associate (
  picture_id int4,
  word VARCHAR(255),
  PRIMARY KEY(picture_id, word),
  FOREIGN KEY(word) REFERENCES Tags(word) ON DELETE CASCADE,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('1@bu.edu', 'test','1','1','1993/10/17','shaanxi','Female');
INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('2@bu.edu', 'test','2','2','1993/10/17','shaanxi','Female');

INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('3@bu.edu', 'test','3','3','1993/10/17','shaanxi','Female');
INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('4@bu.edu', 'test','4','4','1993/10/17','shaanxi','Female');

INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('5@bu.edu', 'test','5','5','1993/10/17','shaanxi','Female');
INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('6@bu.edu', 'test','6','6','1993/10/17','shaanxi','Female');
INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('7@bu.edu', 'test','7','7','1993/10/17','shaanxi','Female');
