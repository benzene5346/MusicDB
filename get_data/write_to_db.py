import MySQLdb, json, config
from datetime import datetime 

def connect_db():
    """Connect database and return db and cursor"""
    db = MySQLdb.connect(host="localhost",user='root',
                     passwd=config.DB_PASSWD,db="MusicDB")
    cursor = db.cursor()
    return db, cursor

def table_exists(table_name):
    """Check table existence base on table name"""
    db, cursor = connect_db()
    cursor.execute("SELECT * FROM information_schema.tables \
                   WHERE table_name = '%s'" % table_name)
    nrows = int(cursor.rowcount); db.close()
    return False if nrows == 0 else True

def drop_table(table_name):
    db, cursor = connect_db()
    if table_exists(table_name):
        sql = """DROP TABLE %s""" % table_name
        cursor.execute(sql)
    db.close()

def load_json(filename):
    with open('data/' + filename) as fp:
        results = json.load(fp)
    return results

def create_table_artist():
    db, cursor = connect_db()
    sql = """CREATE TABLE artist(
             name CHAR(50) NOT NULL,
             mbid_artist CHAR(50) PRIMARY KEY,
             url CHAR(80),
             listeners INT,
             playcount INT,
             image TEXT)"""
    if not table_exists('artist'):
        cursor.execute(sql)
    db.close()

def create_table_album():
    db, cursor = connect_db()
    sql = """CREATE TABLE album(
             name CHAR(50) NOT NULL,
             artist CHAR(50),
             mbid_album CHAR(50) PRIMARY KEY,
             mbid_artist CHAR(50),
             listeners INT,
             playcount INT,
             image TEXT,
             published TIMESTAMP,
             FOREIGN KEY (mbid_artist) REFERENCES artist(mbid_artist)
             ON DELETE CASCADE ON UPDATE CASCADE)"""
    if not table_exists('album'):
        cursor.execute(sql)
    db.close()

def create_table_track():
    db, cursor = connect_db()
    sql = """CREATE TABLE track(
             name CHAR(50) NOT NULL,
             mbid_track CHAR(50) PRIMARY KEY,
             url CHAR(80),
             artist CHAR(50),
             mbid_artist CHAR(50),
             album CHAR(50),
             mbid_album CHAR(50),
             duration MEDIUMINT,
             listeners INT,
             playcount INT,
             FOREIGN KEY (mbid_album) REFERENCES album(mbid_album)
             ON DELETE CASCADE ON UPDATE CASCADE)"""
    if not table_exists('track'):
        cursor.execute(sql)
    db.close()

def create_table_tag():
    db, cursor = connect_db()
    sql = """CREATE TABLE tag(
          id INT PRIMARY KEY AUTO_INCREMENT,
          name CHAR(50),
          url CHAR(80))"""
    if not table_exists('tag'):
        cursor.execute(sql)
    db.close()

def create_table_track_tag():
    """Junction table between track and tag"""
    db, cursor = connect_db()
    sql = """CREATE TABLE track_tag(
             id INT PRIMARY KEY AUTO_INCREMENT,
             track CHAR(50),
             listeners INT,
             tag CHAR(80))"""
    if not table_exists('track_tag'):
        cursor.execute(sql)
    db.close()

def create_table_comment():
    """
    Comment table, each track can have many comments
    """
    db, cursor = connect_db()
    sql = """CREATE TABLE comment(
             id INT PRIMARY KEY AUTO_INCREMENT,
             content TEXT NOT NULL,
             track CHAR(50),
             FOREIGN KEY (track) REFERENCES track(mbid_track)
             ON DELETE CASCADE ON UPDATE CASCADE)
             """
    if not table_exists('comment'):
        cursor.execute(sql)
    db.close()

def insert_into_artist():
    artists = load_json('artists.json')       
    db, cursor = connect_db()
    sql = """INSERT INTO artist(
           name, mbid_artist, url, listeners, playcount, image)
           VALUES ('%s', '%s', '%s', '%d', '%d', '%s')"""
    for a in artists:
        try:
            tp = (a['name'], a['mbid_artist'], a['url'], int(a['listeners']),
                  int(a['playcount']), a['image'])
            cursor.execute(sql % tp); db.commit()
        except:
            db.rollback()
    db.close()

def insert_into_album():
    albums = load_json('albums.json')
    db, cursor = connect_db()
    sql = """INSERT INTO album(name, artist, mbid_album, mbid_artist, 
             listeners, playcount, image, published)
             VALUES ('%s', '%s', '%s', '%s', '%d', '%d', '%s', '%s')"""
    for a in albums:
        published = datetime.strptime(a['published'],'%d %b %Y, %H:%M')
        try:
            tp = (a['name'],a['artist'],a['mbid_album'],a['mbid_artist'],
                  int(a['listeners']),int(a['playcount']),a['image'],published)
            cursor.execute(sql % tp); db.commit()
        except:
            db.rollback()
    db.close()

def insert_into_track():
    tracks = load_json('tracks.json')
    db, cursor = connect_db()
    sql = """INSERT INTO track(name, mbid_track, url, artist, mbid_artist,
             album, mbid_album, duration, listeners, playcount)
             VALUES('%s','%s','%s','%s','%s','%s','%s','%d','%d','%d')"""
    for t in tracks:
        try:
            tp = (t['name'],t['mbid_track'],t['url'],t['artist'],t['mbid_artist'],t['album'],
                  t['mbid_album'],int(t['duration']),int(t['listeners']),int(t['playcount']))
            cursor.execute(sql % tp); db.commit()
        except:
            db.rollback()
    db.close()

def insert_into_tag():
    with open('data/tags_list.txt','r') as fp:
        tags = [(x.split(',')[0],x.split(',')[1].strip()) for x in fp.readlines()]
    db, cursor = connect_db()
    sql = """INSERT INTO tag(name, url) VALUES('%s','%s')"""
    for t in tags:
        try:
            cursor.execute(sql % t); db.commit()
        except:
            db.rollback()
    db.close()

def insert_into_track_tag():
    tracks = load_json('tracks.json')
    db, cursor = connect_db()
    sql = """INSERT INTO track_tag(track, listeners, tag) VALUES('%s','%d','%s')"""
    for t in tracks:
        for tag in t['tags']:
            try:
                tp = (t['name'],int(t['playcount']), tag['name'])
                cursor.execute(sql % tp); db.commit()
            except:
                db.rollback()
    db.close()


def insert_into_comment():
    db, cursor = connect_db()
    sql = """INSERT INTO comment(content,track)
             VALUES ('%s','%s')"""
    comment1 = ('good','24cfd355-220e-4c1f-b8e3-5adf0abbb76f')
    comment2 = ('better','24cfd355-220e-4c1f-b8e3-5adf0abbb76f')
    comment3 = ('great','24cfd355-220e-4c1f-b8e3-5adf0abbb76f')
    cursor.execute(sql % comment1); db.commit()
    cursor.execute(sql % comment2); db.commit()
    cursor.execute(sql % comment3); db.commit()
    db.close()

if __name__ == '__main__':
    drop_table('comment')
    drop_table('track')
    drop_table('album')
    drop_table('artist')
    drop_table('tag')
    drop_table('track_tag')

    create_table_artist()
    insert_into_artist()
    
    create_table_album()
    insert_into_album()
   
    create_table_track()
    insert_into_track()

    create_table_comment()
    insert_into_comment()
   
    create_table_tag()
    insert_into_tag()

    create_table_track_tag()
    insert_into_track_tag()
