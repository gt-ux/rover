Readme
======

Required library
----------------
1. sodapy
2. matplotlib


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

