import streamlit as st
import pandas as pd
from utils.data_loader import render_data_source, numeric_columns, find_date_column
from utils.style import apply_style, page_header

apply_style()
page_header("DATA QUALITY","Data insights","A diagnostic report to help review the dataset before model training.")
df,source=render_data_source()
if df is None:
    st.warning("Upload the CSV from the sidebar."); st.stop()
missing=(df.isna().sum()/max(len(df),1)*100).sort_values(ascending=False)
constant=[c for c in df.columns if df[c].nunique(dropna=True)<=1]
a,b,c,d=st.columns(4)
a.metric("Rows",f"{len(df):,}"); b.metric("Duplicate rows",f"{int(df.duplicated().sum()):,}")
c.metric("Columns with nulls",f"{int((missing>0).sum()):,}"); d.metric("Constant columns",f"{len(constant):,}")
report=pd.DataFrame({"column":df.columns,"dtype":[str(df[x].dtype) for x in df.columns],
 "missing_count":[int(df[x].isna().sum()) for x in df.columns],
 "missing_percent":[round(float(missing[x]),2) for x in df.columns],
 "unique_values":[int(df[x].nunique(dropna=True)) for x in df.columns]})
report["review_flag"]=report.apply(lambda r:"High missingness" if r.missing_percent>=50 else ("Constant / near-constant" if r.unique_values<=1 else ("Some missing values" if r.missing_count else "No obvious issue")),axis=1)
st.subheader("Column quality report")
st.dataframe(report.sort_values(["missing_percent","unique_values"],ascending=[False,True]),use_container_width=True,height=480)
st.download_button("Download quality report",report.to_csv(index=False).encode(),file_name="voltsight_data_quality.csv",mime="text/csv")
st.subheader("Modelling checks")
st.write(f"**Date field detected:** `{find_date_column(df) or 'Not detected'}`")
st.write(f"**Numeric features:** {len(numeric_columns(df))}")
st.write(f"**Columns with at least 50% missing:** {int((missing>=50).sum())}")
st.info("These are diagnostic flags, not automatic instructions to delete columns. Review each field's meaning and its role in the target before changing the training data.")
