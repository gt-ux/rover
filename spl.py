import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sodapy import Socrata

class spl:
  '''
     Initialize object

     param:
       dbName      : sqlite database name
       tableName   : table name to store pet license data
       rowLimit    : number of rows to fetch from api
       srcUrl      : api url
       srcDataCode : data id 
  '''
  def __init__(self, dbName, tableName, rowLimit, srcUrl, srcDataCode):
    self.dbName      = dbName
    self.tableName   = tableName
    self.rowLimit    = rowLimit
    self.srcUrl      = srcUrl
    self.srcDataCode = srcDataCode


  '''
    Grab new data from source and update the table
  '''
  def refreshDB(self):
    self.prepareStagingTable()
    self.loadStagingTable()
    self.swapStgPrdTables()


  '''
    Connect to sqlite database and create a cursor
  '''
  def connectToDB(self):
    self.dbConn = sqlite3.connect('{}.db'.format(self.dbName))
    self.dbCusr = self.dbConn.cursor()


  '''
    Close the database connection
  '''
  def disconnectFromDB(self):
    self.dbConn.close()


  '''
    Check if a table exists in the database
   
    Return
      True/False
  '''
  def tableExists(self, tableName):
    self.dbCusr.execute(f"select count(*) from sqlite_master where tbl_name = '{tableName}'")
    cnt = self.dbCusr.fetchall()[0][0]
    return True if cnt == 1 else False 


  '''
    Drop a table from the database
  '''
  def dropTable(self, tableName):
    self.dbCusr.execute(f"drop table {tableName}")


  '''
    Create staging table to hold source data
  '''
  def prepareStagingTable(self):
    stgTableName = 'stg{}'.format(self.tableName)

    if self.tableExists(stgTableName):
      self.dropTable(stgTableName)

    ddl = '''CREATE TABLE {stgTableName} (
             license_issue_date TIMESTAMP,
  	     license_number TEXT,
             animal_s_name TEXT,
             species TEXT,
             primary_breed TEXT,
             zip_code TEXT,
             secondary_breed TEXT
           )
    '''.format(stgTableName=stgTableName)

    try:
      self.dbCusr.execute(ddl)
    except Exception as e:
      raise Exception('ERROR: Failed to create staging table. MSG:{}'.format(e))

 
  '''
    Load source data to staging table
  '''
  def loadStagingTable(self):
    stgTableName = 'stg{}'.format(self.tableName)

    rowOffset = 0
    rowLimit = self.rowLimit

    try: 
      client = Socrata(self.srcUrl, None)
      results = client.get(self.srcDataCode, limit=rowLimit, offset=rowOffset)
      results_df = pd.DataFrame.from_records(results)

      while len(results_df) > 0:
        results_df.to_sql(name=stgTableName, index=False, if_exists='append', con=self.dbConn, schema=self.dbName)
        rowOffset += rowLimit
        results = client.get(self.srcDataCode, limit=rowLimit, offset=rowOffset)
        results_df = pd.DataFrame.from_records(results)
    except Exception as e:
      raise Exception('ERROR: Failed to load data to staging table. Msg:{}'.format(e))


  '''
    Swap production table with staging table 
  '''
  def swapStgPrdTables(self):
    stgTableName = 'stg{}'.format(self.tableName)
    tmpTableName = 'tmp{}'.format(self.tableName)
    prdTableName = self.tableName

    if self.tableExists(tmpTableName):
      self.dropTable(tmpTableName)


    try:

      if self.tableExists(prdTableName):
        self.dbCusr.execute(f'alter table {prdTableName} rename to {tmpTableName}')

      self.dbCusr.execute(f'alter table {stgTableName} rename to {prdTableName}')
    except Exception as e:
      raise Exception('ERROR: Failed to swap staging with production table. Msg:{}'.format(e))
    

  '''
    Get zip code which has the most Golden Retrievers   

    Return
      List of zip codes which have the most count
  '''
  def getMostBreedByZip(self, breed):
    sql = '''select 
                    zip_code 
                    ,sum(case when (primary_breed = '{breed}' or secondary_breed = '{breed}') then 1 else 0 end) as breed_cnt
             from 
                 {tableName}
             where
                 (primary_breed = '{breed}' or secondary_breed = '{breed}')  
             group by
                 zip_code
          '''.format(breed=breed, tableName=self.tableName)

    self.dbCusr.execute(sql)

    maxZip = []
    maxCnt = 0    
    for (zip, cnt) in self.dbCusr.fetchall():
      if cnt > maxCnt:
        maxCnt = cnt 
        maxZip = [zip]
      elif cnt == maxCnt:
        maxZip.append(zip)

    return maxZip, maxCnt


  def getCountOfSpeciesPerYear(self):
    sql = "select strftime('%Y', license_issue_date) as Year, species, count(*) as count from t group by strftime('%Y', license_issue_date), species"
     
    df  = pd.read_sql(sql, self.dbConn)

    df.groupby(['Year', 'species']).sum().unstack().plot(kind='bar', stacked=True)

    plt.show()
