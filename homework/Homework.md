# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework.

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.


## Question 1. 
What's the version of `pip` in the image?
26.0.1

docker run --rm python:3.13 pip --version 

## Question 2.
What is the hostname and port that pgadmin should use to connect to the postgres database?
  ports:
      - '5433:5432'
Port 5433 is the localhost port and port = 5432 is the container port so the correct port = 5432. You can connect with the service via the service name OR container name

## Question 3.
For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

SELECT * FROM public.green_tripdata_2025 
where lpep_pickup_datetime >= '2025-11-01'
AND lpep_pickup_datetime < '2025-12-01' and trip_distance < 1

7757 rows

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

SELECT CAST(lpep_pickup_datetime AS DATE), MAX(trip_distance) as a FROM public.green_tripdata_2025 
GROUP BY lpep_pickup_datetime, trip_distance
having trip_distance < 100
order by a desc;

2025-09-26 which was on a Friday

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?
Flushing

SELECT MAX(total_amount) as total_amount_per_zone, a."Zone"
FROM green_tripdata_2025 as b
INNER JOIN taxi_zones as a
ON a."LocationID" = b."PULocationID"
GROUP BY total_amount, a."Zone", b."lpep_pickup_datetime"
HAVING CAST(b."lpep_pickup_datetime" AS DATE) = '2025-11-18'
order by total_amount_per_zone desc;


## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

JFK Airport

SELECT 
    MAX(b.tip_amount) as max_tip,
    a."Zone" as pickup_zone,
    c."Zone" as dropoff_zone
FROM green_tripdata_2025 as b
INNER JOIN taxi_zones as a
    ON a."LocationID" = b."PULocationID"
INNER JOIN taxi_zones as c
    ON c."LocationID" = b."DOLocationID"
WHERE a."Zone" = 'East Harlem North' 
    AND CAST(b."lpep_pickup_datetime" AS DATE) = '2025-11-11'
GROUP BY a."Zone", c."Zone"
ORDER BY MAX(b.tip_amount) DESC;

## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- teraform init, terraform plan -auto-apply, terraform rm

# Module 2 Homework: Workflow & Orchestration

### Quiz Questions

Complete the quiz shown below. It's a set of 6 multiple-choice questions to test your understanding of workflow orchestration, Kestra, and ETL pipelines.

1) Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?
In the execution go to metrics -> upload_to_gcs -> 134,481,400
- 134.5 MiB

2) What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?
- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv` 
- `green_tripdata_2020-04.csv`

3) How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?
In the yellow_tripdata dataset go to details and find the 'Number of rows' under Storage info. 
- 24,648,499

4) How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?
In the green_tripdata dataset go to details and find the 'Number of rows' under Storage info.
- 1,734,051

5) How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?
- 1,925,152

6) How would you configure the timezone to New York in a Schedule trigger?
In the yaml file check the documentation for triggers. Here you'll find what properties are available and one of them being timezone. The default here is set to Etc/UTC however we could set this to any second column in https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List according to the kestra 'Schedule' documentation .
- Add a `timezone` property and set this to `America/New_York` in the `Schedule` trigger configuration  

# Module 3 Homework: Data Warehousing & BigQuery

## Question 1. Counting records

What is count of records for the 2024 Yellow Taxi Data?
SELECT COUNT(*) 
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata`
- 20,332,093

## Question 2. Data read estimation

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
 
What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?

SELECT COUNT (DISTINCT PULocationID)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata`;

SELECT COUNT (DISTINCT PULocationID)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_materialized`;

- 0 MB for the External Table and 155.12 MB for the Materialized Table
This is because BigQuery checks the metadata of the parquet files in GCS and not actually reads in any data. When the Materialized Table is created it actually scans the data.

## Question 3. Understanding columnar storage

Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.

SELECT COUNT(*)
FROM (SELECT PULocationID, DOLocationId 
      FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_materialized`
      GROUP BY PULocationID, DOLocationID);

Why are the estimated number of Bytes different?
- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

## Question 4. Counting zero fare trips

How many records have a fare_amount of 0?
SELECT COUNT(*)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_materialized`
WHERE fare_amount = 0;
- 8,333

## Question 5. Partitioning and clustering

What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)

CREATE OR REPLACE TABLE `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS (SELECT * FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata`)
;
- Partition by tpep_dropoff_datetime and Cluster on VendorID


## Question 6. Partition benefits

Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)


Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? 

Choose the answer which most closely matches.
 
 # Q6: Materialized
SELECT DISTINCT (VendorID)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_materialized`
WHERE tpep_dropoff_datetime >= '2024-03-01' AND tpep_dropoff_datetime <= '2024-03-15';
# Q6: Partitioned and clustered
SELECT DISTINCT (VendorID)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_partitioned_clustered`
WHERE tpep_dropoff_datetime >= '2024-03-01' AND tpep_dropoff_datetime <= '2024-03-15';

- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table


## Question 7. External table storage

Where is the data stored in the External Table you created?

- GCP Bucket

## Question 8. Clustering best practices

It is best practice in Big Query to always cluster your data:
- False


## Question 9. Understanding table scans

No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?
The estimated amount of bytes being processed when running the query: 
SELECT COUNT(*)
FROM `de-zoomcamp-mv-499409.nytaxi.yellow_tripdata_materialized`
Is 0 bytes. This is happening because when the table was created there is metadata available on how many rows there are in the table. The SELECT COUNT(*) is a metadata operation on the table and therefor doesnt need to read in any data. When we for example add a where clause then this isn't a metadata operation and the query would require to read the table. 

# Module 4 Homework: Analytics Engineering with dbt

## Question 1. dbt Lineage and Execution

Given a dbt project with the following structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `dbt run --select int_trips_unioned`, what models will be built?

- `int_trips_unioned` only

### Question 2. dbt Tests

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data.

What happens when you run `dbt test --select fct_trips`?

- dbt will fail the test, returning a non-zero exit code

### Question 3. Counting Records in `fct_monthly_zone_revenue`

After running your dbt project, query the `fct_monthly_zone_revenue` model.

What is the count of records in the `fct_monthly_zone_revenue` model?
SELECT COUNT(*) FROM `de-zoomcamp-mv-499409.dbt_marc_vogtlander_taxi_rides_ny_homework_wk4.fct_monthly_zone_revenue`
- 12,184

### Question 4. Best Performing Zone for Green Taxis (2020)

Using the `fct_monthly_zone_revenue` table, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

SELECT pickup_zone, SUM(revenue_monthly_total_amount) as total_revenue FROM `de-zoomcamp-mv-499409.dbt_marc_vogtlander_taxi_rides_ny_homework_wk4.fct_monthly_zone_revenue`
where service_type = 'Green' and revenue_month >= '2020-01-01' and revenue_month < '2021-01-01'
group by pickup_zone order by total_revenue desc;

Which zone had the highest revenue?

- East Harlem North

### Question 5. Green Taxi Trip Counts (October 2019)

Using the `fct_monthly_zone_revenue` table, what is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

SELECT SUM(total_monthly_trips) FROM `de-zoomcamp-mv-499409.dbt_marc_vogtlander_taxi_rides_ny_homework_wk4.fct_monthly_zone_revenue`
where service_type = 'Green' and revenue_month >= '2019-10-01' and revenue_month <= '2019-10-31'; 
- 384,624

### Question 6. Build a Staging Model for FHV Data

Create a staging model for the **For-Hire Vehicle (FHV)** trip data for 2019.

1. Load the [FHV trip data for 2019](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv) into your data warehouse
2. Create a staging model `stg_fhv_tripdata` with these requirements:
   - Filter out records where `dispatching_base_num IS NULL`
   - Rename fields to match your project's naming conventions (e.g., `PUlocationID` → `pickup_location_id`)

What is the count of records in `stg_fhv_tripdata`?

SELECT COUNT (*) 
from {{ ref('stg_fhv_tripdata') }}
- 43,244,693