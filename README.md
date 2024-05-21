# Country Population Guessing Game

## Overview

This Python script provides an interactive guessing game where players attempt to determine which of two randomly selected countries has a larger population. The game leverages data fetched from a public API and supports score tracking via a local SQLite database.

## Features

- Fetches up-to-date country information using RESTful API requests.
- Players can guess which country among a pair has the higher population.
- Scores are tracked and stored locally, with functionality to display the top scores.
- Automated database management to maintain and limit the number of stored scores.

## Functionality

- Country Data Fetching: Data is fetched from the REST Countries API and stored locally to minimize redundant network requests.
- Game Loop: Players continue guessing until they choose to stop or make an incorrect guess.
- Score Tracking: Scores are saved to a local SQLite database, and the top scores are displayed at the end of the game session.
