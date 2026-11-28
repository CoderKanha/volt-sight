import streamlit as st
import plotly.express as px
from utils.data_loader import render_data_source, find_date_column, numeric_columns, parse_date
from utils.style import apply_style, page_header

apply_style()
page_header("POWER SYSTEM OVERVIEW","Grid dashboard","A high-level view of the historical dataset loaded in Streamlit.")
df,source=render_data_source()
if df is None:
    st.warning("Upload the CSV from the sidebar."); st.stop()
date_col=find_date_column(df); nums=numeric_columns(df)
a,b,c,d=st.columns(4)
a.metric("Observations",f"{len(df):,}"); b.metric("Fields",f"{len(df.columns):,}")
c.metric("Numeric fields",f"{len(nums):,}"); d.metric("Missing cells",f"{int(df.isna().sum().sum()):,}")
data=parse_date(df,date_col)
if date_col:
    dates=data[date_col].dropna()
    if len(dates): st.write(f"**Dataset coverage:** {dates.min().date()} to {dates.max().date()}")
if nums:
    selected=st.selectbox("Choose an indicator",nums)
    chart=data[[date_col,selected]].dropna() if date_col else data[[selected]].dropna().reset_index()
    fig=px.line(chart,x=date_col,y=selected,title=f"{selected} over time") if date_col else px.line(chart,y=selected,title=f"{selected} by row")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=390)
    st.plotly_chart(fig,use_container_width=True)
    fig=px.histogram(df,x=selected,nbins=40,title=f"Distribution of {selected}")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=320)
    st.plotly_chart(fig,use_container_width=True)
    st.subheader("Numeric summary")
    st.dataframe(df[nums].describe().T,use_container_width=True)
else: st.warning("No numeric columns detected.")
