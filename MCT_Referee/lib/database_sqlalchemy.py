#!/usr/bin/python








__all__ = ['MCT_Database_SQLAlchemy', 'Request', 'Player', 'Vm', 'Status', 'Threshold']








###############################################################################
## IMPORT                                                                    ##
###############################################################################
from sqlalchemy                 import *;
from sqlalchemy.ext.declarative import declarative_base;
from sqlalchemy.orm             import relation, sessionmaker, mapper;
from sqlalchemy.dialects.mysql  import *;







###############################################################################
## DEFINITION                                                                ##
###############################################################################
Base = declarative_base();







###############################################################################
## CLASSES                                                                   ##
###############################################################################
## Used by MCT_Dispatch.
class Request(Base):

    """
    Class Request:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'REQUEST';

    id                 = Column(INT        , nullable=False, primary_key=True);
    player_id          = Column(VARCHAR(45), nullable=False);
    request_id         = Column(VARCHAR(45), nullable=False);
    action             = Column(INT        , nullable=True);
    timestamp_received = Column(TIMESTAMP  , nullable=True);
    timestamp_finished = Column(TIMESTAMP  , nullable=True);
    status             = Column(INT        , nullable=True , default=0 );

## END CLASS.

    






class Threshold(Base):

    """
    Class Threshold:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'THRESHOLD';

    division = Column(INT  , nullable=False, primary_key=True);
    botton   = Column(FLOAT, nullable=True , default=0.0);
    top      = Column(FLOAT, nullable=True , default=0.0);

## END CLASS.








## Used by MCT_Referee|MCT_Division.
class Vm(Base):

    """
    Class Vm:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'VM';

    id                 = Column(INT        , nullable=False, primary_key=True);
    origin_add         = Column(VARCHAR(45), nullable=False);
    origin_id          = Column(VARCHAR(45), nullable=False);
    origin_name        = Column(VARCHAR(45), nullable=False);
    destiny_add        = Column(VARCHAR(45), nullable=False);
    destiny_name       = Column(VARCHAR(45), nullable=False);
    destiny_id         = Column(VARCHAR(45), nullable=False);
    status             = Column(TINYINT(1) , nullable=False);
    has_resources      = Column(TINYINT(1) , nullable=False);
    vcpus              = Column(INT        , nullable=False, default=0);
    mem                = Column(BIGINT     , nullable=False, default=0);
    disk               = Column(BIGINT     , nullable=False, default=0);
    timestamp_received = Column(TIMESTAMP  , nullable=True);
    timestamp_finished = Column(TIMESTAMP  , nullable=True);

## END CLASS.








## Used by MCT_Dispatch|MCT_Register.
class Player(Base):

    """
    Class Player:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'PLAYER';

    id            = Column(INT        , nullable=False, primary_key=True);
    name          = Column(VARCHAR(45), nullable=False); 
    address       = Column(VARCHAR(45), nullable=False); 
    division      = Column(INT        , nullable=False);
    score         = Column(FLOAT      , nullable=True , default=0.0);
    history       = Column(INT        , nullable=True , default=0  );
    fairness      = Column(FLOAT      , nullable=True , default=0.0);
    accepts       = Column(INT        , nullable=True , default=0  ); 
    rejects       = Column(INT        , nullable=True , default=0  );
    running       = Column(INT        , nullable=True , default=0  );
    finished      = Column(INT        , nullable=True , default=0  );
    problem_del   = Column(INT        , nullable=True , default=0  );
    vcpus         = Column(INT        , nullable=True , default=0  );
    vcpus_used    = Column(INT        , nullable=True , default=0  );
    memory        = Column(BIGINT(20) , nullable=True , default=0  );
    memory_used   = Column(BIGINT(20) , nullable=True , default=0  );
    local_gb      = Column(BIGINT(20) , nullable=True , default=0  );
    local_gb_used = Column(BIGINT(20) , nullable=True , default=0  );
    max_instance  = Column(INT        , nullable=True , default=0  );
    fairness      = Column(FLOAT      , nullable=True , default=0.0);
    token         = Column(VARCHAR(45), nullable=True);
    suspend       = Column(TIMESTAMP  , nullable=True);
    enabled       = Column(INT        , nullable=True , default=0  );
    last_choice   = Column(TIMESTAMP  , nullable=True , default='2018-01-01 00:00:00');
    playoff       = Column(TINYINT(1) , nullable=True , default=0  );
## END CLASS.








## Used by MCT_Division.
class Status(Base):

    """
    Class Status:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'STATUS';

    id            = Column(INT        , nullable=False, primary_key=True);
    players       = Column(INT        , nullable=False);
    all_requests  = Column(INT        , nullable=False);
    accepts       = Column(INT        , nullable=False);
    rejects       = Column(INT        , nullable=False);
    fairness      = Column(FLOAT      , nullable=True , default=0.0);
    timestamp     = Column(TIMESTAMP  , nullable=True);

## END CLASS.








class MCT_Database_SQLAlchemy:

    """
    Class MCT_Database_SQLAlchemy:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    session  = None;
    __engine = None;


    ###########################################################################
    ## SPECIAL METHODS                                                       ##
    ###########################################################################
    ##
    ## BRIEF: initialize the object.
    ## ------------------------------------------------------------------------
    ##
    def __init__(self, dbDictionary):

        parameter  = 'mysql://';
        parameter += dbDictionary['user'];
        parameter += ':';
        parameter += dbDictionary['pass'];
        parameter += '@';
        parameter += dbDictionary['host'];
        parameter += '/';
        parameter += dbDictionary['base'];

        ##
        self.__engine = create_engine(parameter);


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: return all registries
    ## ------------------------------------------------------------------------
    ## @PARAM obj table == object that meaning one table in database.
    ##
    def all_regs(self, table):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        rList = [];

        ## Obtain all registries from database:
        allRegistries = session.query(table).all();

        for registry in allRegistries:
            rList.append(self.__row2dict(registry));

        session.close();
        return rList;


    ##
    ## BRIEF: return first registry
    ## ------------------------------------------------------------------------
    ## @PARAM obj table == object that meaning one table in database.
    ##
    def first_reg(self, table):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        rList = [];

        ## Obtain the first registry from database:
        registry = session.query(table).first();

        rList.append(self.__row2dict(registry));

        session.close();

        return rList;


    ##
    ## BRIEF: return all registries from database (with filter).
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dct filterRules== filters to apply.
    ##
    def all_regs_filter(self, table, filterRule):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        rList = [];

        ## Obtain all registries from database:
        allRegistries = session.query(table).filter(filterRule).all();

        for registry in allRegistries:
            rList.append(self.__row2dict(registry));

        session.close();

        return rList;


    ##
    ## BRIEF: return the first registry from database (with filter).
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dct filterRules== filters to apply.
    ##
    def first_reg_filter(self, table, filterRules):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        rList = [];

        ## Execute the query:
        querySql = session.query(table)

        ## Filter:
        for attr, value in filterRules.items():
            if querySql:
                querySql = querySql.filter(value);

        ## Get the first element found in the table:
        registry = querySql.first();

        ## Convert the object structure to a pythoninc dictionary format:
        if registry:
            rList.append(self.__row2dict(registry));

        session.close();

        return rList;


    ##
    ## BRIEF: update a registry.
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM str filterRule == filter to apply.
    ## @PARAM dic fieldsDict == dictionary with fields:value to update.
    ##
    def update_reg(self, table, filterRule, fieldsDict):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        ## Update the registry:
        session.query(table).filter(filterRule).update(fieldsDict);
        session.commit();

        session.close();

        return 0;

    ##
    ## BRIEF: insert a new register in table;
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dic fieldsDict == dictionary with fields:value to update.
    ##
    def insert_reg(self, row):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        session.add(row);
        session.commit();

        session.close();

        return 0;


    ##
    ## BRIEF: delete an existent register in table;
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM str filterRule == filter to apply.
    ##
    def delete_reg(self, table, filterRules):

        DBSession = sessionmaker(bind=self.__engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        session = DBSession();

        ## Execute the query:
        querySql = session.query(table);

        ### Filter:
        for attr, value in filterRules.items():
            if querySql:
                querySql = querySql.filter(value);

        ### Delete element found in the table:
        registry = querySql.delete(synchronize_session=False);

        session.commit();

        session.close();
        return 0;


    ##
    ## BRIEF: convert the sqlalchemy row to python dictionary.
    ## ------------------------------------------------------------------------
    ## @PARAM row == row to convert. 
    ## 
    def __row2dict(self, row):
        dictionary = {};

        ##
        for column in row.__table__.columns:
            dictionary[column.name] = str(getattr(row, column.name));

        return dictionary
## END CLASS.









###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    config = {
        'user' : 'mct',
        'pass' : 'password',
        'base' : 'mct',
        'host' : 'localhost'
    };

    db = MCT_Database_SQLAlchemy(config);

    filterRules = {
        0 : Map.uuid_dst == '2628788d-7e48-432f-b642-24e88a99d4ed',
        1 : Map.uuid_src == 'playerVirtual0_3338579772'
    };

    valRet = db.delete_reg(Map, filterRules);
## END.
