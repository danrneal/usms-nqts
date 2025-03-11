import os
import json
from datetime import datetime, timedelta
from requests_html import HTMLSession

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
START_YEAR = 2024

session = HTMLSession()


def main():
    nqts = parse_nqts()
    year = START_YEAR
    while year <= datetime.now().year:
        print(year)
        for course in COURSES:
            for gender in GENDERS:
                for age_group in AGE_GROUPS:
                    top_10 = get_top_10(course, year, gender, age_group)
                    for event in EVENTS[course]:
                        nqt = calculate_nqt(course, year, event, top_10)
                        actual_nqt = nqts[year][course][gender][age_group][
                            event
                        ]
                        if (
                            nqt == timedelta.max
                            and actual_nqt == timedelta.max
                        ):
                            continue

                        if nqt == timedelta.max or actual_nqt == timedelta.max:
                            print(
                                f"{course} {gender} {age_group} {event} is {actual_nqt} and should be {nqt}"
                            )
                            continue

                        hundredth = timedelta(0, 0, 1) * 10000
                        if not (-hundredth <= actual_nqt - nqt <= hundredth):
                            print(
                                f"{course} {gender} {age_group} {event} is {actual_nqt} and should be {nqt}"
                            )

        year += 1


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
                            if year not in nqts:
                                nqts[year] = {}

                            if course not in nqts[year]:
                                nqts[year][course] = {}

                            if gender not in nqts[year][course]:
                                nqts[year][course][gender] = {}

                            if AGE_GROUPS[j] not in nqts[year][course][gender]:
                                nqts[year][course][gender][AGE_GROUPS[j]] = {}

                            if time == "NT":
                                time = timedelta.max
                            else:
                                minutes, seconds = 0, time.strip(":")
                                if ":" in time:
                                    minutes, seconds = time.split(":")

                                time = timedelta(
                                    minutes=int(minutes),
                                    seconds=float(seconds),
                                )

                            nqts[year][course][gender][AGE_GROUPS[j]][
                                event
                            ] = time
                    else:
                        print(
                            f"Error parsing line {i} of "
                            f'"NQTs/{year}-{course}.txt": {line}'
                        )
                        exit()

        year += 1


def get_top_10(course, year, gender, age_group):
    with open(f"top_10.json") as f:
        top_10 = json.load(f)

    if course not in top_10:
        top_10[course] = {}

    if gender not in top_10[course]:
        top_10[course][gender] = {}

    if age_group not in top_10[course][gender]:
        top_10[course][gender][age_group] = {}

    if str(year) not in top_10[course][gender][age_group]:
        top_10[course][gender][age_group][str(year)] = {}
        course_id = COURSES.index(course) + 1
        age_group_id = AGE_GROUPS.index(age_group) + 1
        print(
            f"Getting Top 10 Times for {year} {course} {gender} {age_group}."
        )
        url = (
            f"https://www.usms.org/comp/tt/toptenlist.php?CourseID={course_id}"
            f"&Year={year}&Sex={gender[0]}&AgeGroupID={age_group_id}"
        )
        r = session.get(url)
        for event in EVENTS[course]:
            top_10[course][gender][age_group][str(year)][event] = {}
            table = r.html.find(
                f"#Event{event.replace(' ' , '')} + table", first=True
            )
            if not table:
                continue

            rows = table.find("tr")
            j = 1
            while (
                j < len(rows)
                and len(rows[j].find("td")) > 0
                and len(rows[j].find("th")) == 0
            ):
                cells = rows[j].find("td")
                top_10[course][gender][age_group][str(year)][event][j] = cells[
                    5
                ].text
                j += 1

        with open(f"top_10.json", "w") as f:
            json.dump(top_10, f, indent=2)

    return top_10[course][gender][age_group]


def calculate_nqt(course, year, event, top_10):
    if course == "SCY":
        tenth = get_place(year, event, top_10, "10")
        if len(tenth) < 2:
            fifth = get_place(year, event, top_10, "5")
            if len(fifth) < 2:
                return timedelta.max

            conversion_factor = 1.2
            if int(event.split()[0]) >= 200:
                conversion_factor = 1.15

            return calculate_average_time(fifth) * conversion_factor

        conversion_factor = 1.15
        if int(event.split()[0]) >= 200:
            conversion_factor = 1.1

        return calculate_average_time(tenth) * conversion_factor

    elif course == "LCM":
        fifth = get_place(year, event, top_10, "5")
        if len(fifth) < 2:
            return timedelta.max

        conversion_factor = 1.15

        return calculate_average_time(fifth) * conversion_factor


def get_place(year, event, top_10, place):
    times = []
    for i in range(1, 4):
        if str(year - i) not in top_10:
            return times

        if place in top_10[str(year - i)][event]:
            times.append(top_10[str(year - i)][event][place])

    return times


def calculate_average_time(times):
    total = timedelta(0)
    for time in times:
        hours, minutes, seconds = 0, 0, time
        if ":" in seconds:
            minutes, seconds = time.rsplit(":", 1)
            if ":" in minutes:
                hours, minutes = minutes.split(":")

        total += timedelta(
            hours=int(hours), minutes=int(minutes), seconds=float(seconds)
        )

    return total / len(times)


if __name__ == "__main__":
    main()
