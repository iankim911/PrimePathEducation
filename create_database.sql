-- PrimePath Database Setup Script
-- Run this in PostgreSQL after installation

-- Create the database
CREATE DATABASE primepath_db;

-- Create the user
CREATE USER primepath_user WITH PASSWORD 'primepath_password';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE primepath_db TO primepath_user;

-- Grant schema permissions (for PostgreSQL 15+)
\c primepath_db
GRANT ALL ON SCHEMA public TO primepath_user;