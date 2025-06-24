### Downloads all AMC problems automatically

from aops_downloader import download_contest
import os
import json

years = list(range(2006, 2025))[::-1]
years.remove(2021)  # 2021 AMC 10/12 were held twice, no AMC 8 that year
contests = ["8", "10A", "10B", "12A", "12B"]

save_dir = "amc_problems"


def resume_download():
    for year in years:
        for contest in contests:
            contest_dir = os.path.join(save_dir, f"{contest}")
            os.makedirs(contest_dir, exist_ok=True)
            output_file = os.path.join(contest_dir, f"{year}-{contest}.json")
            if not os.path.exists(output_file):
                print(f"Downloading {year} AMC {contest} problems...")
                problems = download_contest(year, contest)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(problems, f, indent=2, ensure_ascii=False)
                print(f"Saved to {output_file}")
            else:
                print(f"Already downloaded {year} AMC {contest} problems. Skipping...")


if __name__ == "__main__":
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    resume_download()
    print("All downloads completed.")
