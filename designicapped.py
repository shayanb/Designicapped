from pinata.client import PinterestPinata
from pymongo import MongoClient


from keys import email, username, password, mongoURI

pinata = PinterestPinata(email=email, password=password, username=username)
#pinata.create_board(name='my test board', category='food_drink', description='my first board')


images = pinata.search_pins(query="bedroom")


#print images


def init_db():
    URI = mongoURI
    DBclient = MongoClient(URI)
    print("Connected to %s..." % URI[0:25])
    DB = DBclient.heroku_01lm10c6
    return DB


db = init_db()


def mongodb_write(object, DB = db):

    def write(data):

        #TODO: field verification here

        result = DB.designicapped.save(data)
        # print result
        return result

    return write(object)



def mongodb_readall(DB= db):
    all = DB.designicapped.find({})
    #print ("fetched %s items" %len(all))
    return all
    #print closestBelow[0]




obj = {"test": "test123"}

mongodb_write(obj)

all_saved_items = mongodb_readall()
for item in all_saved_items:
    print item
    item["new_field"] = "new_v2alue"
    mongodb_write(item)




