#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import click
from tqdm.auto import tqdm
from sqlalchemy import create_engine


@click.command()
@click.option('--year', default=2021, type=int, help='Year of taxi data')
@click.option('--month', default=1, type=int, help='Month of taxi data')
@click.option('--pg-user', default='root', help='PostgreSQL username')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default='5432', help='PostgreSQL port')
@click.option('--pg-database', default='ny_taxi', help='PostgreSQL database name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for data ingestion')
def run(year, month, pg_user, pg_password, pg_host, pg_port, pg_database, chunksize):
    target_table = 'yellow_taxi_data{year}_{month:02d}'.format(year=year, month=month)

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
    df.to_sql(name=target_table, con=engine, if_exists='replace')

    # Ingest data in chunks
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize
    )

    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(name=target_table, con=engine, if_exists='append')

if __name__ == '__main__':
    run()