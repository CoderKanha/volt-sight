
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import inspect, text

from app.core.database import engine


router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Retrieval"]
)

DB_SCHEMA = "public"


@router.get("/tables")
def get_available_tables():
    """
    Return all available tables in the public schema.
    """
    try:
        inspector = inspect(engine)

        tables = inspector.get_table_names(
            schema=DB_SCHEMA
        )

        return {
            "success": True,
            "schema": DB_SCHEMA,
            "tables": tables,
            "total_tables": len(tables)
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch tables: {str(exc)}"
        )


@router.get("/{table_name}")
def fetch_table_data(
    table_name: str,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0)
):
    """
    Fetch records from a dynamically selected database table.
    Supports pagination.
    """

    # Validate table name to prevent SQL injection
    if not re.fullmatch(
        r"[a-zA-Z_][a-zA-Z0-9_]{0,62}",
        table_name
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid table name."
        )

    try:
        inspector = inspect(engine)

        if not inspector.has_table(
            table_name,
            schema=DB_SCHEMA
        ):
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' does not exist."
            )

        # Get column names
        column_details = inspector.get_columns(
            table_name,
            schema=DB_SCHEMA
        )

        columns = [
            column["name"]
            for column in column_details
        ]

        # Safely quote PostgreSQL identifiers
        preparer = engine.dialect.identifier_preparer

        quoted_schema = preparer.quote_schema(DB_SCHEMA)
        quoted_table = preparer.quote(table_name)

        table_reference = f"{quoted_schema}.{quoted_table}"

        with engine.connect() as connection:

            # Total number of records
            total_count = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM {table_reference}"
                )
            ).scalar_one()

            # Fetch requested records
            result = connection.execute(
                text(
                    f"""
                    SELECT *
                    FROM {table_reference}
                    LIMIT :limit
                    OFFSET :offset
                    """
                ),
                {
                    "limit": limit,
                    "offset": offset
                }
            )

            rows = [
                dict(row)
                for row in result.mappings().all()
            ]

        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "total_records": total_count,
            "returned_records": len(rows),
            "limit": limit,
            "offset": offset,
            "data": rows
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch table data: {str(exc)}"
        )
