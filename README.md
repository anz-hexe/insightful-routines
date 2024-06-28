# insightful-routines

## Project structure

insightful_routines/content
example of photo angles expected from the user

insightful_routines/handlers
handlers for all activities that are tracked

insightful_routines/keyboards
repetitive keyboard

insightful_routines/models
Files containing definitions of data models associated with users.

insightful_routines/utils/face_position.py
This file contains the logic to analyze and determine the facial pose in user photos.

insightful_routines/config.py
manage .env file settings

insightful_routines/settings.py
This is a file that initializes the folder in which the database and saved photos from the user will be stored

insightful_routines/main.py
This is the main bot file that initializes the bot and connects routers to handle various commands and requests from users.

Dockerfile
This file stores container Docker settings

docker-compose.yaml: Docker Compose configuration file that defines how to run a project in a Docker container.

poetry.lock: this is a file that is used by the Poetry dependency manager to capture the exact versions of all the project's dependencies and subdependencies

pyproject.toml: Configuration file for managing project dependencies and installation with Poetry.

## Installation

Follow these steps to install and run the project:

1. Install Docker
2. Create a project folder
3. Download files
```Dockerfile```
```docker-compose.yml```
4. Create a .env file
5. Create a new bot in Telegram
6. Copy the API to the .env file
7. Open a command line and run the command
```
docker-compose up
```


## Usage

Once the bot is launched, users can interact with it to track various aspects of their lives. Below are the main features that the bot provides:

User Onboarding: Supports the onboarding process for new users and provides information on how to use the bot.

Morning and evening skin care processing: Allows you to track morning and evening skin care, such as the use of cosmetics.

Nutrition Tracking: Includes tracking the consumption of specific ingredients during breakfast, lunch and dinner.

Beverage Tracking: The bot allows you to track your consumption of various types of drinks including hot drinks, milk drinks and others.

Snack Tracking: Allows the user to track snacks throughout the day.

Stress Tracking: Allows the user to track stress levels throughout the day.

Supplement Tracking: Allows the user to track their supplement and vitamin intake.

Workout Tracking: Allows the user to track physical activity location and workout.

Water Balance Tracking: Allows the user to track their water intake throughout the day.

Acne Tracking: Allows the user to track acne. 

Processing facial photos: The bot can save photos of the user's face for further analysis based on the received data.

Reports: The bot can generate a report based on the tracked data for further data analysis.
