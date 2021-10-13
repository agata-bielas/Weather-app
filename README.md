# Weather-app
A web application showing current basic weather conditions, simple statistics 
and five-day temperature forecast in Khapalu, Pakistan.

## Table of contents
* [API key activation](#active-api-key)
* [Setup](#setup)

## API key activation

The application loads data from http://openweathermap.org/api.
To access the data, sign up for a free account and confirm your email address.
Then an API key is sent and ready to use after activation 
(at most a couple of hours after receiving the key). 
Click on a link "Example of API call" and refresh the website. 
If you can see the JSON format, the API key has been activated.

## Setup

Read [API key activation](#active-api-key).
While waiting for an API key activation, please follow the steps below.

Git clone this repository.

Create a virtual environment to install dependencies and activate it.
Install all dependencies using 
>(env)$ pip install -r requirements.txt

Note the (env) in front of the prompt. This indicates that this terminal session operates in a virtual environment.


If API key is active you will store our API key in a configuration file.
Create a file called config.ini and write inside:

    [openweathermap]
    api=your_api_key

Where your_api_key should be replaced with an active API key.

Now the Weather-app is ready to run
> python app.py

Please visit the website address that will appear in the terminal.   