CREATE TYPE mediatype AS ENUM ('image', 'video');

CREATE TABLE events (
	id SERIAL PRIMARY KEY,
	organizer_id INTEGER NOT NULL,
	title VARCHAR(255) NOT NULL,
	description TEXT NOT NULL,
	location TEXT,
	event_date TIMESTAMPTZ NOT NULL,
	max_capacity INTEGER,
	ticket_price NUMERIC,
	end_time TIMESTAMP,
	CONSTRAINT fk_user
		FOREIGN KEY(organizer_id)
		REFERENCES users(id)
		ON DELETE CASCADE
	);

CREATE TABLE tags (
	id SERIAL PRIMARY KEY,
	tag_name VARCHAR(55) UNIQUE NOT NULL
	);

CREATE TABLE event_tags (
	event_id INTEGER NOT NULL,
	tag_id INTEGER NOT NULL,
	PRIMARY KEY (event_id, tag_id),
	CONSTRAINT fk_events
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_tags
		FOREIGN KEY (tag_id)
		REFERENCES tags(id)
		ON DELETE CASCADE
	);

CREATE TABLE media (
	id SERIAL PRIMARY KEY,
	event_id INTEGER NOT NULL,
	media_url VARCHAR(521) NOT NULL,
	media_type mediatype DEFAULT 'image',
	created_at TIMESTAMP DEFAULT now(),
	CONSTRAINT fk_events
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE
	);

