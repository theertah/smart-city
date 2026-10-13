CREATE DATABASE IF NOT EXISTS smart_city;
USE smart_city;

CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DOUBLE,
    longitude DOUBLE,
    zone VARCHAR(50) NOT NULL,
    population INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS traffic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    vehicle_count INT,
    average_speed FLOAT,
    congestion_level FLOAT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS environment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT,
    air_quality FLOAT,
    noise_level FLOAT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS waste (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    fill_percentage FLOAT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS energy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    consumption FLOAT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    category VARCHAR(50),
    department VARCHAR(100),
    description TEXT,
    severity INT,
    priority_score INT,
    status VARCHAR(20) DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    prediction_type VARCHAR(50),
    prediction FLOAT,
    confidence FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

INSERT INTO locations (name, latitude, longitude, zone, population) VALUES
    ('Hebbal', 13.0354, 77.5988, 'North Zone', 60000),
    ('Majestic', 12.9766, 77.5713, 'Central Zone', 90000),
    ('Whitefield', 12.9698, 77.7499, 'East Zone', 80000),
    ('Electronic City', 12.8452, 77.6602, 'South Zone', 70000),
    ('Jayanagar', 12.9299, 77.5824, 'South Zone', 50000),
    ('Koramangala', 12.9352, 77.6245, 'South East Zone', 65000),
    ('Indiranagar', 12.9719, 77.6412, 'East Zone', 55000),
    ('Malleshwaram', 13.0031, 77.5643, 'West Zone', 45000);
