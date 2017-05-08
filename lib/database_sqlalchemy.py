#!/usr/bin/python








__all__ = ['MCT_Database_SQLAlchemy', 'Simulation', 'State', 'Request', 'Player', 'Fairness']








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

    player_id      = Column(VARCHAR(45), nullable=False, primary_key=True); 
    vcpus          = Column(INT        , nullable=True , default=0); 
    vcpus_used     = Column(INT        , nullable=True , default=0); 
    local_gb       = Column(INT        , nullable=True , default=0);
    local_gb_used  = Column(INT        , nullable=True , default=0);
    memory         = Column(INT        , nullable=True , default=0);
    memory_mb_used = Column(INT        , nullable=True , default=0);
    requests       = Column(INT        , nullable=True , default=0);
    accepted       = Column(INT        , nullable=True , default=0);
    fairness       = Column(FLOAT      , nullable=True , default=0);

## END CLASS.









class MCT_Database_SQLAlchemy:

    """
    Class MCT_Database_SQLAlchemy:
    ---------------------------------------------------------------------------
    """

    ###########################################################################
    ## ATTRIBUTES                                                            ##
    ###########################################################################
    session = None;


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
        engine = create_engine(parameter);

        ##
        DBSession = sessionmaker(bind=engine)

        ## A DBSession() instance establishes all conversations with the databa
        ## se and represents a staging zone for all the objects loaded into the
        ## database session object. Any change made against the objects in the 
        ## session won't be persisted into the database until you call session.
        ## commit(). If you are not happy about the changes, you can revert all
        ## of them back to the last commit by calling session.rollback();
        self.session = DBSession();


    ###########################################################################
    ## PUBLIC METHODS                                                        ##
    ###########################################################################
    ##
    ## BRIEF: return all registries
    ## ------------------------------------------------------------------------
    ## @PARAM obj table == object that meaning one table in database.
    ##
    def all_regs(self, table):
        rList = [];

        ## Obtain all registries from database:
        allRegistries = self.session.query(table).all();

        for registry in allRegistries:
            rList.append(self.__row2dict(registry));

        return rList;


    ##
    ## BRIEF: return first registry
    ## ------------------------------------------------------------------------
    ## @PARAM obj table == object that meaning one table in database.
    ##
    def first_reg(self, table):
        rList = [];

        ## Obtain the first registry from database:
        registry = self.session.query(table).first();

        rList.append(self.__row2dict(registry));

        return rList;


    ##
    ## BRIEF: return all registries from database (with filter).
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dct filterRules== filters to apply.
    ##
    def all_regs_filter(self, table, filterRule):
        rList = [];

        ## Obtain all registries from database:
        allRegistries = self.session.query(table).filter(filterRule).all();

        for registry in allRegistries:
            rList.append(self.__row2dict(registry));

        return rList;


    ##
    ## BRIEF: return the first registry from database (with filter).
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dct filterRules== filters to apply.
    ##
    def first_reg_filter(self, table, filterRules):

        rList = [];

        ## Execute the query:
        querySql = self.session.query(table)

        ## Filter:
        for attr, value in filterRules.items():
            if querySql:
                querySql = querySql.filter(value);

        ## Get the first element found in the table:
        registry = querySql.first();

        ## Convert the object structure to a pythoninc dictionary format:
        if registry:
            rList.append(self.__row2dict(registry));

        return rList;


    ##
    ## BRIEF: update a registry.
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM str filterRule == filter to apply.
    ## @PARAM dic fieldsDict == dictionary with fields:value to update.
    ##
    def update_reg(self, table, filterRule, fieldsDict):

        ## Update the registry:
        self.session.query(table).filter(filterRule).update(fieldsDict);
        self.session.commit();

        return 0;


    ##
    ## BRIEF: insert a new register in table;
    ## ------------------------------------------------------------------------
    ## @PARAM obj table      == object that meaning one table in database.
    ## @PARAM dic fieldsDict == dictionary with fields:value to update.
    ##
    def insert_reg(self, row):

        self.session.add(row);
        self.session.commit();

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

## END.
