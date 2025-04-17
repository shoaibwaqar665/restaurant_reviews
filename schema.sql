CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE trip_business_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id VARCHAR UNIQUE NOT NULL,
    name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    postal_code TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    schedule JSONB,
    thumbnail TEXT,
    review_rating DECIMAL(2,1),
    review_count INT,
    dining_options TEXT[],
    cuisines TEXT[],
    meal_types TEXT[],
    diets TEXT[],
    menu_url TEXT,
    has_menu_provider BOOLEAN DEFAULT FALSE
);

CREATE TABLE trip_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id VARCHAR UNIQUE NOT NULL,
    location_id VARCHAR REFERENCES trip_business_details(location_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    username TEXT,
    title TEXT,
    text TEXT NOT NULL,
    translated_title TEXT,
    translated_text TEXT,
    is_translated BOOLEAN DEFAULT FALSE,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    published_date DATE,
    language TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trip_review_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id VARCHAR REFERENCES trip_reviews(review_id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL
);
