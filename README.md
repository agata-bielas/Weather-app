# Weather-app
> ...

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Active API key](#active-api-key)
* [Setup](#setup)

## General info
- ...
- ...

## Technologies
- ...
- ...


## Active API key

Application get data from http://openweathermap.org/api.
To access the data sign up for a free account and confirm your email. 
After that they will sent email with your an API key. 
In this mail you read that the API key will be ready to use after activated. 
The activation takes from two minutes to a couple hours. 
Clik to a link "Example of API call" and refresh it. 
If this link works and you see the JSON format then you konw that the API key has been 
activated otherwise you will see a 401 error that mean the API key hasn't been activated.


## SetUp

First of all read [Active API key](#active-api-key).
Follow along the other parts of setup if you wait for API key activated.

Git clone this repository.

Create a virtual environment to install dependencies in and activate it.
Install all dependencies on your computer using in terminal: 
>(env)$ pip install -r requirements.txt

Note the (env) in front of the prompt. This indicates that this terminal session operates in a virtual environment.


If API key is active you will store our API key in a configuration file.
Create a file called config.ini and write inside:

    [openweathermap]
    api=your_api_key

Where your_api_key repleaca by your active API key.

Now your app is redy to running
> python app.py

Come to the webside address that will appear in the terminal.   