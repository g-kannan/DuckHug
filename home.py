import streamlit as st
import duckdb
from hugging_face_utils import get_hf_datasets
import polars as pl

# Initialize session state variables if they don't exist
if 'datasets' not in st.session_state:
    st.session_state.datasets = []

conn = duckdb.connect(database=':memory:')
conn.execute("INSTALL httpfs;LOAD httpfs;")

st.set_page_config(layout="wide")

st.title("Query Hugging face datasets more easily")

sort_options = {
    "Trending": "trending_score",
    "Newest": "last_modified",
    "Most Downloads": "downloads",
    "Most Likes": "likes",
}

file_formats = ["csv","arrow","parquet"]

file_format = st.selectbox("Select File Format", file_formats)
sort_option = st.selectbox("Select Sort Option", list(sort_options.keys()))
limit = st.number_input("Enter number of datasets to display", min_value=1, value=10)

if st.button("Fetch Datasets"):
    sort_by = sort_options[sort_option]
    dataset_props = get_hf_datasets(sort_by,file_format,limit)
    st.session_state.datasets = [dataset[0] for dataset in dataset_props]
    props_df = pl.DataFrame(dataset_props, schema=["id", "description"])
    st.write(f"Fetched {len(st.session_state.datasets)} datasets")
    st.dataframe(props_df,hide_index=True,use_container_width=True)
    # st.write(st.session_state.datasets)

dataset_to_preview = st.selectbox("Select dataset to preview", st.session_state.datasets)
view_name = dataset_to_preview.replace("/","_").replace("-","_").replace(".","_").upper()
st.write("view_name: " + view_name)
st.write("Locate this dataset on Hugging Face: https://huggingface.co/datasets/" + dataset_to_preview)
view_query = f"CREATE OR REPLACE VIEW {view_name} AS (SELECT * FROM read_parquet('hf://datasets/{dataset_to_preview}@~parquet/default/train/*.parquet') );"
select_query = f"SELECT * FROM {view_name} limit 1000;"
st.write("DuckDB query: " + view_query)
if st.button("Preview Dataset"):
    conn.execute(view_query)
    result_df = conn.sql(select_query).df()
    # result_df = conn.sql("SELECT * FROM read_parquet('hf://datasets/nyuuzyou/subdomains@~parquet/default/train/*.parquet') limit 1000;").df()
    # result_df = conn.sql(f"SELECT * FROM read_parquet('hf://datasets/floworks/HubBench-queries@~parquet/default/train/*.parquet') limit {limit};").df()
    # result_df = pl.read_csv('hf://datasets/Aurelium/github-repo-enumeration/**/*.csv').limit(1000)
    # cornell-movie-review-data/rotten_tomatoes
    st.dataframe(result_df,hide_index=True,use_container_width=True)
    # st.write(result_df)
