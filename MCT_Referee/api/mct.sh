#!/bin/bash








###############################################################################
## DEFINITION                                                                ##
###############################################################################
DBBASE="mct"
DBUSER="mct"
DBPASS="password"
CMYSQL="mysql -u${DBUSER} -p${DBPASS} ${DBBASE}"




###############################################################################
## FUNCTION                                                                  ##
###############################################################################
##
## BRIEF: list the instance' actions.
## ----------------------------------------------------------------------------
##
function instances() {

    case ${1} in

        'all')
            ## Execute the command: 
            SQL="select * from PLAYER"
            ${CMYSQL} -e "${SQL}"

            if [[ ${2} == 'detail' ]]; then
                ## Execute the command: 
                SQL="select * from VM"
                ${CMYSQL} -e "${SQL}"
            fi
            ;;

        ## Verify all instances that are running in enviroment.
        'running')
            ## Execute the command: 
            SQL="select sum(running) from PLAYER"
            ${CMYSQL} -e "${SQL}"

            if [[ ${2} == 'detail' ]]; then
                ## Execute the command: 
                SQL="select * from VM where timestamp_finished is NULL"
                ${CMYSQL} -e "${SQL}"
            fi
            ;;

        'accepted')
            ## Execute the command: 
            SQL="select sum(accepts) from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        'rejects')
            ## Execute the command: 
            SQL="select sum(rejects) from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        'finished')
            ## Execute the command: 
            SQL="select sum(finished) from PLAYER"
            ${CMYSQL} -e "${SQL}"

            if [[ ${2} == 'detail' ]]; then
                ## Execute the command: 
                SQL="select * from VM where timestamp_finished is not NULL"
                ${CMYSQL} -e "${SQL}"
            fi
            ;;

        ## Unknow actions:
        *)
            echo 'Command not suported!'
            ;;
    esac

    return 0
}




###############################################################################
## MAIN                                                                      ##
###############################################################################



case ${1} in

    'instance')
        ## Remove the instance argument from the list of arguments.
        shift
        instances ${@}
        ;;

    *)
esac

## EOF

