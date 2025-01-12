import streamlit as st
import duckdb
from hugging_face_utils import get_hf_datasets
import polars as pl

# Initialize session state variables if they don't exist
if 'datasets' not in st.session_state:
    st.session_state.datasets = []

if 'show_input' not in st.session_state:
    st.session_state.show_input = False

conn = duckdb.connect(database=':memory:')
conn.execute("INSTALL httpfs;LOAD httpfs;")

st.set_page_config(page_title="DuckHug",layout="wide")

st.image("public/duckhug_logo.jpg",width=150)
st.header("Query Hugging face datasets more easily")

sort_options = {
    "Trending": "trending_score",
    "Newest": "last_modified",
    "Most Downloads": "downloads",
    "Most Likes": "likes",
}

file_formats = ["csv","arrow","parquet"]

file_format = st.selectbox("Select File Format", file_formats)
sort_option = st.selectbox("Select Sort Option", list(sort_options.keys()))

# limit = st.number_input("Enter number of datasets to display", min_value=1, value=10)

if st.button("Fetch Datasets"):
    sort_by = sort_options[sort_option]
    dataset_props = get_hf_datasets(sort_by,file_format)
    st.session_state.datasets = [dataset[0] for dataset in dataset_props]
    props_df = pl.DataFrame(dataset_props, schema=["id", "description"])
    if len(st.session_state.datasets) == 0:
        st.info("No datasets found, please try different sort option or file format or enter manually")
    else:
        st.info(f"Fetched {len(st.session_state.datasets)} datasets")
    st.dataframe(props_df,hide_index=True,use_container_width=True)
    # st.write(st.session_state.datasets)

if st.button("Manually enter dataset"):
    st.session_state.show_input = True

# Show the input field if the button was clicked
if st.session_state.show_input:
    manual_dataset = st.text_input("Enter dataset name", key="manual_dataset_input")
    if st.button("Add Dataset"):
        st.session_state.datasets.append(manual_dataset)
        st.success(f"Added dataset: {manual_dataset}")

dataset_to_preview = st.selectbox("Select dataset to preview", st.session_state.datasets)
if dataset_to_preview is None:
    dataset_to_preview = "Test"
    view_name = "TEST"
else:
    view_name = dataset_to_preview.replace("/","_").replace("-","_").replace(".","_").upper()
st.write("view_name: " + view_name)
st.write("Locate this dataset on Hugging Face: https://huggingface.co/datasets/" + dataset_to_preview)
view_query = f"CREATE OR REPLACE VIEW {view_name} AS (SELECT * FROM read_parquet('hf://datasets/{dataset_to_preview}@~parquet/default/train/*.parquet') );"
select_query = f"SELECT * FROM {view_name} limit 1000;"
st.code(view_query + "\n\n" + select_query)
if st.button("Preview Dataset(1000 Rows)"):
    conn.execute(view_query)
    result_df = conn.sql(select_query).df()
    # result_df = conn.sql("SELECT * FROM read_parquet('hf://datasets/nyuuzyou/subdomains@~parquet/default/train/*.parquet') limit 1000;").df()
    # result_df = conn.sql(f"SELECT * FROM read_parquet('hf://datasets/floworks/HubBench-queries@~parquet/default/train/*.parquet') limit {limit};").df()
    # result_df = pl.read_csv('hf://datasets/Aurelium/github-repo-enumeration/**/*.csv').limit(1000)
    # cornell-movie-review-data/rotten_tomatoes
    st.dataframe(result_df,hide_index=True,use_container_width=True)
    # st.write(result_df)

query = st.text_area("Enter your query",value=f"{select_query}")
if st.button("Run Query"):
    conn.execute(view_query)
    result_df = conn.sql(query).df()
    st.dataframe(result_df,hide_index=True,use_container_width=True)