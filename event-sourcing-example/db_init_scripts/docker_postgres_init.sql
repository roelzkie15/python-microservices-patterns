CREATE USER booking_read_user WITH PASSWORD 'postgres';
GRANT CONNECT ON DATABASE postgres TO booking_read_user;
GRANT USAGE ON SCHEMA public TO booking_read_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO booking_read_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO booking_read_user;
