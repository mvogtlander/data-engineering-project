import pandas as pd
import os
import glob
import sys
from sqlalchemy import create_engine, text

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'nyc_taxi_data'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root')
}

# Data path from environment
DATA_PATH = os.getenv('DATA_PATH', '/data')

def download_taxi_zones(data_path):
    import urllib.request
    
    zone_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
    zone_file = os.path.join(data_path, "taxi_zone_lookup.csv")
    
    try:
        urllib.request.urlretrieve(zone_url, zone_file)
        return zone_file
    except Exception as e:
        print(f"Failed to download: {e}")
        return None

def load_taxi_zones(engine, data_path):
    #create path to taxi zones file
    zone_file = os.path.join(data_path, "taxi_zone_lookup.csv")
    
    # Download if not exists
    if not os.path.exists(zone_file):
        zone_file = download_taxi_zones(data_path)
    
    if zone_file and os.path.exists(zone_file):
        zones_df = pd.read_csv(zone_file)
        
        # Write to PostgreSQL and overwrite if exists
        zones_df.to_sql('taxi_zones', engine, if_exists='replace', index=False)
        return True
    else:
        print("Taxi zone file not found")
        return False

def create_db_connection():
    """Create database connection"""
    url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(url)

def load_and_save_green_taxi_data(engine, data_path):
    """Load green taxi parquet files and write directly to PostgreSQL"""
    print(f"Looking for data in: {data_path}")
    
    # Check if data path exists
    if not os.path.exists(data_path):
        print(f" Data path does not exist: {data_path}")
        return False
    
    # Find all .parquet files from 2025
    parquet_files = glob.glob(os.path.join(data_path, "green_tripdata_2025-*.parquet"))
    
    if not parquet_files:
        print(f"No parquet files found in {data_path}")
        return False
    
    print(f"\nFound {len(parquet_files)} parquet files:")
    for f in sorted(parquet_files):
        file_size = os.path.getsize(f) / (1024**2)
        print(f"  - {os.path.basename(f)} ({file_size:.1f} MB)")
    
    # Process each file and write to database incrementally
    first_file = True
    
    for file in sorted(parquet_files):
        print(f"\nProcessing {os.path.basename(file)}...")
        df = pd.read_parquet(file)
        print(f"  Rows: {len(df):,}")
        
        # Convert data types
        df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
        df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
        df['store_and_fwd_flag'] = df['store_and_fwd_flag'].astype(str).map({'Y': True, 'N': False})
        
        # Convert integer columns
        int_columns = ['VendorID', 'RatecodeID', 'PULocationID', 'DOLocationID', 
                       'passenger_count', 'payment_type', 'trip_type']
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        
        # Write to PostgreSQL
        df.to_sql(
            name='green_tripdata_2025',
            con=engine,
            if_exists='append' if not first_file else 'replace',
            index=False,
            chunksize=10000,
            method='multi'
        )
        
        print(f"Written to database")
        first_file = False
    
    return True

def verify_data(engine):
    
    # Check row count
    result = pd.read_sql("SELECT COUNT(*) as count FROM green_tripdata_2025", engine)
    row_count = result.iloc[0, 0]
    print(f"Total rows in green_tripdata_2025: {row_count:,}")
    
    # Check taxi zones
    result = pd.read_sql("SELECT COUNT(*) as count FROM taxi_zones", engine)
    zone_count = result.iloc[0, 0]
    print(f"Total rows in taxi_zones: {zone_count:,}")
    
    return row_count > 0

def main():
    """Main ingestion pipeline"""
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Data path: {DATA_PATH}")
    
    # Create database connection
    print("\n[1/4] Creating database connection...")
    engine = create_db_connection()
    
    try:
        with engine.connect() as conn:
            print("Connected to PostgreSQL")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
    
    # Load green taxi data
    print("\n[2/4] Loading green taxi data...")
    success = load_and_save_green_taxi_data(engine, DATA_PATH)
    
    if not success:
        print("Failed to load green taxi data")
        sys.exit(1)
    
    # Load taxi zones
    print("\n[3/4] Loading taxi zones...")
    load_taxi_zones(engine, DATA_PATH)
    
    # Verify data
    print("\n[4/4] Verifying data...")
    verify_data(engine)

if __name__ == "__main__":
    main()