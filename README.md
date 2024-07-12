# Recipe Ingredient Parser

Welcome to the Recipe Ingredient Parser project! This repository is dedicated to extracting and processing ingredient information from recipe data. The goal is to build a robust and comprehensive system that can accurately identify, quantify, and process ingredients from any given recipe.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

This project reads recipe data, processes the ingredient lists, and identifies key elements such as quantities, measurement units, and ingredient names. It leverages natural language processing (NLP) tools to tag parts of the text and extract meaningful data. The data can then be used for further applications such as nutritional analysis, ingredient substitution, and more.

## Features

- **Ingredient Extraction**: Automatically recognizes ingredients and their respective measurements from recipe text.
- **NLP Integration**: Uses the NLTK library to tokenize and tag words, making it easier to identify quantities, measurements, and ingredient names.
- **Data Persistence**: Utilizes MongoDB for storing processed recipe data and tracking ingredient frequencies.
- **Customization and Extensibility**: Modular structure allows easy extension and customization of the parsing and processing logic.

## File Structure

Here is an overview of the main files and directories in this repository:

- `run.py`: Main entry point to run the ingredient extraction process.
- `test.py`: Contains test cases and setup for testing the various components.
- `parser/`: Directory containing the core parsing and processing modules.
  - `cleaner.py`: Handles cleaning and preprocessing of input text.
  - `config.py`: Configuration settings, including database connection details.
  - `data_loader.py`: Loads and processes data from CSV and MongoDB.
  - `db_manager.py`: Manages interactions with MongoDB.
  - `file_loader.py`: Utility functions for loading files.
  - `finder.py`: Contains functions for identifying numbers and keys in text.
  - `languagetools.py`: Utility functions for language processing using NLTK.
  - `matcher.py`: Placeholder for future implementation.
  - `measurements.py`: Extracts and processes measurement data from text.
  - `mongo_collection_stats.py`: Functions for generating statistics from MongoDB collections.
  - `phrase.py`, `sentence.py`, `word_set.py`, `wordlet.py`: Modules for handling phrases, sentences, and words in the context of ingredient parsing.
- `tester.py`: Utility for testing with random recipes from the database.

## Installation

To get started with this project, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/recipe-ingredient-parser.git
    cd recipe-ingredient-parser
    ```

2. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up MongoDB:**
   Make sure MongoDB is installed and running on your machine. Update the `Config` class in `parser/config.py` with your database connection details.

4. **Download NLTK data:**
    ```python
    import nltk
    nltk.download('all')
    ```

## Usage

1. **Running the parser:**
    ```sh
    python run.py
    ```

2. **Testing:**
    ```sh
    python test.py
    ```

The `run.py` script continually fetches random recipes from the MongoDB database, processes their ingredients, and prints the extracted information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

