# DuckHug

<img src="public/duckhug_logo.jpg" alt="DuckHug Logo" width="200"/>

Query Hugging Face datasets directly from Streamlit using DuckDB's powerful SQL engine.

## Features

### Dataset Management
- 🔍 Browse and search Hugging Face datasets
- ✏️ Manually add custom dataset paths
- 👀 Preview datasets with up to 100 rows

### Query Capabilities
- 📊 Automatic column detection
- 🔧 Custom SQL query support
- 💪 Efficient data handling with DuckDB

### User Experience
- 🌟 Modern Streamlit-based UI
- 🔗 Direct links to Hugging Face dataset pages

### Live app
https://duckhug.streamlit.app/

## Run locally
1. Install dependencies: `pip install -r requirements.txt`
2. Add your Hugging face API token to .env file(Only for fetching data sets, manual dataset will work without it)
3. Run the app: `streamlit run home.py`
4. Start exploring datasets!

## Credits
- Powered by DuckDB: [Star on GitHub](https://github.com/duckdb/duckdb)
- Logo created using [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- Built with ❤️ for the data community

## Support
Found an issue or have suggestions? [Open an issue](https://github.com/g-kannan/DuckHug/issues/new/choose)
If you find this useful, please [give us a star on GitHub](https://github.com/g-kannan/DuckHug)!
