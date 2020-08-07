#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

# Modified by Sanha Lee at SNU Software Platform Lab for
# SWPP fall 2018 lecture.

import codecs
import sys
import re
import os

"""Baby Names exercise
Implement the babyname parser class that parses the popular names and their ranks from an html file.
1) At first, you need to implement a decorator that checks whether the html file exists or not.
2) Also, the parser should extract the tuples of (rank, male-name, female-name) from the file by using regex. 
   For writing regex, it's nice to include a copy of the target text for inspiration.
3) Finally, you need to implement the parse(self, parsing_lambda) method that parses the extracted tuples
   with the given lambda and return the list of processed results.
Here's what the html looks like in the baby.html files:
    ...
    <h3 align="center">Popularity in 1990</h3>
    ....
    <tr align="right"><td>1</td><td>Michael</td><td>Jessica</td>
    <tr align="right"><td>2</td><td>Christopher</td><td>Ashley</td>
    <tr align="right"><td>3</td><td>Matthew</td><td>Brittany</td>
    ...
"""


class BabynameFileNotFoundException(Exception):
    """
    A custom exception for the cases that the babyname file does not exist.
    """
    pass


def check_filename_existence(func):
    """
    A decorator that catches the non-exiting filename argument and raises a custom `BabynameFileNotFoundException`.
    Args:
        func: The function to decorate.
    Raises:
        BabynameFileNotFoundException: if there is no such file named as the first argument of the function to decorate.
    """
    def file_check(temp, filename):
        if not os.path.exists(filename):
            exception_string = "No such babyname file or directory: " + filename
            raise BabynameFileNotFoundException(exception_string)
            return
        return func(temp, filename)
    return file_check


class BabynameParser:

    @check_filename_existence
    def __init__(self, filename):
        """
        Given a file name for baby.html, extracts the year of the file and
        a list of the (rank, male-name, female-name) tuples from the file by using regex.
        [('1', 'Michael', 'Jessica'), ('2', 'Christopher', 'Ashley'), ....]
        Args:
            filename: The filename to parse.
        """

        text = codecs.open(filename, 'r').read()
        # Testing if the text works well (DEBUG USAGE):
        # print(text)

        # Could process the file line-by-line, but regex on the whole text at once is even easier.

        # The year extracting code is provided. Implement the tuple extracting code by using this.
        year_match = re.search(r'Popularity\sin\s(\d{4})', text)
        if not year_match:
            # We didn't find a year, so we'll exit with an error message.
            sys.stderr.write('Couldn\'t find the year!\n')
            sys.exit(1)
        self.year = year_match.group(1)

        
        # Extract all the data tuples with a findall()
        # each tuple is: (rank, male-name, female-name

        # Testing if the rank_name_tuples_search works well (DEBUG USAGE):
        # rank_name_tuples_search = re.findall(r'<td>(\d{1,})</td><td>([a-zA-Z]{2,})</td><td>([a-zA-Z]{2,})</td>', text)
        # print(rank_name_tuples_search)
        # print("Type:" + str(type(rank_name_tuples_search)))
        # print("Element type:" + str(type(rank_name_tuples_search[0])))

        self.rank_to_names_tuples = re.findall(r'<td>(\d{1,})</td><td>([a-zA-Z]{2,})</td><td>([a-zA-Z]{2,})</td>', text)  
        # TODO: Extract the list of rank to names tuples. <-- I DON'T GET WHAT THIS MEANS, NEED HELP. ALSO, THE ABOVE MAKES IT INTO LIST OF TUPLES ANYWAYS...

    def parse(self, parsing_lambda):
        """
        Collects a list of babynames parsed from the (rank, male-name, female-name) tuples.
        The list must contains all results processed with the given lambda.
        Args:
            parsing_lambda: The parsing lambda.
                            It must process an single (string, string, string) tuple and return something.
        Returns:
            The list of parsed babynames.
        """
        # TODO: Implement this method.