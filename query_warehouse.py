import sqlite3


def analyze_warehouse_data():
    """Establishes a connection to the local SQLite warehouse and executes

    analytical queries to summarize provider profiles.
    """
    database_file = "healthcare_provider_warehouse.db"

    try:
        # Step 1: Establish the transactional database connection
        print(f"[INFO] Connecting to local data asset: '{database_file}'...")
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()

        # Step 2: Define your analytical SQL query
        # This mirrors a standard T-SQL/SQL Server query structure
        sql_query = """
            SELECT 
                entity_type,
                COUNT(*) as total_records,
                MIN(postal_code) as sample_zip
            FROM staging_providers
            GROUP BY entity_type
            ORDER BY total_records DESC;
        """

        print("[INFO] Executing relational aggregation query...")
        cursor.execute(sql_query)

        # Step 3: Fetch structural database tuples
        results = cursor.fetchall()

        # Step 4: Format and print output cleanly to console/log
        print("\n" + "=" * 50)
        print(f"{'ENTITY TYPE':<15} | {'TOTAL RECORDS':<15} | {'SAMPLE ZIP':<10}")
        print("=" * 50)

        for row in results:
            entity_type, total, zip_code = row
            print(f"{entity_type:<15} | {total:<15} | {zip_code:<10}")

        print("=" * 50 + "\n")

    except sqlite3.Error as sql_error:
        print(f"[DATABASE ERROR] Query execution failed: {sql_error}")

    finally:
        # Step 5: Always close connection hooks to protect files from corruption
        connection.close()
        print("[INFO] Relational database connection safely closed.")


if __name__ == "__main__":
    analyze_warehouse_data()
