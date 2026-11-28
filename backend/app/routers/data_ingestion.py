import re
import hashlib
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
import os

from fastapi.params import Form
import pandas as pd

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
)

from sqlalchemy import inspect

from app.core.database import engine

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Ingestion"]
)


MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
DB_SCHEMA = "public"


# --------------------------------------------------
# 1. Clean table and column names
# --------------------------------------------------

def clean_identifier(name: str) -> str:

    name = str(name).strip().lower()

    name = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        name
    )

    name = name.strip("_")

    if not name:
        name = "unnamed_column"

    if name[0].isdigit():
        name = f"col_{name}"

    # PostgreSQL identifier limit: 63 bytes.
    if len(name) > 63:
        suffix = hashlib.md5(
            name.encode()
        ).hexdigest()[:8]

        name = f"{name[:54]}_{suffix}"

    return name


def generate_table_name(filename: str) -> str:

    file_stem = Path(filename).stem

    cleaned_name = clean_identifier(file_stem)

    return f"raw_{cleaned_name}"


# --------------------------------------------------
# 2. Clean CSV column names
# --------------------------------------------------

def clean_dataframe_columns(df: pd.DataFrame):

    original_columns = list(df.columns)

    cleaned_columns = [
        clean_identifier(column)
        for column in original_columns
    ]

    # Prevent different original names from becoming
    # the same PostgreSQL column name.
    if len(cleaned_columns) != len(set(cleaned_columns)):
        raise ValueError(
            "Duplicate column names detected after cleaning."
        )

    df.columns = cleaned_columns

    return df


# --------------------------------------------------
# 3. CSV Upload API
# --------------------------------------------------

@router.post(
    "/upload-csv",
    status_code=status.HTTP_201_CREATED
)
async def upload_csv(
    file: UploadFile = File(...),
    secret: str = Form(...)
):

    # Validate Secret key to upload CSV
    if secret != os.getenv("UPLOAD_CSV_SECRET_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Invalid secret key"
        )
    
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    # Read uploaded file
    contents = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 50 MB limit."
        )

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV file is empty."
        )

    # --------------------------------------------------
    # Read CSV using Pandas
    # --------------------------------------------------

    try:

        df = pd.read_csv(
            BytesIO(contents),
            low_memory=False
        )

        if len(df.columns) == 0:
            raise ValueError("CSV contains no columns.")

        df = clean_dataframe_columns(df)

        # Improve Pandas dtype inference
        df = df.convert_dtypes()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process CSV: {str(exc)}"
        )

    # --------------------------------------------------
    # Generate PostgreSQL table name
    # --------------------------------------------------

    table_name = generate_table_name(file.filename)

    # --------------------------------------------------
    # Create table if missing and insert rows
    # --------------------------------------------------

    try:

        with engine.begin() as connection:

            inspector = inspect(connection)

            table_exists = inspector.has_table(
                table_name,
                schema=DB_SCHEMA
            )

            if table_exists:

                existing_columns = [
                    column["name"]
                    for column in inspector.get_columns(
                        table_name,
                        schema=DB_SCHEMA
                    )
                ]

                uploaded_columns = list(df.columns)

                # Prevent inserting incompatible CSV schemas
                if set(existing_columns) != set(uploaded_columns):

                    raise HTTPException(
                        status_code=409,
                        detail={
                            "message": "Table already exists with a different column structure.",
                            "table": table_name,
                            "existing_columns": existing_columns,
                            "uploaded_columns": uploaded_columns
                        }
                    )

            # Pandas creates the table automatically
            # when it does not already exist.
            inserted_rows = df.to_sql(
                name=table_name,
                con=connection,
                schema=DB_SCHEMA,
                if_exists="append",
                index=False,
                chunksize=1000
            )

            if inserted_rows is None:
                inserted_rows = len(df)

        return {
            "success": True,
            "message": "CSV data imported successfully.",
            "filename": file.filename,
            "table_name": table_name,
            "schema": DB_SCHEMA,
            "table_created": not table_exists,
            "columns": list(df.columns),
            "total_columns": len(df.columns),
            "rows_inserted": int(inserted_rows)
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Database import failed: {str(exc)}"
        )
