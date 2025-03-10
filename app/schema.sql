PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS rules;
DROP TABLE IF EXISTS students;

CREATE TABLE
    courses (
        guid TEXT PRIMARY KEY DEFAULT (lower(hex (randomblob (16)))), -- Generates a GUID
        course_code TEXT UNIQUE NOT NULL, -- User-defined unique course code
        course_name TEXT NOT NULL, -- Course name
        passing_grade REAL NOT NULL DEFAULT 3.0 -- Passing grade
    );

CREATE TABLE
    grades (
        guid TEXT PRIMARY KEY DEFAULT (lower(hex (randomblob (16)))), -- Generates a GUID
        student_guid TEXT NOT NULL, -- Reference to student
        course_guid TEXT NOT NULL, -- Reference to course
        score INTEGER NOT NULL, -- Raw percentage score (0-100)
        grade REAL NOT NULL, -- PH 5-point grade
        FOREIGN KEY (student_guid) REFERENCES students (guid) ON DELETE CASCADE,
        FOREIGN KEY (course_guid) REFERENCES courses (guid) ON DELETE CASCADE,
        UNIQUE(student_guid, course_guid)
    );

CREATE TABLE
    rules (
        guid INTEGER PRIMARY KEY DEFAULT (lower(hex (randomblob (16)))), -- Generates a GUID
        min_score INTEGER NOT NULL, -- Minimum score for the rule
        max_score INTEGER NOT NULL, -- Maximum score for the rule
        grade REAL NOT NULL -- PH 5-point grade equivalent
    );

INSERT INTO rules (min_score, max_score, grade) VALUES (99, 100, 1.0);
INSERT INTO rules (min_score, max_score, grade) VALUES (96, 98, 1.25);
INSERT INTO rules (min_score, max_score, grade) VALUES (93, 95, 1.5);
INSERT INTO rules (min_score, max_score, grade) VALUES (90, 92, 1.75);
INSERT INTO rules (min_score, max_score, grade) VALUES (87, 89, 2.0);
INSERT INTO rules (min_score, max_score, grade) VALUES (84, 86, 2.25);
INSERT INTO rules (min_score, max_score, grade) VALUES (81, 83, 2.5);
INSERT INTO rules (min_score, max_score, grade) VALUES (78, 80, 2.75);
INSERT INTO rules (min_score, max_score, grade) VALUES (75, 77, 3.0);
INSERT INTO rules (min_score, max_score, grade) VALUES (70, 74, 4.0);
INSERT INTO rules (min_score, max_score, grade) VALUES (0, 69, 5.0);

CREATE TABLE
    students (
        guid TEXT PRIMARY KEY DEFAULT (lower(hex (randomblob (16)))), -- Generates a GUID
        student_number TEXT UNIQUE NOT NULL, -- User-defined unique student number
        email TEXT UNIQUE NOT NULL, -- Unique email
        password TEXT NOT NULL -- Hashed password for security
    );
