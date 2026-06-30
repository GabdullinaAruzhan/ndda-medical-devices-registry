

import pandas as pd
from sqlalchemy import create_engine

# ЗАМЕНИ user, password на свои данные от MySQL Workbench
DB_USER = "root"
DB_PASSWORD = "ТВОЙ_ПАРОЛЬ"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ndda_registry"

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DB_URL)

# 1. Загружаем подготовленный датасет
df = pd.read_csv("ndda_full.csv", encoding="utf-8-sig")
print("Загружено строк:", len(df))

# 2. Готовим dim_country: уникальные страны
countries = df[['countryNameRu']].drop_duplicates().dropna()
countries.columns = ['country_name']
countries.to_sql('dim_country', engine, if_exists='append', index=False)
print("Залито стран:", len(countries))

# 3. Подтягиваем сгенерированные country_id обратно, чтобы привязать к производителям
country_map = pd.read_sql("SELECT country_id, country_name FROM dim_country", engine)

# 4. Готовим dim_producer: уникальные производители + их страна
producers = df[['producerNameRu', 'producerNameEng', 'countryNameRu']].drop_duplicates(subset=['producerNameRu'])
producers = producers.merge(country_map, left_on='countryNameRu', right_on='country_name', how='left')
producers = producers[['producerNameRu', 'producerNameEng', 'country_id']]
producers.columns = ['producer_name_ru', 'producer_name_eng', 'country_id']
producers.to_sql('dim_producer', engine, if_exists='append', index=False)
print("Залито производителей:", len(producers))

producer_map = pd.read_sql("SELECT producer_id, producer_name_ru FROM dim_producer", engine)

# 5. Готовим dim_risk_class: 4 уникальных класса риска
risk_classes = df[['degreeRiskName']].drop_duplicates().dropna()
risk_classes.columns = ['risk_class_name']
risk_classes.to_sql('dim_risk_class', engine, if_exists='append', index=False)
print("Залито классов риска:", len(risk_classes))

risk_map = pd.read_sql("SELECT risk_class_id, risk_class_name FROM dim_risk_class", engine)

# 6. Готовим dim_nmirk_term: уникальные коды NMIRK
nmirk = df[['nmirkCode', 'termName_rus', 'termDefinition']].drop_duplicates(subset=['nmirkCode']).dropna(subset=['nmirkCode'])
nmirk.columns = ['nmirk_code', 'term_name', 'term_definition']
nmirk['nmirk_code'] = nmirk['nmirk_code'].astype(int)
nmirk.to_sql('dim_nmirk_term', engine, if_exists='append', index=False)
print("Залито NMIRK-терминов:", len(nmirk))

# 7. Собираем основную таблицу registrations, подставляя ID вместо текста
main = df.merge(country_map, left_on='countryNameRu', right_on='country_name', how='left')
main = main.merge(producer_map, left_on='producerNameRu', right_on='producer_name_ru', how='left')
main = main.merge(risk_map, left_on='degreeRiskName', right_on='risk_class_name', how='left')

main_final = main[[
    'id', 'regNumber', 'regTypesName', 'regActionName', 'regDate', 'expireDate',
    'unlimitedSign', 'regTerm', 'storageTerm', 'storageMeasureName', 'tradeName',
    'purpose', 'useArea', 'risk_class_id', 'producer_id', 'nmirkCode',
    'sterilitySign', 'mtSign', 'invitroSign', 'gmpSign', 'patentSign',
    'trademarkSign', 'measurementSign', 'comments'
]].copy()

main_final.columns = [
    'id', 'reg_number', 'reg_type_name', 'reg_action_name', 'reg_date', 'expire_date',
    'unlimited_sign', 'reg_term', 'storage_term', 'storage_measure_name', 'trade_name',
    'purpose', 'use_area', 'risk_class_id', 'producer_id', 'nmirk_code',
    'sterility_sign', 'mt_sign', 'invitro_sign', 'gmp_sign', 'patent_sign',
    'trademark_sign', 'measurement_sign', 'comments'
]

# trade_name на всякий случай обрежем до 1000 символов под лимит колонки
main_final['trade_name'] = main_final['trade_name'].str.slice(0, 1000)

main_final.to_sql('registrations', engine, if_exists='append', index=False)
print("Залито записей в registrations:", len(main_final))

print("\nГотово! Все таблицы заполнены.")
