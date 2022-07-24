# seenons-assignment

## This repository contains code for the Seenons integration assignment.

The main file integration.py contains all API requests to combine data between the Seenons API and Huisvuilkalendar API data.
It takes a postal code, house number and optionally weekdays as inputs and returns the available waste streams and on which dates they are available. If weekdays are passed as arguments, the output dates will be limited to only the weekdays provided by the user.

## Usage:

`python3 integration.py -p <POSTCODE> -n <HOUSENUMBER> [-wd <WEEKDAY> [<WEEKDAY> ...]]`

POSTCODE: Must contain 2 letters at the end without space (e.g. 2512HE)
HOUSENUMBER: Must be an integer (e.g. 68)
If POSTCODE and HOUSENUMBER do not form a valid address, the program will exit.
WEEKDAY must be one of the following: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
If a weekday is misspelled, it will just be ignored.

## Returns:

Available waste streams for given address (Type and ID).
Available dates for each waste stream.