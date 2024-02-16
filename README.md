# ATX Neighborhood Violence Rating API

*This project uses data made accessible by the City of Austin through the Socrata Open Data API (SODA).*

The primary function of the API is to return a numerical breakdown of violent crimes reported in a given Austin zip code in a given timeframe. The crimes are queried by their corresponding UCR (Uniform Crime Reporting) codes. 


## Usage

Requests are made by appending a zip code and cutoff time (given in years ago) as URL parameters.

Example:

> `domain.com/78704/2` 

The above code will search for violent crimes reported in the 78704 zip code within the last two years.

It returns:


> ```
[
    {
        "murder": "6"
    },
    {
        "rape": "21"
    },
    {
        "agg_robbery": "95"
    },
    {
        "agg_assault": "835"
    },
    {
        "sexual_assault": "40"
    },
    {
        "kidnapping": "0"
    },
    {
        "trafficking": "0"
    }
]
```
