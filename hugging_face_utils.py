import os
from dotenv import load_dotenv
from huggingface_hub import HfApi
from typing import List

load_dotenv() 
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")


def get_hf_datasets(sort_option,file_format,limit: int = 10) -> List[str]:
    try:
        # Initialize the Hugging Face API client
        api = HfApi(endpoint="https://huggingface.co",token=huggingface_token)
 
        dataset_props = api.list_datasets(
            sort=sort_option,
            direction=-1,
            gated=False,
            expand=["description"],
            tags=f"format:{file_format}", 
            limit=limit
        )
        
        # Extract just the dataset names
        # dataset_names = [dataset.id for dataset in dataset_props]
        dataset_props = [(dataset.id, dataset.description) for dataset in dataset_props]
        
        return dataset_props
        
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return []