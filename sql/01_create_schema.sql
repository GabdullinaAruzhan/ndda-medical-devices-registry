-- Схема базы данных реестра медицинских изделий НЦЭЛС
-- Нормализация: схема "звезда" с фактовой таблицей registrations
-- и четырьмя справочниками (dim_*)

CREATE DATABASE IF NOT EXISTS ndda_registry
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ndda_registry;

-- Справочник стран производителей
CREATE TABLE dim_country (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

-- Справочник производителей
CREATE TABLE dim_producer (
    producer_id INT AUTO_INCREMENT PRIMARY KEY,
    producer_name_ru VARCHAR(500) NOT NULL,
    producer_name_eng VARCHAR(500),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id)
);

-- Справочник классов риска (1 / 2а / 2б / 3 по правилам ЕАЭС)
CREATE TABLE dim_risk_class (
    risk_class_id INT AUTO_INCREMENT PRIMARY KEY,
    risk_class_name VARCHAR(100) NOT NULL UNIQUE
);

-- Справочник номенклатурных терминов (NMIRK)
CREATE TABLE dim_nmirk_term (
    nmirk_code INT PRIMARY KEY,
    term_name VARCHAR(500),
    term_definition TEXT
);

-- Основная таблица регистраций медицинских изделий
CREATE TABLE registrations (
    id INT PRIMARY KEY,
    reg_number VARCHAR(100),
    reg_type_name VARCHAR(50),
    reg_action_name VARCHAR(50),
    reg_date DATE,
    expire_date DATE,
    unlimited_sign BOOLEAN,
    reg_term INT,
    storage_term FLOAT,
    storage_measure_name VARCHAR(50),
    trade_name VARCHAR(1000),
    purpose TEXT,
    use_area TEXT,
    risk_class_id INT,
    producer_id INT,
    nmirk_code INT,
    sterility_sign BOOLEAN,
    mt_sign BOOLEAN,
    invitro_sign BOOLEAN,
    gmp_sign BOOLEAN,
    patent_sign BOOLEAN,
    trademark_sign BOOLEAN,
    measurement_sign BOOLEAN,
    comments TEXT,

    FOREIGN KEY (risk_class_id) REFERENCES dim_risk_class(risk_class_id),
    FOREIGN KEY (producer_id) REFERENCES dim_producer(producer_id),
    FOREIGN KEY (nmirk_code) REFERENCES dim_nmirk_term(nmirk_code)
);
