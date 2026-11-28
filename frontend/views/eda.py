import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import render_data_source, numeric_columns
from utils.style import apply_style, page_header

apply_style()
page_header("DATA EXPLORATION","EDA analytics","Explore missing values, distributions, correlations and raw records.")
df,source=render_data_source()
if df is None:
    st.warning("Upload the CSV from the sidebar."); st.stop()
st.caption(f"{source} · {len(df):,} rows · {len(df.columns):,} columns")
overview,missing,dist,relations,raw=st.tabs(["Overview","Missing values","Distributions","Relationships","Raw data"])
nums=numeric_columns(df)
with overview:
    l,r=st.columns(2)
    types=df.dtypes.astype(str).value_counts().rename_axis("dtype").reset_index(name="columns")
    fig=px.pie(types,names="dtype",values="columns",hole=.55,title="Column type composition")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=340)
    l.plotly_chart(fig,use_container_width=True)
    r.metric("Duplicate rows",f"{int(df.duplicated().sum()):,}")
    r.metric("Missing cells",f"{int(df.isna().sum().sum()):,}")
    r.metric("Numeric fields",f"{len(nums):,}")
    if nums: st.dataframe(df[nums].describe().T,use_container_width=True)
with missing:
    m=df.isna().sum().sort_values(ascending=False)
    mdf=pd.DataFrame({"column":m.index,"missing_count":m.values})
    mdf["missing_percent"]=(mdf.missing_count/max(len(df),1)*100).round(2)
    show=mdf[mdf.missing_count>0].head(40)
    if show.empty: st.success("No missing values detected.")
    else:
        fig=px.bar(show.sort_values("missing_percent"),x="missing_percent",y="column",orientation="h",title="Columns with most missing data")
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=max(380,22*len(show)))
        st.plotly_chart(fig,use_container_width=True)
    st.dataframe(mdf,use_container_width=True)
with dist:
    if not nums: st.info("No numeric fields.")
    else:
        col=st.selectbox("Numeric field",nums)
        s=pd.to_numeric(df[col],errors="coerce").dropna()
        a,b,c=st.columns(3)
        a.metric("Mean",f"{s.mean():,.3f}" if len(s) else "—")
        b.metric("Median",f"{s.median():,.3f}" if len(s) else "—")
        c.metric("Std. deviation",f"{s.std():,.3f}" if len(s) else "—")
        l,r=st.columns(2)
        f=px.histogram(x=s,nbins=45,title=f"Distribution: {col}")
        f.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350); l.plotly_chart(f,use_container_width=True)
        f=px.box(y=s,points="outliers",title=f"Spread and outliers: {col}")
        f.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350); r.plotly_chart(f,use_container_width=True)
with relations:
    if len(nums)<2: st.info("At least two numeric fields are required.")
    else:
        selected=st.multiselect("Correlation fields",nums,default=nums[:min(12,len(nums))])
        if len(selected)>=2:
            corr=df[selected].corr(numeric_only=True)
            f=px.imshow(corr,text_auto=".2f",color_continuous_scale="RdBu_r",zmin=-1,zmax=1,title="Pearson correlation matrix")
            f.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=620)
            st.plotly_chart(f,use_container_width=True)
        x=st.selectbox("X axis",nums,key="eda_x")
        y=st.selectbox("Y axis",[n for n in nums if n!=x],key="eda_y")
        sample=df[[x,y]].dropna()
        if len(sample)>6000:
            sample=sample.sample(6000,random_state=42); st.caption("Scatter chart sampled to 6,000 rows for speed.")
        f=px.scatter(sample,x=x,y=y,opacity=.55,title=f"{y} vs {x}")
        f.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=420)
        st.plotly_chart(f,use_container_width=True)
with raw:
    n=st.slider("Rows to preview",10,min(500,max(10,len(df))),min(100,max(10,len(df))))
    st.dataframe(df.head(n),use_container_width=True,height=480)
    st.download_button("Download CSV",df.to_csv(index=False).encode(),file_name="voltsight_dataset.csv",mime="text/csv")
