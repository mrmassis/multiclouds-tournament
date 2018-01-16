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

        'simple')
            ## Execute the command: 
            SQL="select name,score,history,fairness,accepts,running,rejects,max_instance from PLAYER"
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

        'score')
            ## Execute the command: 
            SQL="select name, score from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        'max_score')
            ## Execute the command: 
            SQL="select MAX(score) from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        'min_score')
            ## Execute the command: 
            SQL="select MIN(score) from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        'history')
            ## Execute the command: 
            SQL="select name,history from PLAYER"
            ${CMYSQL} -e "${SQL}"
            ;;

        ## Unknow actions:
        *)
            echo 'Command not suported!'
            ;;
    esac

    return 0
}




##
## BRIEF: list the instance' actions.
## ----------------------------------------------------------------------------
##
function vm() {

    case ${1} in

        'all')
            ## Execute the command: 
            SQL="select * from VM"
            ${CMYSQL} -e "${SQL}"
            ;;


        'running')
            ## Execute the command: 
            SQL="select * from VM where status=1"
            ${CMYSQL} -e "${SQL}"
            ;;

        'finished')
            ## Execute the command: 
            SQL="select * from VM where status=3"
            ${CMYSQL} -e "${SQL}"
            ;;

        'cheating')
            ## Execute the command: 
            SQL="select * from VM where status=2"
            ${CMYSQL} -e "${SQL}"
            ;;

        ## Unknow actions:
        *)
            echo 'Command not suported!'
            ;;
    esac

    return 0
}








function status() {

    case ${1} in

        'all')
            ## Execute the command: 
            SQL="select * from STATUS"
            ${CMYSQL} -e "${SQL}"
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
        shift
        instances ${@}
        ;;

    'vm')
        shift
        vm ${@}
        ;;

    'status')
        shift
        status ${@}
        ;;

    *)  echo "Command not valid!"
        ;;
esac

## EOF

