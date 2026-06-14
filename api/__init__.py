"""FastAPI backend — the controlled gateway between the UI and the data stores.

The browser never talks to Databricks/Redis/Neo4j directly; every read goes
through a typed endpoint here (PRD Section 7; roadmap Step 5.1).
"""
