# arangodb-geonames
Python script to generate JSON from GeoNames for importing into ArangoDB

This is a simple script to download data from geonames.org and export to to JSON files
meant to be imported using `arangoimp`

For example:

    arangoimp --collection cities --type json --file cities.json
    
It's written for use in Python 3 so if you need to use Python 2, you'll have to deal with
unicode and all that jazz.
