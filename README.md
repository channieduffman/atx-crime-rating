# ATX Neighborhood Violence Rating API

*This project uses data made accessible by the City of Austin through the Socrata Open Data API (SODA).*

The primary function of the API is to return a numerical breakdown of violent crimes reported in a given Austin zip code within a given timeframe. The crimes are queried by their corresponding UCR (Uniform Crime Reporting) codes. 


## Usage

Requests are made by appending a zip code and cutoff time (given in years ago) as URL parameters.

Example:

    https://domain.com/78704/2 

The above code will search for violent crimes reported in the 78704 zip code within the last two years.

It returns:

    {
        "zip_code": "78704",
        "number_of_years": "2",
        "reported_violent_crime_count": "988",
        "by_category": {
            "murder": "7",
            "rape": "21",
            "aggravated_robbery": "92",
            "aggravated_assault": "827",
            "sexual_assault": "41"
        }
    }


## Definition Violent Crime

The FBI defines violent crime [here](https://ucr.fbi.gov/crime-in-the-u.s/2018/crime-in-the-u.s.-2018/topic-pages/violent-crime#:~:text=Definition,force%20or%20threat%20of%20force.).  

> In the FBI’s Uniform Crime Reporting (UCR) Program, violent crime is composed of four offenses: murder and nonnegligent manslaughter, rape, robbery, and aggravated assault. Violent crimes are defined in the UCR Program as those offenses that involve force or threat of force.

Thus the selection of UCR codes that this API queries correspond to such types of crime. 
