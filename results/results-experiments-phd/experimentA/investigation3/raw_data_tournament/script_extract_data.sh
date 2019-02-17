#!/bin/bash







P0='playerVirtual0'
P1='playerVirtual1'
P2='playerVirtual2'
P3='playerVirtual3'
P4='playerVirtual4'
P5='playerVirtual5'
P6='playerVirtual6'
P7='playerVirtual7'
P8='playerVirtual8'
P9='playerVirtual9'


FREERIDERS=0
LINES=0

cat ${1} |while read LINE; do


    if [ "${LINE}" != '>>>>>>>>>>' ]; then

        ID=$(echo ${LINE} |cut -d' ' -f1)

        case ${ID} in
           "${P0}")
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD0="${FAIRNESS}"
              ;; 

           "${P1}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD1="${FAIRNESS}"
               ;; 

           "${P2}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD2="${FAIRNESS}"
               ;; 

           "${P3}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD3="${FAIRNESS}"
               ;; 

           "${P4}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD4="${FAIRNESS}"
               ;; 

           "${P5}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD5="${FAIRNESS}"
               ;; 

           "${P6}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD6="${FAIRNESS}"
               ;; 

           "${P7}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD7="${FAIRNESS}"
               ;; 

           "${P8}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD8="${FAIRNESS}"
               ;; 

           "${P9}") 
               FAIRNESS=$(echo ${LINE} |cut -d' ' -f5) 
               RECORD9="${FAIRNESS}"
               ;; 
           *)
               FREERIDERS=$(( FREERIDERS + 1 ));
        esac
    else
         echo "${RECORD0} ${FREERIDERS}" >> ${P0}.dat 
         echo "${RECORD1} ${FREERIDERS}" >> ${P1}.dat
         echo "${RECORD2} ${FREERIDERS}" >> ${P2}.dat
         echo "${RECORD3} ${FREERIDERS}" >> ${P3}.dat 
         echo "${RECORD4} ${FREERIDERS}" >> ${P4}.dat 
         echo "${RECORD5} ${FREERIDERS}" >> ${P5}.dat
         echo "${RECORD6} ${FREERIDERS}" >> ${P6}.dat
         echo "${RECORD7} ${FREERIDERS}" >> ${P7}.dat
         echo "${RECORD8} ${FREERIDERS}" >> ${P8}.dat
         echo "${RECORD9} ${FREERIDERS}" >> ${P9}.dat

         FAIRNESS=0
         FREERIDERS=0;
         LINES=$(( LINES + 1 ))
    fi


    if [ ${LINES} == 101 ]; then
        break
    fi

done