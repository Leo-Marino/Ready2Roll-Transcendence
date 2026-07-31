
CREATE TABLE direct_messages (
	id SERIAL PRIMARY KEY,
	sender_id INTEGER NOT NULL,
	reciever_id INTEGER NOT NULL,
	event_id INTEGER,
	message_type content_type DEFAULT 'text',
	content TEXT NOT NULL,
	is_read BOOLEAN DEFAULT FALSE,
	created_at TIMESTAMP DEFAULT now(),
	CONSTRAINT fk_sender
		FOREIGN KEY (sender_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_reciever
		FOREIGN KEY (reciever_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_event
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE
	);
