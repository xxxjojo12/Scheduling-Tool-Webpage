-- /exam/flask_app/create_tables/availability.sql
CREATE TABLE IF NOT EXISTS availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event_id INT,
    day DATE,
    time_slot VARCHAR(10),
    status ENUM('available', 'maybe', 'unavailable'),
    UNIQUE (user_id, event_id, day, time_slot),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
