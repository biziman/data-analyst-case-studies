"""Generate a fictional mobile game SDK incident dataset (all records synthetic)."""
import csv
import datetime as dt
import random
from pathlib import Path

SEED = 481516
START = dt.date(2026, 5, 1)
DAYS = 45
OUT = Path(__file__).parent / "data"
EVENT_FILE = OUT / "events.csv"
TRUTH_FILE = OUT / "simulation_truth.csv"
FIELDS = ["event_id", "user_id", "event_name", "event_timestamp", "received_timestamp", "platform", "app_version", "country", "acquisition_channel"]


def generate():
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    truth = []
    with EVENT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        for offset in range(DAYS):
            day = START + dt.timedelta(days=offset)
            n_active = int(720 * (1.08 if day.weekday() >= 5 else 1) * rng.uniform(.97, 1.03))
            by_platform = {"Android": 0, "iOS": 0}
            for user_n in range(n_active):
                uid = f"u{user_n:05d}"
                platform = "Android" if user_n % 100 < 58 else "iOS"
                by_platform[platform] += 1
                android_live = day >= dt.date(2026, 5, 12)
                ios_live = day >= dt.date(2026, 5, 15)
                rollout = android_live if platform == "Android" else ios_live
                version = ("4.8.0" if rollout else ("4.7.9" if platform == "Android" else "4.7.8"))
                country = rng.choices(["US", "GB", "DE", "TR", "BR"], [.28, .18, .16, .16, .22])[0]
                channel = rng.choices(["Paid Social", "Search Ads", "Organic", "Influencer"], [.34, .24, .32, .10])[0]
                if day >= dt.date(2026, 5, 12) and rng.random() < .08:
                    channel = "Organic"
                base = dt.datetime.combine(day, dt.time(8)) + dt.timedelta(seconds=rng.randrange(14 * 3600))
                event_names = ["app_open", "session_start"] + rng.choices(["level_start", "purchase"], [0.88, 0.12], k=rng.choices([0, 1, 2], [.25, .58, .17])[0])
                # A fixed subset of upgraded players loses its ID on all client events.
                id_broken = rollout and rng.random() < .08
                for j, name in enumerate(event_names):
                    event_time = base + dt.timedelta(minutes=6*j + rng.randrange(4))
                    # Pre-release background missingness is rare; post-release failure is correlated by player.
                    missing_id = id_broken or (not rollout and rng.random() < .005)
                    user_value = "" if missing_id else uid
                    delay_h = rng.expovariate(1 / .18)
                    if rollout and rng.random() < .11:
                        delay_h += rng.uniform(1.5, 8)
                    event_id = f"{day:%Y%m%d}_{uid}_{j}"
                    row = [event_id, user_value, name, event_time.isoformat(sep=" "), (event_time + dt.timedelta(hours=delay_h)).isoformat(sep=" "), platform, version, country, channel]
                    writer.writerow(row)
                    # Retry duplicates affect event counts, not unique-user DAU in this analysis.
                    if name == "session_start" and rollout and rng.random() < .035:
                        duplicate = row.copy()
                        duplicate[0] += "_retry"
                        duplicate[4] = (event_time + dt.timedelta(hours=delay_h, seconds=rng.randrange(1, 90))).isoformat(sep=" ")
                        writer.writerow(duplicate)
            truth.append([day.isoformat(), n_active, by_platform["Android"], by_platform["iOS"], int(day >= dt.date(2026,5,12)), int(day >= dt.date(2026,5,15))])
    with TRUTH_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "true_active_users", "true_android_active_users", "true_ios_active_users", "android_rollout_active", "ios_rollout_active"])
        writer.writerows(truth)
    print(f"Wrote {EVENT_FILE} and {TRUTH_FILE}")


if __name__ == "__main__":
    generate()
