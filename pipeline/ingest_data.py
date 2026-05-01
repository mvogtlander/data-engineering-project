#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine


def run():
    year = 2021
    month = 1

    pg_user = 'root'
    pg_password = 'root'
    pg_host = 'localhost'
    pg_port = '5432'
    pg_database = 'ny_taxi'

    chunksize = 100000

    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64"
    }

    parse_dates = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime"
    ]

    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    folder = f'yellow_tripdata_{year}-{month:02d}.csv.gz'
    url = prefix + folder

    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}')

    # Create table schema
    df = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        nrows=0
    )
    df.to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

    # Ingest data in chunks
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize
    )

    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')


if __name__ == '__main__':
    run()