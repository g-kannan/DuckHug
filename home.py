import streamlit as st
import duckdb
from hugging_face_utils import get_hf_datasets
import polars as pl

# Initialize session state variables if they don't exist
if 'datasets' not in st.session_state:
    st.session_state.datasets = []

if 'cols_list' not in st.session_state:
    st.session_state.cols_list = '*'

if 'show_input' not in st.session_state:
    st.session_state.show_input = False

conn = duckdb.connect(database=':memory:')
conn.execute("INSTALL httpfs;LOAD httpfs;")

st.set_page_config(page_title="DuckHug",layout="wide")

st.image("public/duckhug_logo.jpg",width=150)
st.header("Query Hugging Face datasets more easily using DuckDB")

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
        st.session_state.datasets.insert(0,manual_dataset)
        st.success(f"Added dataset: {manual_dataset}")

dataset_to_preview = st.selectbox("Select dataset to preview", st.session_state.datasets)
if dataset_to_preview is None:
    dataset_to_preview = "Test"
    view_name = "TEST"
else:
    view_name = dataset_to_preview.replace("/","_").replace("-","_").replace(".","_").upper()
st.write("view_name: " + view_name)
locate_dataset = "Check this dataset on Hugging Face: https://huggingface.co/datasets/" + dataset_to_preview
st.write(locate_dataset)
view_query = f"CREATE OR REPLACE VIEW {view_name} AS (SELECT * FROM read_parquet('hf://datasets/{dataset_to_preview}@~parquet/default/*/*.parquet') );"
select_query = f"SELECT * FROM {view_name} limit 100;"
top1_query = f"SELECT * FROM {view_name} limit 1;"
st.code(view_query + "\n\n" + select_query,language='SQL',line_numbers=True,wrap_lines=True)
if st.button("Preview Dataset(100 Rows)"):
    try:
        conn.execute(view_query)
        result_df = conn.sql(select_query).df()
        st.dataframe(result_df,hide_index=True,use_container_width=True)
    except:
        st.warning("Failed to fetch dataset preview, this is usually due to the dataset having custom filepaths or its too large. Please " + locate_dataset)
    try:
        conn.execute(view_query)
        result_df = conn.sql(top1_query).df()
        cols = result_df.columns
        cols_list = cols.tolist()
        st.session_state.cols_list = ', '.join(cols_list)
    except:
        st.session_state.cols_list = "*"

place_holder_query = f"SELECT {st.session_state.cols_list} FROM {view_name} limit 100;"

query = st.text_area("Custom query",value=place_holder_query)
if st.button("Run Query"):
    conn.execute(view_query)
    result_df = conn.sql(query).df()
    st.dataframe(result_df,hide_index=True,use_container_width=True)

st.divider()
st.write("Thanks to the Hugging Face & DuckDB team for thier awesome work")
st.write("If you still havent starred DuckDB, please do it first: https://github.com/duckdb/duckdb")
st.write("DuckHug Logo was created using Hugging Face model: https://huggingface.co/black-forest-labs/FLUX.1-dev")
st.write("If you find this useful, please give us a star on GitHub: https://github.com/g-kannan/DuckHug")
