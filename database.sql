CREATE DATABASE attendance_db;

USE attendance_db;

CREATE TABLE batches (
    batch_id INT PRIMARY KEY,                        
    batch_name VARCHAR(30) NOT NULL
);

INSERT INTO batches VALUES
(1, 'BCA'),
(2, 'Civil'),
(3, 'IT'),
(4, 'AIML');

CREATE TABLE students (
    student_id INT not null PRIMARY KEY,                                    # har student ki id unique or not null
    student_name VARCHAR(50) NOT NULL,
    batch_id INT,
    branch VARCHAR(30),
    phone VARCHAR(15) not null,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
    check (length(phone) = 10)
);
ALTER TABLE students
ADD marks INT;
desc students;

INSERT INTO students
(student_id, student_name, batch_id, branch, phone)
VALUES
(101, 'Anjali', 1, 'BCA', '9876543210'),
(102, 'Priya', 2, 'Civil', '9876543211'),
(103, 'Rahul', 3, 'IT', '9876543212'),
(104, 'Neha', 4, 'AIML', '9876543213'),
(105, 'Aman', 1, 'BCA', '9876543214'),
(106, 'Pooja', 2, 'Civil', '9876543215'),
(107, 'Rohit', 3, 'IT', '9876543216'),
(108, 'Sneha', 4, 'AIML', '9876543217'),
(109, 'Arjun', 1, 'BCA', '9876543218'),
(110, 'Simran', 2, 'Civil', '9876543219'),
(111, 'Karan', 3, 'IT', '9876543220'),
(112, 'Riya', 4, 'AIML', '9876543221'),
(113, 'Vikas', 1, 'BCA', '9876543222');
select * from students;



CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent' , 'leave') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE (student_id, attendance_date)            # unique  -> duplicate attendance nhi lag sakti agar 1 baar lag gyi h toh same date par agale din lag sakti h
);
INSERT INTO attendance
(student_id, attendance_date, status)
VALUES
(101, '2026-10-29', 'Present'),
(102, '2026-10-29', 'Present'),
(103, '2026-10-29', 'Absent'),
(104, '2026-10-29', 'Present'),
(105, '2026-10-29', 'leave'),
(106, '2026-10-29', 'Present'),
(107, '2026-10-29', 'Absent'),
(108, '2026-10-29', 'Present'),
(109, '2026-10-29', 'Present'),
(110, '2026-10-29', 'leave'),
(111, '2026-10-29', 'Absent'),
(112, '2026-10-29', 'Present'),
(113, '2026-10-29', 'Present');
