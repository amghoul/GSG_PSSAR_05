# Data Quality Report

This document outlines the data quality analysis, missing value summaries, structural characteristics, and engineering decisions made for the `chess_games.csv` and `play_data.csv` datasets.

---

## 1. Executive Summary
An initial data quality audit was conducted on two core datasets: `chess_games.csv` (historical game logs) and `play_data.csv` (user account registry profiles). 

- **chess_games.csv**: A highly clean, large-scale dataset (`20,058` records) with no duplicate entries but with missing data.
- **play_data.csv**: A small registry dataset (`215` records) tracking user status. It presents multiple data quality challenges, including missing categorical markers, unpopulated country coordinates, and improper numeric casting for temporal values (`registered_year`).

---

## 2. Dataset Analysis: `chess_games.csv`

### 2.1 Structural Overview & Shape
* **Total Rows (Shape):** 20,058 rows
* **Total Columns (Shape):** 17 columns
* **Duplicate Rows:** 0 (No exact duplicates detected)

### 2.2 Missing Data Profile
The dataset contains a total of **20,058 records**. Missing values and their relative percentages are explicitly detailed below:

| Column Name | Data Type | Null Count | Null % | Data Quality Status / Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| `game_id` | int64 | 0 | 0.00% | Valid / Complete Unique Identifier |
| `rated` | bool | 0 | 0.00% | Valid / Complete |
| `turns` | int64 | 0 | 0.00% | Valid / Complete (Range: 1 to 349 turns) |
| `victory_status` | object | 0 | 0.00% | Valid / Complete |
| `winner` | object | 0 | 0.00% | Valid / Complete |
| `time_increment` | object | 0 | 0.00% | Valid / Complete |
| `white_id` | object | 0 | 0.00% | Valid / Complete |
| `white_rating` | int64 | 0 | 0.00% | Valid / Complete (Range: 784 to 2700) |
| `black_id` | object | 0 | 0.00% | Valid / Complete |
| `black_rating` | int64 | 0 | 0.00% | Valid / Complete (Range: 789 to 2723) |
| `moves` | object | 0 | 0.00% | Valid / Complete (PGN representation) |
| `opening_code` | object | 0 | 0.00% | Valid / Complete (ECO Standard Codes) |
| `opening_moves` | int64 | 0 | 0.00% | Valid / Complete |
| `opening_fullname` | object | 0 | 0.00% | Valid / Complete |
| `opening_shortname`| object | 0 | 0.00% | Valid / Complete |
| `opening_response` | object | 18,851 | **93.98%** | Missing structurally (Conditional on opening line) |
| `opening_variation`| object | 5,660 | **28.22%** | Missing structurally (Conditional on sub-variation) |

### 2.3 Quality Decisions & Rationale

#### Decision 1: Retain Null Values in `opening_response` and `opening_variation`
* **Action:** Keep the nulls exactly as they are. Do **not** drop rows, and do **not** impute using standard string replacements like "Unknown".
* **Why:** An *opening response* only exists if the second player makes a specific counter-move that creates a named sub-classification. Similarly, an *opening variation* only occurs if the line extends deeply enough to branch out. 

#### Decision 2: Retain Extreme Outliers in `turns`
* **Action:** Preserve the record with the maximum value of `349` turns.
* **Why:** Although the 75th percentile sits at `79` turns, a 349-turn game is a realistic statistical tail event in high-level or bullet/blitz chess formats where players shuffle pieces to force draws or run down clocks. Since it represents legitimate behavioral data, it must not be pruned.

---

## 3. Dataset Analysis: `play_data.csv`

### 3.1 Structural Overview & Shape
* **Total Rows (Shape):** 215 rows
* **Total Columns (Shape):** 9 columns
* **Duplicate Rows:** 0 (No exact duplicates detected)

### 3.2 Missing Data Profile
The dataset contains a total of **215 records**. Missing values and their relative percentages are explicitly detailed below:

| Column Name | Data Type | Null Count | Null % | Data Quality Status / Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| `username` | object | 0 | 0.00% | Valid / Complete Unique Key |
| `display_name` | object | 0 | 0.00% | Valid / Complete |
| `country` | object | 14 | **6.51%** | Missing Data (Optional profile field) |
| `registered_year` | float64 | 7 | **3.26%** | Missing Data / Erroneous Data Type |
| `rating_registry` | int64 | 0 | 0.00% | Valid / Complete (Range: 943 to 2621) |
| `total_games_registry`| int64 | 0 | 0.00% | Valid / Complete |
| `account_status` | object | 46 | **21.40%** | Missing Data (High-risk omission) |
| `email_verified` | bool | 0 | 0.00% | Valid / Complete |
| `join_platform` | object | 0 | 0.00% | Valid / Complete |

### 3.3 Quality Decisions & Rationale

#### Decision 1: Type-Cast `registered_year` from Float64 to Nullable Integer (`Int64`)
* **Action:** Impute the 7 missing values using the **Median** registration year (`2018`) or flag them with an indicator variable, then explicitly convert the column from `float64` to pandas' `Int64` (nullable integer).
* **Why:** Calendar years are discrete intervals. The raw data parsed it as a `float64` strictly because standard NumPy arrays force integer columns containing `NaN` values to become floats. Converting to a nullable integer keeps numerical accuracy intact without displaying deceptive floats (e.g., `2018.0`). 

#### Decision 2: Impute Missing `account_status` Values with an explicit label (`"Unspecified"`)
* **Action:** Map all 46 missing items to a new categorical string identifier, `"Unspecified"` or `"Active_Default"`.
* **Why:** Over 21% of users lack a status flag. Dropping these rows would destroy more than a fifth of our profile dataset. Since an unpopulated status field usually implies that the account is standard/active and hasn't triggered an administrative flag (like "Banned" or "Premium"), treating it as its own structural category avoids model skewing.

#### Decision 3: Fill Missing `country` Fields with `"Unknown"` 
* **Action:** Replace `NaN` values with `"Unknown"`.
* **Why:** Global location data is usually an optional self-reported field during user registration.
---
