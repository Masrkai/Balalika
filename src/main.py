import argparse
from pathlib import Path

from src.data.countries import resolve_countries
from src.data.units import build_units, split_units, filter_units, Unit
from src.scraper.scrape import fetch_and_parse_batch, fetch_job_details
from src.scraper.checkpoint import (
    get_unit_checkpoint,
    update_unit_checkpoint,
    reset_unit_checkpoint,
)
from src.data.storage import append_to_csv_shard, append_to_jsonl_shard

DEFAULT_CATEGORIES = Path("Data/CS_Jobs.json")


def main():
    parser = argparse.ArgumentParser(description="Distributed LinkedIn job scraper.")
    parser.add_argument("--device", type=int, default=None, help="Device index (1-based)")
    parser.add_argument("--of", type=int, default=None, help="Total device count for mod-split")
    parser.add_argument("--countries", type=str, default=None,
                        help="Comma-separated country filter (overrides mod-split)")
    parser.add_argument("--categories", type=str, default=None,
                        help="Comma-separated category filter")
    parser.add_argument("--device-id", type=str, default=None,
                        help="Shard identifier (defaults to device index)")
    parser.add_argument("--full-countries", action="store_true",
                        help="Use the full country list instead of the default 9")
    parser.add_argument("--override-checkpoint", action="store_true",
                        help="Reset this device's per-unit checkpoints")
    parser.add_argument("--categories-file", type=Path, default=DEFAULT_CATEGORIES)
    parser.add_argument("--data-dir", type=Path, default=Path("Data"))
    args = parser.parse_args()

    if (args.device is None) != (args.of is None):
        parser.error("--device and --of must be supplied together")
    if args.device is not None and args.of is not None and args.countries:
        parser.error("--countries overrides mod-split; do not combine with --device/--of")

    device_id = args.device_id or (f"dev{args.device}" if args.device else "local")
    checkpoint_path = args.data_dir / "checkpoints" / f"{device_id}.json"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    if args.override_checkpoint:
        print(f"Resetting checkpoints for {device_id}...")
        reset_unit_checkpoint(checkpoint_path)

    # Build the full matrix, then select this device's slice.
    all_units = build_units(
        args.categories_file,
        countries_spec=args.countries,
        full_countries=args.full_countries,
    )
    if args.device is not None and args.of is not None:
        owned = split_units(all_units, args.device, args.of)
    else:
        owned = filter_units(all_units, args.countries, args.categories)

    if not owned:
        print("No units assigned to this device. Nothing to do.")
        return

    print(f"Device {device_id}: {len(owned)} units of {len(all_units)} total.")

    try:
        for unit in owned:
            run_unit(unit, checkpoint_path, args.data_dir, device_id)
    except KeyboardInterrupt:
        print("\nStopping... checkpoints saved.")


def run_unit(unit: Unit, checkpoint_path: Path, data_dir: Path, device_id: str) -> None:
    start = get_unit_checkpoint(checkpoint_path, unit.id)
    seen_urls = set()
    print(f"[{unit.id}] start={start}")
    while True:
        jobs, next_start = fetch_and_parse_batch(
            unit.keyword, unit.country, start=start
        )
        if not jobs:
            print(f"[{unit.id}] no more jobs.")
            break

        new_jobs = []
        for job in jobs:
            url = job.get("job_url")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            new_jobs.append(job)
        jobs = new_jobs

        if jobs:
            for job in jobs:
                description, salary_detail = fetch_job_details(job["job_url"])
                if description:
                    job["description"] = description
                if salary_detail:
                    job["salary"] = salary_detail
            append_to_jsonl_shard(jobs, data_dir, device_id)
            append_to_csv_shard(jobs, data_dir, device_id)
            print(f"[{unit.id}] saved {len(jobs)} jobs. checkpoint -> {next_start}")

        update_unit_checkpoint(checkpoint_path, unit.id, next_start)
        start = next_start


if __name__ == "__main__":
    main()
