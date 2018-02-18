#!/bin/bash


ACCEPTS_FILE="accepts.txt"
REJECTS_FILE="rejects.txt"



ARRAY_ACCEPTS=(0 0 0 0 0 0 0 0 0 0 0)
ARRAY_REJECTS=(0 0 0 0 0 0 0 0 0 0 0)
cat filter-coalition.dat |while read LINE; do

    if [[ ${LINE} == '-------' ]]; then

        echo ${ARRAY_ACCEPTS[@]} >> ${ACCEPTS_FILE}
        echo ${ARRAY_REJECTS[@]} >> ${REJECTS_FILE}

        ARRAY_ACCEPTS=(0 0 0 0 0 0 0 0 0 0 0)
        ARRAY_REJECTS=(0 0 0 0 0 0 0 0 0 0 0)
        continue
    fi

    PLAYERS=$(echo $LINE|cut -d' ' -f1)

    ACCEPTS=$(echo $LINE|cut -d' ' -f5)
    REJECTS=$(echo $LINE|cut -d' ' -f6)

    case $PLAYERS in
        'playerVirtual0')
            ARRAY_ACCEPTS[0]=${ACCEPTS}
            ARRAY_REJECTS[0]=${REJECTS}
            ;;
        'playerVirtual1')
            ARRAY_ACCEPTS[1]=${ACCEPTS}
            ARRAY_REJECTS[1]=${REJECTS}
            ;;
        'playerVirtual2')
            ARRAY_ACCEPTS[2]=${ACCEPTS}
            ARRAY_REJECTS[2]=${REJECTS}
            ;;
        'playerVirtual3')
            ARRAY_ACCEPTS[3]=${ACCEPTS}
            ARRAY_REJECTS[3]=${REJECTS}
            ;;
        'playerVirtual4')
            ARRAY_ACCEPTS[4]=${ACCEPTS}
            ARRAY_REJECTS[4]=${REJECTS}
            ;;
        'playerVirtual5')
            ARRAY_ACCEPTS[5]=${ACCEPTS}
            ARRAY_REJECTS[5]=${REJECTS}
            ;;
        'playerVirtual6')
            ARRAY_ACCEPTS[6]=${ACCEPTS}
            ARRAY_REJECTS[6]=${REJECTS}
            ;;
        'playerVirtual7')
            ARRAY_ACCEPTS[7]=${ACCEPTS}
            ARRAY_REJECTS[7]=${REJECTS}
            ;;
        'playerVirtual8')
            ARRAY_ACCEPTS[8]=${ACCEPTS}
            ARRAY_REJECTS[8]=${REJECTS}
            ;;
        'playerVirtual9')
            ARRAY_ACCEPTS[9]=${ACCEPTS}
            ARRAY_REJECTS[9]=${REJECTS}
            ;;
    esac
done
