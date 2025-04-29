-- /exam/flask_app/create_tables/events.sql
CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    start_date DATE,
    end_date DATE,
    start_time TIME,
    end_time TIME,
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);
