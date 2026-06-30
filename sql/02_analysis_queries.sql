-- Аналитические запросы по реестру медицинских изделий НЦЭЛС
-- Используются JOIN, оконные функции (RANK), агрегации с CASE WHEN

-- 1. Распределение изделий по классам риска
SELECT
    r.risk_class_name,
    COUNT(*) AS total
FROM registrations reg
JOIN dim_risk_class r ON reg.risk_class_id = r.risk_class_id
GROUP BY r.risk_class_name
ORDER BY total DESC;


-- 2. Топ-10 производителей по количеству изделий, с разбивкой
--    по доле изделий высокого класса риска
SELECT
    p.producer_name_ru,
    c.country_name,
    COUNT(*) AS total_devices,
    SUM(CASE WHEN rc.risk_class_name LIKE 'Класс 3%' THEN 1 ELSE 0 END) AS high_risk_count
FROM registrations r
JOIN dim_producer p ON r.producer_id = p.producer_id
JOIN dim_country c ON p.country_id = c.country_id
JOIN dim_risk_class rc ON r.risk_class_id = rc.risk_class_id
GROUP BY p.producer_id, p.producer_name_ru, c.country_name
ORDER BY total_devices DESC
LIMIT 10;


-- 3. Топ-3 страны внутри каждого класса риска (оконная функция RANK)
SELECT *
FROM (
    SELECT
        rc.risk_class_name,
        c.country_name,
        COUNT(*) AS device_count,
        RANK() OVER (PARTITION BY rc.risk_class_name ORDER BY COUNT(*) DESC) AS country_rank
    FROM registrations r
    JOIN dim_producer p ON r.producer_id = p.producer_id
    JOIN dim_country c ON p.country_id = c.country_id
    JOIN dim_risk_class rc ON r.risk_class_id = rc.risk_class_id
    GROUP BY rc.risk_class_name, c.country_name
) ranked
WHERE country_rank <= 3
ORDER BY risk_class_name, country_rank;


-- 4. Динамика регистраций по годам: новые регистрации vs перерегистрации
SELECT
    YEAR(reg_date) AS year,
    COUNT(*) AS total_registrations,
    SUM(CASE WHEN reg_action_name = 'Регистрация' THEN 1 ELSE 0 END) AS new_registrations,
    SUM(CASE WHEN reg_action_name = 'Перерегистрация' THEN 1 ELSE 0 END) AS re_registrations
FROM registrations
GROUP BY YEAR(reg_date)
ORDER BY year;


-- 5. Топ-10 номенклатурных терминов NMIRK по количеству регистраций
SELECT
    n.term_name,
    COUNT(*) AS total,
    rc.risk_class_name
FROM registrations r
JOIN dim_nmirk_term n ON r.nmirk_code = n.nmirk_code
JOIN dim_risk_class rc ON r.risk_class_id = rc.risk_class_id
GROUP BY n.term_name, rc.risk_class_name
ORDER BY total DESC
LIMIT 10;


-- 6. Доля стерильных и ИВД-изделий внутри каждого класса риска
SELECT
    rc.risk_class_name,
    COUNT(*) AS total,
    ROUND(SUM(CASE WHEN r.sterility_sign = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS sterile_pct,
    ROUND(SUM(CASE WHEN r.invitro_sign = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS ivd_pct
FROM registrations r
JOIN dim_risk_class rc ON r.risk_class_id = rc.risk_class_id
GROUP BY rc.risk_class_name
ORDER BY rc.risk_class_name;
