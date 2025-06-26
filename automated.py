### Downloads all AMC problems automatically

import time
from aops_downloader import download_contest
import os
import json

years = reversed(list(map(str, range(2002, 2026))) + ["2021 Fall"])
contests = ["8", "10A", "10B", "12A", "12B"]

save_dir = "amc_problems"


def resume_download():
    for year in years:
        contests_available = (
            ["10A", "10B", "12A", "12B"]
            if "2021" in year
            else ["8"]
            if "2025" in year
            else contests
        )
        for contest in contests_available:
            contest_dir = os.path.join(save_dir, f"{contest}")
            os.makedirs(contest_dir, exist_ok=True)
            output_file = os.path.join(contest_dir, f"{year}-{contest}.json")
            if not os.path.exists(output_file):
                done = False
                while not done:
                    print(f"Downloading {year} AMC {contest} problems...")
                    try:
                        problems = download_contest(year, contest)
                    except Exception as e:
                        print(f"Error downloading {year} AMC {contest}: {e}")
                        time.sleep(61)
                        continue
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(problems, f, indent=2, ensure_ascii=False)
                    print(f"Saved to {output_file}")
                    done = True
            else:
                print(f"Already downloaded {year} AMC {contest} problems. Skipping...")


if __name__ == "__main__":
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    resume_download()
    print("All downloads completed.")
