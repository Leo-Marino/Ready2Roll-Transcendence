CREATE TYPE content_type AS ENUM ('text', 'image', 'video', 'gif');

CREATE TABLE subscriptions (
	follower_id INTEGER NOT NULL,
	followed_id INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT now(),
	PRIMARY KEY (follower_id, followed_id),
	CONSTRAINT fk_follower
		FOREIGN KEY (follower_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_followed
		FOREIGN KEY (followed_id)
		REFERENCES users(id)
		ON DELETE CASCADE
	);

CREATE TABLE likes (
	user_id INTEGER NOT NULL,
	event_id INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT now(),
	PRIMARY KEY (user_id, event_id),
	CONSTRAINT fk_users
		FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_event
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE
	);

CREATE TABLE comments (
	id SERIAL PRIMARY KEY,
	content TEXT NOT NULL,
	type_content content_type DEFAULT 'text',
	parent_comment_id INTEGER,
	user_id INTEGER NOT NULL,
	event_id INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT now(),
	CONSTRAINT fk_users
		FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_event
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_comment_reply
		FOREIGN KEY (parent_comment_id)
		REFERENCES comments(id)
		ON DELETE CASCADE
	);

CREATE TABLE registered_events (
	user_id INTEGER NOT NULL,
	event_id INTEGER NOT NULL,
	PRIMARY KEY (user_id, event_id),
	CONSTRAINT fk_user
		FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_events
		FOREIGN KEY (event_id)
		REFERENCES events(id)
		ON DELETE CASCADE
	);

CREATE TABLE user_tags (
	user_id INTEGER NOT NULL,
	tag_id INTEGER NOT NULL,
	PRIMARY KEY(user_id, tag_id),
	CONSTRAINT fk_user
		FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	CONSTRAINT fk_tags
		FOREIGN KEY (tag_id)
		REFERENCES tags(id)
		ON DELETE CASCADE
	);
