updated 2024/4/17

# Carscraper

This minor project takes a car site and scrapes it for cars for sale. One can then use the car prices in the past and
present to find the best car to buy compared to the other cars. This is done using ML in sci-kit learn. If we keep
scarping we can also get trends for when different cars will drop in value compared to when they were released.

## Background

I wanted to create a scarping project that could use some of the ML that I have been applying at work. This Opens up for
the possibility as a minor side project.

## Getting started
There is an updated requirements.txt, so:

- Download the rep. 
- Install the requirements file:
```
pip install requirements.txt
```
- and run:
```
Python main.py
```
you will need a data folder where the csv files will go.

- The model can be trained using:
```
Python main.py -t
```
and will result in two Excel files with the best candidates for purchase  

## Still missing:
- SQLite to hold the data.
- More parameters in the model since this was build in 2021 originally and didn't have many electrical cars.

