CREATE TYPE type_notification AS ENUM ('like', 'comment', 'subscription', 'registration', 'system');

CREATE TABLE notifications (
	id SERIAL PRIMARY KEY,
	recipient_id INTEGER NOT NULL,
	sender_id INTEGER,
	event_id INTEGER,
	notification_type type_notification NOT NULL,
	notification_txt TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT now(),
	is_read BOOLEAN DEFAULT FALSE,
	CONSTRAINT fk_recipient
		FOREIGN KEY (recipient_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_sender
		FOREIGN KEY (sender_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_events
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE
	);
