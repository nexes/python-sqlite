"""Playing around with sqlite3. This does nothing but play around with sqlite through python"""

import time
import sqlite3
from os.path import isfile
from os import remove

DATABASE_FILE = "/Users/jberria/DBs/test.db"


def create_users_table(cursor):
    """TODO"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            value REAL
        )
    ''')

def create_tweet_table(cursor):
    """TODO"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            tweetid INTEGER PRIMARY KEY NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            author INTEGER NOT NULL,
            FOREIGN KEY(author) REFERENCES users(userid)
        )
    ''')

def insert_into_tweets(cursor, message, username):
    """get the userid from the user making the tweet, this will be the foreign key
        insert the message for the user sending it.
    """

    cursor.execute('SELECT userid FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    timestamp = time.strftime("%X %p %x")
    if row is None:
        return

    try:
        cursor.execute('''
            INSERT INTO tweets (message, timestamp, author)
            VALUES (?,?,?)
        ''', (message, timestamp, row[0]))
    except sqlite3.IntegrityError as e:
        print('Integrity Error: {}'.format(e.message))

def insert_into_users(cursor, username, password):
    """Insert user data into the user table"""

    timestamp = time.strftime("%X %p %x")

    try:
        cursor.execute('''
            INSERT INTO users (username, password, timestamp, value)
            VALUES (?, ?, ?, ?)
        ''', (username, password, timestamp, 23424.234)) #made up value data
    except sqlite3.Error as e:
        print('Insert error into the user table: {}'.format(e))

def delete_from_user(cursor, username):
    """first delete the tweets of the user then the user. We use the userid from the user table
        as the foreign key to the tweets table
    """

    cursor.execute('''
        SELECT userid FROM users WHERE username = ?
    ''', (username,))

    row = cursor.fetchone()
    if row:
        try:
            cursor.execute('''
                DELETE FROM tweets WHERE author = ?
            ''', (row[0],))
            cursor.execute('''
                DELETE FROM users WHERE username = ?
            ''', (username, ))
        except sqlite3.Error as e:
            print('Error deleting from user: {}'.format(e))

def find_user(cursor, username=None, password=None):
    """Lets find the user from the user table. Search by username or password or both"""

    if username and password:
        cursor.execute('''
            SELECT username, password, timestamp FROM users
            WHERE username = ? AND password = ?
        ''', (username, password))

    elif username and not password:
        cursor.execute('''
            SELECT username, password, timestamp FROM users
            WHERE username = ?;
        ''', (username,))

    elif password and not username:
        cursor.execute('''
            SELECT username, password, timestamp FROM users
            WHERE password = ?;
        ''', (password,))

    for row in cursor.fetchall():
        #just print the tuple
        print(row)

def print_user_tweets(cursor, username):
    """Print the user and tweet data from both tables using INNER JOIN"""

    cursor.execute('SELECT userid FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row is None:
        return

    cursor.execute('''
        SELECT users.username, tweets.timestamp, tweets.message FROM users
        JOIN tweets ON users.username = ? AND tweets.author = ?
    ''', (username, row[0]))

    for row in cursor.fetchall():
        #just print the tuple
        print(row)
    print('\n')

def main():
    """This doesn't do anything interesting. Just playing around with sqlite through python,
        a mock tweet/message database
    """

    #delete the database everytime so we can recreate it. I don't know why, just cause.
    if isfile(DATABASE_FILE):
        remove(DATABASE_FILE)

    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    # lets make sure foreign keys are being enforced.
    cur.execute('PRAGMA foreign_keys=ON')
    conn.commit()

    create_users_table(cur)
    insert_into_users(cur, 'jberria', '100234')
    insert_into_users(cur, 'bunnyss', 'password')
    insert_into_users(cur, 'sallyw', '123455six')
    insert_into_users(cur, 'dbuser', 'sekret33@')
    conn.commit()

    create_tweet_table(cur)
    insert_into_tweets(cur, "what is up", 'jberria')
    insert_into_tweets(cur, "there is a banana", 'sallyw')
    insert_into_tweets(cur, "oh you know what yeah", 'sallyw')
    insert_into_tweets(cur, "now that you see 3.4545", 'jberria')
    insert_into_tweets(cur, "3.14 is my favorite desert", 'dbuser')
    insert_into_tweets(cur, "what ever man I love you typescript python", 'bunnyss')
    conn.commit()

    find_user(cur, username='jberria')
    find_user(cur, username='sallyw', password="123455six")
    find_user(cur, username='notThere')
    find_user(cur, password='sekret33@')

    print_user_tweets(cur, 'jberria')
    print_user_tweets(cur, 'bunnyss')
    print_user_tweets(cur, 'sallyw')
    print_user_tweets(cur, 'dbuser')

    delete_from_user(cur, 'sallyw')
    conn.commit()

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
