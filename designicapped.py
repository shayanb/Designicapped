from pinata.client import PinterestPinata
from pymongo import MongoClient


from keys import email, username, password, mongoURI




def get_pins(keyword = None):
    pinata = PinterestPinata(email=email, password=password, username=username)
    # pinata.create_board(name='my test board', category='food_drink', description='my first board')
    images = pinata.search_pins(query=keyword)
    return images


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
        return result

    return write(object)



def mongodb_readall(DB= db):
    all = DB.designicapped.find({})
    #print ("fetched %s items" %len(all))
    return all
    #print closestBelow[0]


def fetch_images_and_save_to_db(keyword = "bedroom"):
    pins = get_pins(keyword=keyword)
    for pin in pins:
        mongodb_write(pin)


def update_db_example():
    all_saved_items = mongodb_readall()
    for item in all_saved_items:
        print item
        item["new_field"] = "new_v2alue"
        mongodb_write(item)



fetch_images_and_save_to_db()
