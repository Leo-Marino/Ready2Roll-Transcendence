CREATE TYPE usertype AS ENUM ('standard', 'business');

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(50) UNIQUE NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
	password TEXT NOT NULL,
	type_of_user usertype DEFAULT 'standard',
	created_time_stamp TIMESTAMP DEFAULT now()
);

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
	event_id INTEGER,
	tag_id INTEGER,
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
