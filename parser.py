import os
import json
from datetime import timedelta

COURSES = ["SCY", "LCM"]
GENDERS = ["WOMEN", "MEN"]
EVENTS = {
    "SCY": [
        "50 Free",
        "100 Free",
        "200 Free",
        "500 Free",
        "1000 Free",
        "1650 Free",
        "50 Back",
        "100 Back",
        "200 Back",
        "50 Breast",
        "100 Breast",
        "200 Breast",
        "50 Fly",
        "100 Fly",
        "200 Fly",
        "100 IM",
        "200 IM",
        "400 IM",
    ],
    "LCM": [
        "50 Free",
        "100 Free",
        "200 Free",
        "400 Free",
        "800 Free",
        "1500 Free",
        "50 Back",
        "100 Back",
        "200 Back",
        "50 Breast",
        "100 Breast",
        "200 Breast",
        "50 Fly",
        "100 Fly",
        "200 Fly",
        "200 IM",
        "400 IM",
    ],
}
AGE_GROUPS = [
    "18-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
    "75-79",
    "80-84",
]
START_YEAR = 2008


def main():
    nqts = parse_nqts()
    check_nqts(nqts)
    top_nqts = calculate_top_nqts(nqts)
    for course in COURSES:
        print(f"USMS National Qualifying Times ({course})")
        for gender in GENDERS:
            print()
            print(gender)
            print(f"EVENT,{','.join(AGE_GROUPS)}")
            for event in EVENTS[course]:
                line = [event]
                for age_group in AGE_GROUPS:
                    if (
                        top_nqts[course][gender][age_group][event]["time"]
                        == timedelta.max
                    ):
                        line.append("NO TIME")
                    else:
                        time = top_nqts[course][gender][age_group][event][
                            "time"
                        ]
                        minutes, seconds = divmod(time.seconds, 60)
                        hours, minutes = divmod(minutes, 60)
                        hundrenths = round(time.microseconds / 10000)
                        line.append(
                            f"{hours}:{minutes:02}:{seconds:02}.{hundrenths:02}".lstrip(
                                "0:"
                            )
                        )

                print(",".join(line))

        print()
        print()


def parse_nqts():
    nqts = {}
    year = START_YEAR
    while True:
        for course in COURSES:
            if not os.path.exists(f"NQTs/{year}-{course}.txt"):
                return nqts

            with open(f"NQTs/{year}-{course}.txt") as f:
                for i, line in enumerate(f.readlines()):
                    line = line.replace("NO TIME", "NT")
                    line = line.replace("No Time", "NT")
                    line = line.replace("‐", "-")
                    line = line.replace(" :", " ")
                    cells = line.split()
                    if cells[0].upper() in GENDERS:
                        gender = cells[0].upper()
                    elif cells[0].upper() == "EVENT":
                        for j, age_group in enumerate(cells[1:]):
                            if age_group != AGE_GROUPS[j]:
                                print(
                                    f"Error parsing line {i} of "
                                    f'"NQTs/{year}-{course}.txt": String '
                                    f'"{age_group}" is not equal to age group '
                                    f'"{AGE_GROUPS[j]}"'
                                )
                                exit()
                    elif f"{cells[0]} {cells[1]}" in EVENTS[course]:
                        event = f"{cells[0]} {cells[1]}"
                        for j, time in enumerate(cells[2:]):
                            if course not in nqts:
                                nqts[course] = {}

                            if gender not in nqts[course]:
                                nqts[course][gender] = {}

                            if AGE_GROUPS[j] not in nqts[course][gender]:
                                nqts[course][gender][AGE_GROUPS[j]] = {}

                            if (
                                event
                                not in nqts[course][gender][AGE_GROUPS[j]]
                            ):
                                nqts[course][gender][AGE_GROUPS[j]][event] = []

                            if time != "NT":
                                minutes, seconds = 0, time.strip(":")
                                if ":" in time:
                                    minutes, seconds = time.split(":")

                                time = timedelta(
                                    minutes=int(minutes),
                                    seconds=float(seconds),
                                )

                            nqts[course][gender][AGE_GROUPS[j]][event].append(
                                {
                                    "time": time,
                                    "year": year,
                                }
                            )
                    else:
                        print(
                            f"Error parsing line {i} of "
                            f'"NQTs/{year}-{course}.txt": {line}'
                        )
                        exit()

        year += 1


def check_nqts(nqts):
    for course in COURSES:
        for gender in GENDERS:
            for age_group in AGE_GROUPS:
                for event in EVENTS[course]:
                    year = START_YEAR
                    for nqt in nqts[course][gender][age_group][event]:
                        if nqt["year"] != year:
                            print(
                                f"{year} is missing from {course} {gender} "
                                f"{age_group} {event}: Check "
                                f'"NQTs/{year}-{course}.txt" for parsing '
                                "errors."
                            )
                            print(nqts[course][gender][age_group][event])
                            exit()

                        year += 1

                    if os.path.exists(f"NQTs/{year}-{course}.txt"):
                        print(
                            f"{year} is missing from {course} {gender} "
                            f"{age_group} {event}: Check "
                            f'"NQTs/{year}-{course}.txt" for parsing errors.'
                        )
                        exit()


def calculate_top_nqts(nqts):
    top_nqts = {}
    for course in COURSES:
        for gender in GENDERS:
            for event in EVENTS[course]:
                time = timedelta.max
                best_nqt = {"time": timedelta.max, "year": START_YEAR}
                for age_group in reversed(AGE_GROUPS):
                    if course not in top_nqts:
                        top_nqts[course] = {}

                    if gender not in top_nqts[course]:
                        top_nqts[course][gender] = {}

                    if age_group not in top_nqts[course][gender]:
                        top_nqts[course][gender][age_group] = {}

                    for nqt in nqts[course][gender][age_group][event]:
                        if (
                            nqt["time"] != "NT"
                            and nqt["time"] < best_nqt["time"]
                        ):
                            best_nqt = nqt

                    top_nqts[course][gender][age_group][event] = best_nqt

    return top_nqts


if __name__ == "__main__":
    main()
