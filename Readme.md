Readme
======

Data source: https://data.seattle.gov/Community/Seattle-Pet-Licenses/jguv-t9rb

Required libraries
----------------
1. sqlite3
2. pandas
3. sodapy
4. matplotlib


Usage
-----
~~~python
 $ python myreport.py -h
 usage: myreport.py [-h] [-rdb] [-q1] [-q2]
 
 Seattle Pet Licenses API QA
 
 optional arguments:
   -h, --help  show this help message and exit
   -rdb        refresh database
   -q1         answer to Q1
   -q2         answer to Q2
~~~

Note
----
Run "python myreport.py -rdb" first to create the database and populate the table with fresh data

Example
-------
Get the answer of Q1

~~~python
 $ python myreport.py -q1
 The following zip code has the most Golden Retriever. And the total count is 224
	98115
~~~

Answer to Q3:
-------------
Question #3: How would you extend this job to continuously capture pet license data? A description of your thoughts here are sufficient, you do not need to write this code.


The python script is designed to be able to refresh the entire table with new data with minimal impact. 

This is done by pulling the new datasets into a staging table. Then the production table will be swapped with the staging table via table rename.

In order to capture the data continuously, schedule this python script to run hourly in a crontab. And at every run, the entire table will be refreshed with new data.

Or modified the script and 

1) get the max license_issue_date and count the number of records of that date
2) fetch the data from source and see if the count of the source matches the count in the database
   a) if not, delete all rows from the local database, then fetch the data (of max license_issue_date of the database) from source and insert into the database
   or
   b) if the counts match, fetch the latest data from source, and then insert those into the database

