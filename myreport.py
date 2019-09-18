import argparse
from spl import spl

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Seattle Pet Licenses API QA')
  parser.add_argument('-rdb', action='store_true', help='refresh database')
  parser.add_argument('-q1',  action='store_true', help='answer to Q1')
  parser.add_argument('-q2',  action='store_true', help='answer to Q2')

  args = parser.parse_args()
   

  myReport = spl(dbName='test', 
                 tableName='t', 
                 rowLimit=5000, 
                 srcUrl='data.seattle.gov', 
                 srcDataCode='jguv-t9rb')

  myReport.connectToDB()

  if args.rdb:
    try:
      myReport.refreshDB()
    except Exception as e:
      print("ERROR: Failed to refresh database. Msg: {}".format(e))

  elif args.q1:
    breed = 'Retriever, Golden'
    breedName = ' '.join([x.strip() for x in reversed(breed.split(','))])
    (zip, cnt)=myReport.getMostBreedByZip(breed)

    print("The following zip code has the most {nbreed}. And the total count is {cnt}".format(cnt=cnt, nbreed=breedName))
    print("\t{}".format(','.join(zip)))


  elif args.q2:
    myReport.getCountOfSpeciesPerYear()


  myReport.disconnectFromDB()
