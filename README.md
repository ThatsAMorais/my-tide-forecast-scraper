# Tide Forecast Scraper

A Python script for scraping daylight low-tides from https://www.tide-forecast.com/ to help with planning trips to 
the tide pools!

# Installation from source

1. git clone the repo: https://bitbucket.org/ThatsAMorais/tide-forecast-scraper

1. Some setup:
   ``` 
   cd /tide-forecast-scraper`
   pip install -r requirements.txt`
   chmod +x tide-scraper.py
   ```

# Running the application

The scraper requires only a filename with a list of valid locations. An example of one is included in the project, `basic-input.txt`. Try creating your own!

```
./tide-scraper.py basic-input.txt
```

# Output

The output is JSON that looks like the following example:

```json
{
    "Providence-Rhode-Island": {
        "low-tides": {
            "3:37 PM": "-0.76 feet",
            "4:17 PM": "-0.50 feet",
            "4:56 PM": "-0.19 feet",
            "7:04 AM": "0.87 feet",
            "9:53 AM": "1.14 feet",
            "8:04 AM": "0.99 feet",
            "10:52 AM": "1.11 feet",
            "9:04 AM": "0.96 feet",
            "11:41 AM": "1.04 feet",
            "9:56 AM": "0.80 feet",
            "12:18 PM": "0.95 feet",
            "10:44 AM": "0.58 feet",
            "11:29 AM": "0.34 feet",
            "12:14 PM": "0.10 feet",
            "12:58 PM": "-0.12 feet",
            "1:41 PM": "-0.30 feet",
            "2:22 PM": "-0.44 feet",
            "3:02 PM": "-0.52 feet",
            "3:43 PM": "-0.53 feet",
            "4:25 PM": "-0.46 feet",
            "5:11 PM": "-0.33 feet",
            "6:45 AM": "0.11 feet",
            "7:54 AM": "0.17 feet",
            "9:03 AM": "0.07 feet",
            "10:08 AM": "-0.14 feet",
            "11:08 AM": "-0.38 feet",
            "12:05 PM": "-0.59 feet",
            "12:57 PM": "-0.74 feet",
            "1:45 PM": "-0.81 feet",
            "2:27 PM": "-0.78 feet",
            "3:06 PM": "-0.66 feet",
            "3:44 PM": "-0.45 feet"
        }
    },
    ...
```

low-tides are organized by a location key, which contains a low-tides block containing 12hr-times as keys to height values.


# The Approach

The process by which this data is scraped in a nutshell entails requesting the page for the given location, locating the tide table within it, and sequentially reading the rows of the table, managing the daytime state and recording low-tides for the final output

## LXML

Being new to web-scraping, this is a library that enabled me to traverse an HTML response in a straight-forward manner while gaining the necessary understanding of successfully parsing the data.

## Requesting the Tide Table Page for a Location

Understanding how the desired data was served by the page was important because each representation may entail different caveats. The "tides/latest" page for a given location displayed the needed data with 3 advantages to other pages.
  1. predictable to parse
  1. plenty of days worth
  1. easily able to track daylight low-tides with a finite state machine

The tide table page does have one caveat in that some locations will contain the state name, while others are merely the location's name. For example, Huntington Beach, California is simply `../Huntington-Beach/...`, but Providence, Rhode Island is `../Providence-Rhode-Island/..`. I added a special case for this, but if that fails the location will be skipped.

## Parsing the Table

The tide table contains a set of events: 
 * sunrise
 * moonrise
 * sunset
 * low-tide
 * high-tide

To read all of the daylight low-tides I walk through each row,
determining what event it represents. Walking through rows is simply an xpath on all `tr` in the `td` of the table:
 * sunrise: set `daylight` = `True`
 * sunset: set `daylight` = `False`
 * When `daylight` is `False`, ignore the current `tr` iteration
 * low-tide: (plus, `daylight = True`): record the low-tide's time and height in feet
 * high-tide, moonrise are ignored

 By monitoring for when it is daylight, one does not have to parse the daytime low-tides from the full set of low-tides. Determining sunset for a given region can be tricky, but the table handles the chronology for us.

 # Future Work

 This application could be extended to do more.
  * scrape more data from the sites per location
  * organize data differently or support different output formats, configurable via command arguments. 
  * support more queries
     * specific dates
     * low-tides-by-datetime-range without specifying location
