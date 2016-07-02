## StreetEasy Apartment Finder

Produce a table of available apartments given desired parameters. 

### Command Line Arguments

Command line arguments should be given as strings. 

`--outfile`

Required. Name of CSV file to output to working directory


`--area`

Required. Code for neighborhood. List multiple codes separated by commas. Run a search in your browser to find codes. 


`--min_price`

Default is none. Minimum rent per month.


`--max_price`

Required. Maximum rent per month. 


`--beds`

Default is any. Number of bedrooms. Examples: =1, <=1, >=1.


`--no_fee`

Default is no preference. "1" restricts to only no fee apartments. 


### Columns in Output

**Link**

The link to the apartment listing. 


**Date_avail**

The date the apartment is available. Some are "Available Now" or not provided. 


**Rent**

The monthly rent.


**Listingdesc**

The listing description of the apartment. Usually includes unit type (rental, condo, co-op), neighborhood, rent, number of bedrooms. Sometimes includes square feet. 


**Amenities**

List of apartment amenities, if available. 


**Record_added**

The date the recorded was added to the text file. 
