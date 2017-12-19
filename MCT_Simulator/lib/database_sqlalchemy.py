#!/usr/bin/python








__all__ = ['MCT_Database_SQLAlchemy', 'Simulation', 'State', 'Request', 'Player', 'Fairness', 'Player_MCT']








###############################################################################
## IMPORT                                                                    ##
###############################################################################
from sqlalchemy                 import *;
from sqlalchemy.ext.declarative import declarative_base;
from sqlalchemy.orm             import relation, sessionmaker, mapper;
from sqlalchemy.dialects.mysql  import *;
from sqlalchemy                 import or_, and_;







###############################################################################
## DEFINITION                                                                ##
###############################################################################
Base = declarative_base();







###############################################################################
## CLASSES                                                                   ##
###############################################################################
class Simulation(Base):

    """
    Class Simulation:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'SIMULATION';

    id          = Column(BIGINT(20) , nullable=False, primary_key=True); 
    time        = Column(BIGINT(20) , nullable=False);
    machineId   = Column(BIGINT(20) , nullable=False);
    eventType   = Column(INT        , nullable=False);
    plataformId = Column(VARCHAR(45), nullable=True );
    cpu         = Column(FLOAT      , nullable=False);
    memory      = Column(FLOAT      , nullable=False);
    valid       = Column(INT        , default=0);
        
    id.autoincrement = True;

## END CLASS.








class State(Base):

    """
    Class State:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'STATE';

    player_id = Column(VARCHAR(45), nullable=False, primary_key=True); 
    vm_id     = Column(VARCHAR(45), nullable=False);
    vm_owner  = Column(VARCHAR(45), nullable=False);
    vm_type   = Column(VARCHAR(45), nullable=False);
    running   = Column(VARCHAR(45), nullable=False);

## END CLASS.
    







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
    message            = Column(LONGTEXT   , nullable=False);
    action             = Column(INT        , nullable=True);
    timestamp_received = Column(TIMESTAMP  , nullable=True);
    timestamp_finished = Column(TIMESTAMP  , nullable=True);
    status             = Column(TINYINT(1) , nullable=True);

## END CLASS.

    





class Map(Base):

    """
    Class Map:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'MAP';

    uuid_src = Column(VARCHAR(45), nullable=False, primary_key=True);
    uuid_dst = Column(VARCHAR(45), nullable=False);
    type_obj = Column(VARCHAR(45), nullable=False);
    date     = Column(TIMESTAMP  , nullable=True);
## END CLASS.







class Fairness:

    """
    Class Fairness:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'FAIRNESS';
## END CLASS.








class Player(Base):

    """
    Class Player:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    __tablename__ = 'PLAYER';

    name          = Column(VARCHAR(45), nullable=False, primary_key=True);
    address       = Column(VARCHAR(45), nullable=True);
    division      = Column(INT        , nullable=True);
    score         = Column(FLOAT      , nullable=True , default=0.0);
    history       = Column(INT        , nullable=True , default=0  );
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
    token         = Column(VARCHAR(45), nullable=True);
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
