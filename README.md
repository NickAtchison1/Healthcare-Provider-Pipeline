# US Healthcare Provider & Facility Directory Integration Pipeline

### Project Overview
An automated, production-grade ELT (Extract, Load, Transform) data pipeline designed to integrate with the Centers for Medicare & Medicaid Services (CMS) National Plan and Provider Enumeration System (NPPES) registry. This system handles real-time extraction of healthcare provider and clinic registration data, executes strict data hygiene and transformation rules, and safely ingests the records into an idempotent relational database staging store.

### Key Architectural Patterns
* **Object-Oriented Infrastructure Engine:** Utilizes an encapsulated, reusable client pattern (`requests.Session`) to manage API connections, query payloads, and optimize network overhead through connection pooling.
* **Network Handshake Emulation:** Implements production-grade enterprise browser emulation headers within the session client to safely bypass standard automated gateway firewall resets.
* **Defensive JSON Data Parsing:** Implements non-destructive dictionary methods (`.get()`) and array length safety checks to robustly traverse complex, deeply nested JSON API payloads, preventing pipeline runtime failures from unexpected null or missing third-party values.
* **Idempotent Transaction Processing:** Employs defensive relational database design strategies (`INSERT OR REPLACE`) to ensure that multiple batch executions safely overwrite existing records instead of generating data duplication or key constraint corruption.

### Technology Stack
* **Language:** Python 3
* **Libraries:** Requests (Network layer / HTTP Routing)
* **Target Storage Platform:** SQLite 3 (Local Relational Engine)
* **Architecture Style:** Mixed Object-Oriented (Client-side) & Procedural (Pipeline Workflow)

### Project Structure
* `nppes_pipeline.py`: The core ingestion engine that extracts data from the CMS registry API, maps properties, and manages the database staging table lifecycle.
* `query_warehouse.py`: An analytical script that programmatically connects to the local relational repository to perform transactional aggregations.

### How to Run Locally
1. Clone this repository to your environment.
2. Ensure dependencies are satisfied:
   ```bash
   pip install requests
   ```
3. Execute the pipeline driver:
   ```bash
   python nppes_pipeline.py
   ```
4. Query the relational database:
   ```bash
   python query_warehouse.py
   ```
