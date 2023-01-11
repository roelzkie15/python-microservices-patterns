CREATE USER booking_projector_user WITH PASSWORD 'postgres';
GRANT CONNECT ON DATABASE postgres TO booking_projector_user;
GRANT USAGE ON SCHEMA public TO booking_projector_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO booking_projector_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO booking_projector_user;
