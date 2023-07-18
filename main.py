"""Country Population guessing game."""

import json
import locale
import sqlite3
import os

from dataclasses import dataclass
from typing import Any, List, Union
from random import choice, randint

import requests

locale.setlocale(locale.LC_ALL, '')

JSON_FILE: str = "country_information.json"
COUNTRY_INFO_DB: str = "country_information.db"

@dataclass
class Country:
    """A country."""
    name: str
    population: int

    def __str__(self) -> str:
        return f"{self.name} has a population of {self.population:n}"

@dataclass
class UserScore:
    """A user's score."""
    username: str
    score: int

    def __str__(self) -> str:
        return f"{self.username} scored {self.score:n}"

def make_country_request(endpoint: str) -> Any:
    """Make a request to the endpoint.

    Args:
        endpoint (str): The endpoint.

    Returns:
        Any: The country information. JSON.
    """
    with requests.get(endpoint) as request:
        # write json to file
        with open(JSON_FILE, "w", encoding = "utf-8") as file:
            file.write(request.text)
        return request.json() if request.status_code == 200 else None



def get_country_information(endpoint: str) -> Any:
    """Get the country information.

    Args:
        endpoint (str): The endpoint.

    Returns:
        Any: The country information. JSON.
    """
    if (
        not os.path.exists(JSON_FILE) or
        os.path.getmtime(JSON_FILE) < (os.path.getmtime(__file__) - 86400)
    ):
        return make_country_request(endpoint)

    # otherwise, read from file
    with open(JSON_FILE, "r", encoding = "utf-8") as file:
        return json.load(file)


def get_country_names_and_populations_info(country_information: Any) -> List[Country]:
    """Get the country name and population from the country information.

    Args:
        country_information (Any): The country information.

    Returns:
        List[Country]: The country name and population.
    """
    countries: List[Country] = []

    for country in country_information:
        name: str = country["name"]["common"]
        population: int = country["population"]

        countries.append(Country(name, population))

    return countries

def set_countries(
        country_1: Country,
        country_2: Country,
        names_and_populations: List[Country]
    ) -> List[Country]:
    """Set the countries.

    Args:
        country_1 (Country): The first country.
        country_2 (Country): The second country.
        names_and_populations (List[Country]): The list of countries.

    Returns:
        List[Country]: Two countries.
    """
    if country_1 is None:
        country_1 = choice(names_and_populations)

    if country_2 is None:
        country_2 = choice(names_and_populations)

    if randint(0, 1) == 0:
        country_1 = choice(names_and_populations)
    else:
        country_2 = choice(names_and_populations)

    if country_1 == country_2:
        return set_countries(country_1, country_2, names_and_populations)

    return [country_1, country_2]

def check_user_guess(country1: Country, country2: Country, user_guess: str) -> bool:
    """Check the user guess.

    Args:
        country1 (Country): The first country.
        country2 (Country): The second country.
        user_guess (str): The user's guess.

    Returns:
        bool: True if the user guess is correct, False otherwise.
    """
    if (
        user_guess == "1"
        and country1.population >= country2.population
        or user_guess != "1"
        and country2.population >= country1.population
        ):
        return True
    return False

def game_loop(names_and_populations: List[Country]) -> int:
    """The game loop.

    Args:
        names_and_populations -- description
    Returns:
        int: The score.
    """

    country1: Union[Country, None] = None
    country2: Union[Country, None] = None

    score: int = 0

    while True:

        [
            country1,
            country2
        ] = set_countries(country1, country2, names_and_populations)


        user_guess: str = ""

        while user_guess not in ["1", "2"]:
            user_guess = input(
            f"Which country has the largest population?\n1. {country1.name}\n2. {country2.name}\n"
            )

        print(country1)
        print(country2)

        if check_user_guess(country1, country2, user_guess):
            score += 1
            print("Correct!")
        else:
            print("Incorrect!")
            break

        # ask the user if they want to continue
        play_again: str = ""

        while play_again not in ["y", "n"]:
            play_again = input("Would you like to continue? (y/n) ").lower()

        if play_again == "n":
            break

        print(f"Your current score is {score}.")

    print(f"Your score was {score}.")

    return score

def get_user_name() -> str:
    """Get the user's name.

    Returns:
        str: The user's name.
    """

    username: str = ""

    while len(username) != 3:
        username = input("Enter your username (3 characters): ").upper()

    return username

def create_database_file() -> None:
    """Create the database file."""
    with sqlite3.connect(COUNTRY_INFO_DB) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS country_information (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                score INTEGER NOT NULL
            )
            """
        )

def save_score(username: str, score: int) -> None:
    """Save the score.

    Args:
        username (str): The user's name.
        score (int): The user's score.
    """
    with sqlite3.connect(COUNTRY_INFO_DB) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO country_information (username, score)
            VALUES (?, ?)
            """,
            (username, score)
        )

def get_top_scores(amount: int) -> List[UserScore]:
    """Get the top n scores.

    Args:
        n (int): The number of scores to get.

    Returns:
        List[tuple]: The top n scores.
    """
    with sqlite3.connect(COUNTRY_INFO_DB) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT username, score
            FROM country_information
            ORDER BY score DESC
            LIMIT ?
            """,
            (amount,)
        )

        return [UserScore(username, int(score)) for username, score in cursor.fetchall()]

def main():
    """The main function."""
    endpoint: str = "https://restcountries.com/v3.1/independent?status=true"

    country_information: Any = get_country_information(endpoint)

    names_and_populations: List[Country] = get_country_names_and_populations_info(
        country_information
    )

    score: int = game_loop(names_and_populations)
    username: str = get_user_name()

    create_database_file()
    save_score(username, score)

    scores: List[UserScore] = get_top_scores(5)

    for score in scores:
        print(score)


if __name__ == '__main__':
    main()
