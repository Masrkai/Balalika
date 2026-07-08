import argparse
from pathlib import Path
from src.scraper.scrape import fetch_and_parse_batch, fetch_job_details
from src.scraper.checkpoint import get_checkpoint, update_checkpoint, reset_checkpoint
from src.data.storage import append_to_csv, append_to_jsonl

def main():
    parser = argparse.ArgumentParser(description="Scrape LinkedIn jobs.")
    parser.add_argument("--override-checkpoint", action="store_true", help="Reset checkpoint")
    args = parser.parse_args()

    # Configuration
    keywords = "software engineer"
    location = "New York, United States"
    data_dir = Path("Data")
    checkpoint_path = data_dir / "checkpoint.json"
    jsonl_path = data_dir / "jobs.jsonl"

    if args.override_checkpoint:
        print("Resetting checkpoint...")
        reset_checkpoint(checkpoint_path)

    start_index = get_checkpoint(checkpoint_path)
    print(f"Starting from index: {start_index}")

    try:
        while True:
            print(f"Fetching batch starting at {start_index}...")
            jobs, next_start = fetch_and_parse_batch(keywords, location, start=start_index)
            
            if not jobs:
                print("No more jobs found.")
                break
            
            # Save data
            # Enrich data with details
            for job in jobs:
                description, salary_detail = fetch_job_details(job['job_url'])
                if description:
                    job['description'] = description
                if salary_detail:
                    job['salary'] = salary_detail
            
            append_to_jsonl(jobs, jsonl_path)

            
            # Update checkpoint
            update_checkpoint(checkpoint_path, next_start)
            start_index = next_start
            print(f"Saved {len(jobs)} jobs. New checkpoint: {start_index}")
            
    except KeyboardInterrupt:
        print("\nStopping... Checkpoint saved.")

if __name__ == "__main__":
    main()
