Landing page screenshot

# c150data
![alt text](app/static/imgs/favicon.png)
Web application created with Flask, Bootstrap, SQLAlchemy, and TrainingPeaks API. 

## Table of Contents
* Introduction
* Header 2

## Introduction
Projects aim, what problems the project solves.

## Features
* Current
* Features

## Site
Short description of each page along with screenshot/gif of it's use.

## Project Layout
.
├── app
│   ├── admin
│   │   └── admin.py               -- Flask-Admin site with views to allow db oversight
│   ├── api
│   │   ├── api_requester.py       -- Handles direct calls to TP API
│   │   ├── api_service.py         -- TP API functions to handl large amounts of similar data
│   │   ├── oauth.py      		   -- Gets/Updates access tokens for TP API
│   │   └── urls.py 			   -- Build urls to make API requests
│   ├── data
│   │   └── hours.py 			   -- Holds functions necessary to display hours table 
│   ├── database
│   │   ├── db_filler.py      	   -- DB functions for large batch requests to TP API
│   │   ├── db_functions.py 	   -- Handles basic SQL functions
│   │   ├── db_updater.py 		   -- DB functions for updating database 
│   │   └── sql_statements.py 	   -- Commonly used SQL expressions
│   ├── db_models.py 			   -- Defines DB objects used in app
│   ├── forms
│   │   └── forms.py 			   -- Uses flask_wtf to create forms for app
│   ├── __init__.py 			   -- Initializes app, db, log, etc. 
│   ├── mappers
│   │   ├── athlete_mapper.py 	   -- Handles mapping involving athlete object
│   │   └── workout_mapper.py 	   -- Handles mapping involving workout object
│   ├── routes.py 				   -- Handles all url endpoints - Main driver of app
│   ├── site.db 				   -- SQLite DB
│   ├── static   				   -- Static files for app 
│   │   ├── css
│   │   ├── img
│   │   ├── js
│   │   └── lib
│   └── templates 				   -- Templates for app
├── config.py 					   -- Config file 
├── README.md
└── run.py    					   -- Calls __init__ to initialize package structure

## Technologies
Languages used, libraries, and versions

API:
* TrainingPeaks API
* OAuth2 Authentication 3.0.1
* Authlib 0.11

Web Page:
* Python 3.7
* Bootstrap 4.0.0
* Flask 1.0.3
* Flask-Admin 1.5.3
* Flask-Bcrypt 0.7.1
* Flask-Login 0.4.1
* Flask-Mail 0.9.1
* Flask-Session 0.3.1
* Flask-SQLAlchemy 2.4.0
* Flask-WTF 0.14.2
* Jinja2==2.10.1
* bcrypt 3.1.7
* python-dateutil 2.8.0
* requests 2.22.0
* urllib3 1.25.2
* Werkzeug 0.15.4
* WTForms 2.2.1
* pyOpenSSL 19.0.0

Database: 
* SQLAlchemy 1.3.5
* SQLite

Server Side:
* gunicorn 19.9.0
* NGINX
* Supervisor 
* Linode Server


#### To Do:
* Future
* Features
Website for Columbia Lightweight Rowing

 ## Author Information
 Links to Lukas and I's Github Accounts, which will have our contact information
 ## Contact Information

Authors: Lukas Geiger and Max Amsterdam

This website is meant to store and meaningfully display workout data for all athletes of C150. 
In order to access this site you must be preregistered by an admin. 

The goal of this webpage is to motivate the athletes of C150 to upload all of their training data. Therefore
we display a list of athletes ranked by the percentage of training hours completed to hours assigned. By 
making this data accessible we hope to motivate the athletes to complete all assigned work. Extra is extra. 

In the future we plan on collecting and analyzing all rowing data and displaying it in a way to give our coach 
oversight of the progress of the entire team. 

For a detailed outline of our project please go to this website: https://drive.google.com/file/d/1HHwZq2sI0DBk9f-UMeV8MYHYhMpAWNMN/view

