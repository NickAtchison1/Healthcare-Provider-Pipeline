import json
import sqlite3
import requests


# 1. OBJECT-ORIENTED ENGINE: Handles communication with the 3rd party system
class NPPESClient:
    """Handles connections, parameter payloads, and HTTP request routing

    to the CMS National Provider Registry API.
    """

    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"

    def __init__(self):
        self.session = requests.Session()
        # 🟢 UPDATED: Complete enterprise browser header emulation stack to prevent drops
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def search_providers(self, city: str, state: str, limit: int = 10) -> list:
        """Queries the public CMS registry for healthcare organizations or

        providers.
        """
        payload = {
            "version": "2.1",
            "city": city,
            "state": state,
            "limit": limit,
            "exact_match": "yes",
        }
        try:
            print(
                f"[INFO] Securely querying API endpoint for active providers in {city.upper()}, {state.upper()}..."
            )
            # We add a small timeout rule to keep the handshake stable
            response = self.session.get(
                self.BASE_URL, params=payload, timeout=15
            )

            # Raise an exception for HTTP error statuses (400s, 500s)
            response.raise_for_status()
            data = response.json()

            # Return the raw array of result dictionaries
            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"[FATAL ERROR] API connection failed: {e}")
            return []


# 2. PROCEDURAL PIPELINE: Line-by-line ETL transformation and storage logic
def run_daily_etl():
    target_city = "Indianapolis"
    target_state = "IN"

    api_client = NPPESClient()
    raw_results = api_client.search_providers(
        city=target_city, state=target_state, limit=20
    )

    if not raw_results:
        print("[WARNING] No records retrieved. Exiting data pipeline.")
        return

    clean_records = []
    for record in raw_results:
        npi = record.get("number")
        basic_info = record.get("basic", {})

        addresses = record.get("addresses", [])
        primary_address = addresses[0] if addresses else {}

        entity_type = record.get("enumeration_type", "UNKNOWN")
        if entity_type == "NPI-2":
            provider_name = basic_info.get(
                "organization_name", "UNKNOWN FACILITY"
            )
        else:
            first_name = basic_info.get("first_name", "")
            last_name = basic_info.get("last_name", "")
            provider_name = f"{last_name}, {first_name}".strip(", ")

        street = primary_address.get("address_1", "NOT PROVIDED")
        postal_code = primary_address.get("postal_code", "00000")

        clean_row = (
            npi,
            provider_name.upper(),
            entity_type,
            street.upper(),
            postal_code,
        )
        clean_records = [*clean_records, clean_row]

    print(
        f"[INFO] Successfully parsed and sanitized {len(clean_records)} enterprise data records."
    )

    try:
        db_connection = sqlite3.connect("healthcare_provider_warehouse.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS staging_providers (
                npi_number INTEGER PRIMARY KEY,
                provider_name TEXT NOT NULL,
                entity_type TEXT,
                street_address TEXT,
                postal_code TEXT
            )
        """
        )

        db_cursor.executemany(
            """
            INSERT OR REPLACE INTO staging_providers (npi_number, provider_name, entity_type, street_address, postal_code)
            VALUES (?, ?, ?, ?, ?)
        """,
            clean_records,
        )

        db_connection.commit()
        print(
            "[SUCCESS] Batch transaction complete. Data committed into 'staging_providers' table."
        )

    except sqlite3.Error as db_error:
        print(f"[DATABASE ERROR] SQL Operation failed: {db_error}")
    finally:
        db_connection.close()
        print("[INFO] Relational database connection safely closed.")


if __name__ == "__main__":
    run_daily_etl()
