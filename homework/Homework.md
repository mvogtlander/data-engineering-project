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