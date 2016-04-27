#!/usr/bin/python




###############################################################################
## IMPORT                                                                    ##
###############################################################################
import mysql.connector;
import mysql;





###############################################################################
## DEFINITION                                                                ##
###############################################################################




###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Database(object):

    """
    Class that handle the mysql database.
    ---------------------------------------------------------------------------
    __db_connect == perform database connection.

    insert_query == perform an insert in the database.
    delete_query == perform a delete in the database.
    select_query == performe a select in the database.
    update_query == perform an update (in record) in the database.
    """

    ###########################################################################
    ## DEFINITION                                                           ##
    ###########################################################################
    __dbConnection = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    def __init__(self, dbDictionary):

        dhost = dbDictionary['host'];
        duser = dbDictionary['user'];
        dpass = dbDictionary['pass'];
        dname = dbDictionary['base'];

        self.__dbConnection = self.__db_connect(dhost, duser, dpass, dname);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: perform an insert in the database.
    ## -----------------------------------------------------------------------
    ## @PARAM query == the request.
    ## @PARAM value == value send together with the request.
    ## 
    def insert_query(self, query, value):

        try:
            cursor = self.__dbConnection.cursor();
            cursor.execute(query, value);
            self.__dbConnection.commit();

            cursor.close();

        except mysql.connector.Error as err:
            print(err);

        return 1;


    ##
    ## BRIEF: performe a select in the database.
    ## -----------------------------------------------------------------------
    ## @PARAM query == the request.
    ## 
    def select_query(self, query):
        entry = [];

        try:
            cursor = self.__dbConnection.cursor();
            cursor.execute(query);
            for row in cursor:
                entry.append(row);

            cursor.close();

        except mysql.connector.Error as err:
            print(err);

        return entry;


    ##
    ## BRIEF: perform a delete in the database.
    ## -----------------------------------------------------------------------
    ## @PARAM query == the request.
    ## 
    def delete_query(self, query):
        try:
            cursor = self.__dbConnection.cursor();

            cursor.execute(query);
            self.__dbConnection.commit();
            cursor.close();

        except mysql.connector.Error as err:
            print(err);

        return 1;


    ##
    ## BRIEF: perform an update (in record) in the database.
    ## -----------------------------------------------------------------------
    ## @PARAM query == the request.
    ## @PARAM value == value to update the registry.
    ## 
    def update_query(self, query, value=()):
        try:
            cursor = self.__dbConnection.cursor();
            cursor.execute(query, value);
            self.__dbConnection.commit();

            cursor.close();

        except mysql.connector.Error as err:
            print(err);

        return 1;


    ###########################################################################
    ## PRIVATE METHODS                                                       ##
    ###########################################################################
    ##
    ## DESCRICAO: perform database connection.
    ## ------------------------------------------------------------------------
    ## @PARAM dbHost == host where database is installed.
    ## @PARAM dbUser == database access user.
    ## @PARAM dbPass == database access password.
    ## @PARAM dbName == database name.
    ##
    def __db_connect(self, dbHost, dbUser, dbPass, dbName):

        dbData = {
           'user':             dbUser,
           'password':         dbPass,
           'host':             dbHost,
           'database':         dbName,
           'raise_on_warnings': True,
        }

        ## Perform the connection to the dbase. It uses data from db dictionary.
        try:
            connection = mysql.connector.connect(**dbData);

        ## Case is not possible to perform the db connection, handles the error.
        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password");
                return None;

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist");
                return None;

            else:
                print(err);
                return None;

        return connection;

## END.

