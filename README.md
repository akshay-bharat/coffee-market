## Project Reflections & Design Choices

### 1. Why did you choose this database schema layout?
I chose a flattened, highly aggregated analytical schema loaded directly into a single target table (`raw_coffee_market_data`). Since the primary objective of this project is to feed a Streamlit data dashboard and calculate Consumption Per Capita (CPC), keeping the data in a wide format eliminates the need for complex, heavy SQL joins at runtime. This maximizes dashboard performance and speeds up query response times.

### 2. How did you handle data cleaning and matching?
Country nomenclature varied heavily across the raw coffee, population, and ISO code datasets (e.g., "Congo (Brazzaville)" vs "Congo"). 
* I built a robust cleaning pipeline using Pandas **method chaining** (`.assign()`) and lambda functions to enforce lowercase and strip whitespace across all joining keys.
* I mapped specific text variations using a standardisation dictionary (`fix`).
* For regional aggregations like the "European Union" and special cases like "Kosovo", I dynamically handled missing keys using `np.where()` and custom assignment logic to backfill structural gaps with unique regional identifiers (`EUU`, `XKX`).

### 3. If you had 10x more data, how would you change your architecture?
If the dataset scaled by 10x, a local Pandas pipeline would hit memory thresholds and slow down. I would evolve the architecture by:
* Moving the compute from Pandas to **PySpark** or **AWS EM**R to handle data processing concurrently across clusters.
* Migrating the raw extraction phase to an **S3 Data Lake**, partition-loading the files by market year.
* Utilizing a cloud data warehouse like **Snowflake** or **AWS Redshift** instead of a standard transactional PostgreSQL database to optimize heavy analytical aggregations.

### 4. What would you do next if you had more time?
* **Automate the Orchestration:** Wrap the pipeline in an **Apache Airflow** DAG to schedule nightly or weekly data extraction automatically.
* **Data Quality Checks:** Implement a library like **Great Expectations** to validate that critical data types aren't null, population numbers are positive, and ISO codes strictly contain 3 letters before writing to production.
* **CI/CD Deployment:** Set up a GitHub Action to run automated testing scripts every time changes are pushed to the repository.
