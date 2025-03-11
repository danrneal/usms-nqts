# USMS NQTs

This script finds the fastest NQTS in every event since 2008. This helps me set goal times.

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

## Usage

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

Copy and paste the latest NQTs in the the NQTs/ directory.

Then run the script:

```bash
Usage: parser.py
```

## Validator Script

This is an extra script to validate that the NQTs were calculated correctly in a given year. The requirements in requirements.txt are required for this script only.

## License

USMS NQTs is licensed under the [MIT license](https://github.com/danrneal/usms-nqts/blob/master/LICENSE).
