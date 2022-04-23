# Word to PDF Document / Directory Conversion Application

## Author: 
- Ben Fraser, https://github.com/BenjaminFraser


## Introduction / Overview

A Python application implemented in Flask with LibreOffice backend to convert a large (or small) directory of word and excel documents into a single PDF document. The final PDF is ordered according to the names of the directories in the uploaded zip file, and each directory in-turn is ordered numberically by the files within.


## Expected directory / file upload format

For example, a typical .zip file with the expected directory structure might be the following:

``` 
directory.zip
---- 1_introduction/
	 ---- 1_introduction.docx
	 ---- 2_introduction.docx
	 ---- 3_introduction.docx
---- 2_main_body/
	 ---- 1_main_body.docx
	 ---- 2_main_body.docx
	 ---- 3_main_body.docx
---- 3_conclusions/
	 ---- 1_conclusions.docx
	 ---- 2_conclusions.docx
	 ---- 3_conclusions.docx

```

This would generate a single PDF document with all of the files merged together in the order shown above. This can also be done for just a single zipped directory, or multiple recursive ones with many hundreds of word documents.

The web page has a basic login functionality provided using SQLAlchemy and flask_login. A dummy user script is provided in the repository just for development purposes, with the user and password: 'dummy'. This facilitates basic usage and testing of the application features locally.


## Application examples

Some examples of the interface are shown below.

![example image](examples/app_example_1.jpg?raw=True "Basic page layout of the app.")

![example image 2](examples/app_example_2.jpg?raw=True "Basic page layout.")

![example image 3](examples/app_example_3.jpg?raw=True "Basic page layout.")