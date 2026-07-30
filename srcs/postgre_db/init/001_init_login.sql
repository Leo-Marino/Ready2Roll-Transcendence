CREATE TYPE usertype AS ENUM ('standard', 'business');

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(50) UNIQUE NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
	password TEXT NOT NULL,
	type_of_user usertype DEFAULT 'standard',
	created_time_stamp TIMESTAMP DEFAULT now(),
	avatar_url VARCHAR(512),
	instagram_handle VARCHAR(55) UNIQUE,
	phone_number VARCHAR(20) UNIQUE,
	legal_name VARCHAR(255),
	first_name VARCHAR(100),
	last_name VARCHAR (100),
	date_of_birth DATE,
	bio TEXT,
	bs_website VARCHAR(512),
	is_verified BOOLEAN DEFAULT FALSE,
	CONSTRAINT check_business_legal_name CHECK (
			type_of_user = 'standard' OR (type_of_user = 'business' AND legal_name IS NOT NULL)
		)
	);


