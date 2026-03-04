# locallib

A comprehensive local library containing analytics, database utilities, and file operations for emission rate calculations and data processing.

## Installation

Install in development mode:

```bash
pip install -e .
```

## Usage

### Analytics Classes

```python
from locallib.analytics import BinnedRER, CustomBinnedRER, BinnedDistribution

# Using BinnedRER (predefined bins and labels)
rer = BinnedRER()
experiments = [0.5, 1.2, 0.8, 2.1, 0.3]  # Example data
rer.set_experiments(experiments)
actual_dist = rer.get_actual_leak_distribution()
posterior_prob = rer.get_posterior_probability_matrix()
posterior_dist = rer.get_posterior_leak_distribution()

# Using CustomBinnedRER (custom bins and labels)
A = ['A1', 'A0', 'A-1', 'A-2']
B = ['B-2', 'B-1', 'B0', 'B1']
bin_floors = [1E-5, 0.1, 1, 10, 1E5]
custom_rer = CustomBinnedRER(A, B, bin_floors)
custom_rer.set_experiments(experiments)

# Using BinnedDistribution (for simple binning)
bin_labels = ['Low', 'Medium', 'High', 'Very High']
bin_floors = [0, 0.5, 1.0, 2.0, 10.0]
binned_dist = BinnedDistribution(experiments, bin_labels, bin_floors)
distribution = binned_dist.set_binned_distribution()
```

### Box File Operations

```python
from locallib.box import BoxFile, BoxFile_old

# Using BoxFile for Box.com operations
box_file = BoxFile(
    local_path="./data/my_file.csv",
    box_folder_id="12345"
)
box_file.upload()  # Upload to Box
box_file.download()  # Download from Box
```

### Database Operations

```python
from locallib.query import Query, get_emission_soruces, get_final_reports
from locallib.picarrodb import (
    PConnection, PDataFrame, EU1_Conn, EU2_Conn,
    DBTable, DBColumn, DBConstructor
)

# Using query module for database queries
query = Query("SELECT * FROM table")
query.set_table("my_table")

# Get emission sources data
emission_query = get_emission_soruces("#TempFinalReports")

# Get final reports for a customer
reports_query = get_final_reports("CustomerName", years=[2023, 2024])

# Using PicarroDB connections
# Use pre-configured connections
session = EU1_Conn.get_session()

# Or create custom connection
custom_conn = PConnection(
    host="your-host",
    user="username", 
    password="password",
    database="database_name"
)

# Using PDataFrame (enhanced pandas DataFrame)
df = PDataFrame(data)
df.set_connection(custom_conn)
df.set_query("SELECT * FROM table")

# Using database structure classes
# Create columns
id_column = DBColumn("id", "INTEGER")
name_column = DBColumn("name", "VARCHAR(255)")

# Create table with columns
users_table = DBTable("users", [id_column, name_column])

# Use constructor to manage multiple tables
db_constructor = DBConstructor()
db_constructor.add_table(users_table)
```

## Classes

### Analytics Module

#### BinnedRER
A class for calculating representative emission rates using predefined binned data and Bayesian analysis.

**Methods:**
- `set_experiments(experiments)`: Set experimental data and calculate actual leak distribution
- `set_actual_leak_distribution(actual_leak_distribution=None)`: Set or calculate the actual leak distribution
- `get_actual_leak_distribution()`: Get the actual leak distribution
- `get_posterior_probability_matrix()`: Calculate and return the posterior probability matrix
- `get_posterior_leak_distribution()`: Calculate and return the posterior leak distribution

#### CustomBinnedRER
A customizable class for representative emission rate calculations with user-defined bins and labels.

**Parameters:**
- `A`: List of bin labels for actual distribution
- `B`: List of bin labels for observed distribution  
- `bin_floors`: List of bin floor values

**Methods:** (Same as BinnedRER)

#### BinnedDistribution
A utility class for creating binned distributions from experimental data.

**Parameters:**
- `experiments`: List of experimental values
- `bin_labels`: List of labels for bins (default: ['A-1','A0','A1','A2'])
- `bin_floors`: List of bin boundaries (default: [1E-5,0.1,1,10,1E5])

**Methods:**
- `set_binned_distribution()`: Create and return binned distribution DataFrame

### Box Module

#### BoxFile
Modern class for handling Box.com file operations with improved error handling.

**Parameters:**
- `local_path`: Path to local file
- `box_folder_id`: Box folder ID (optional if box_file_id provided)
- `box_file_id`: Box file ID (optional, will be retrieved from folder if not provided)

**Methods:**
- `download()`: Download file from Box
- `upload()`: Upload file to Box (creates new or updates existing)
- `delete(site='local')`: Delete file ('local' or 'box')

#### BoxFile_old
Legacy class for Box.com file operations (maintained for backward compatibility).

### Query Module

#### Query
A class for managing database queries with parent-child relationships.

**Parameters:**
- `query`: SQL query string

**Methods:**
- `set_table(table)`: Set the table name for the query
- `set_parent(parent)`: Set parent query
- `set_child(child)`: Set child query  
- `get_parent()`: Get parent query
- `get_child()`: Get child query
- `execute(conn)`: Execute the query with given connection

#### Utility Functions

**get_emission_soruces(report_table)**
- Generates SQL query to retrieve emission source data
- Returns formatted SQL query string

**get_final_reports(customer_name, years=None)**
- Generates SQL query to get final reports for a customer
- `customer_name`: Name of the customer
- `years`: Optional list of years to filter by
- Returns formatted SQL query string

### PicarroDB Module

#### PConnection
Database connection manager for Picarro databases.

**Parameters:**
- `host`: Database host
- `user`: Database username
- `password`: Database password
- `database`: Database name

**Methods:**
- `get_session()`: Get database session

#### PDataFrame
Enhanced pandas DataFrame with database connection capabilities.

**Methods:**
- `set_connection(conn)`: Set database connection
- `set_query(query)`: Set SQL query
- `set_parent(parent)`: Set parent DataFrame
- `set_child(child)`: Set child DataFrame
- `get_parent()`: Get parent DataFrame

#### Pre-configured Connections

**EU1_Conn**
- Pre-configured connection to EU1 production database
- Uses environment variables: `EUDBUSER`, `EUDBPW`

**EU2_Conn** 
- Pre-configured connection to EU2 production database
- Uses environment variables: `EU2DBUSER`, `EU2DBPW`

#### Database Structure Classes

**DBTable**
Class for representing database tables with columns.

**Parameters:**
- `name`: Table name
- `columns`: List of DBColumn objects

**Methods:**
- `get_table_name()`: Get table name
- `add_column(column)`: Add a new column to the table

**DBColumn**
Class for representing database columns.

**Parameters:**
- `name`: Column name
- `type`: Column data type

**Methods:**
- `get_column_name()`: Get column name

**DBConstructor**
Class for managing multiple database tables and columns.

**Methods:**
- `add_table(table)`: Add a table to the constructor
- `add_column(column)`: Add a column to the constructor
- `get_tables()`: Get all tables

## Requirements

- pandas >= 1.0.0
- numpy >= 1.18.0