CREATE TYPE type_notification AS ENUM ('like', 'comment', 'subscription', 'registration', 'system')

CREATE TABLE notifications (
	id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	sender_id INTEGER,
	event_id INTEGER,
	system_not BOOLEAN DEFAULT FALSE,
	notification_txt TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT now(),
	is_read BOOLEAN DEFAULT FALSE
	);
