import os
from datasets import load_dataset
import pandas as pd

def download_cuad():
    print("Downloading CUAD dataset from Hugging Face...")

    # load cuad dataset
    dataset = load_dataset("theatticusproject/cuad",
                           data_files="CUAD_v1/master_clauses.csv")

    df = dataset["train"].to_pandas()

    os.makedirs("backend/data/cuad_raw", exist_ok=True)

    # save locally
    save_path = "backend/data/cuad_raw/master_clauses.csv"
    df.to_csv(save_path, index=False)

    print(f"CUAD dataset downloaded and saved to {save_path}")
    print(f"Total clauses loaded: {len(df)}")

    return df

if __name__ == "__main__":
    download_cuad()


