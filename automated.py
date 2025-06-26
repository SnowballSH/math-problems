### Downloads all AMC problems automatically

import time
from aops_downloader import download_contest
import os
import json

years = reversed(list(map(str, range(1983, 2026))) + ["2021 Fall"])
contests = ["8", "10A", "10B", "12A", "12B"]

amc_dir = "amc_problems"
aime_dir = "aime_problems"
ahsme_dir = "ahsme_problems"


def resume_download():
    for year in years:
        year_int = int(str(year).split()[0])
        contests_available = (
            []
            if year_int <= 2001
            else ["10A", "10B", "12A", "12B"]
            if "2021" in year
            else ["8"]
            if "2025" in year
            else contests
        )
        aime = (
            []
            if "Fall" in year
            else (["AIME I", "AIME II"] if year_int >= 2000 else ["AIME"])
        )
        contests_available = list(contests_available) + aime
        if year_int <= 1999:
            contests_available.append("AHSME")

        for contest in contests_available:
            c_upper = contest.upper()
            if c_upper.startswith("AIME"):
                base_dir = aime_dir
            elif c_upper == "AHSME":
                base_dir = ahsme_dir
            else:
                base_dir = amc_dir

            contest_dir = os.path.join(base_dir, contest)
            os.makedirs(contest_dir, exist_ok=True)
            output_file = os.path.join(contest_dir, f"{year}-{contest}.json")
            if not os.path.exists(output_file):
                done = False
                while not done:
                    print(f"Downloading {year} {contest} problems...")
                    try:
                        problems = download_contest(year, contest)
                    except Exception as e:
                        print(f"Error downloading {year} {contest}: {e}")
                        time.sleep(61)
                        continue
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(problems, f, indent=2, ensure_ascii=False)
                    print(f"Saved to {output_file}")
                    done = True
            else:
                print(f"Already downloaded {year} {contest} problems. Skipping...")


if __name__ == "__main__":
    for d in (amc_dir, aime_dir, ahsme_dir):
        os.makedirs(d, exist_ok=True)
    resume_download()
    print("All downloads completed.")
