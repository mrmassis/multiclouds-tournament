###############################################################################
## TEST MAP                                                                  ##
## ------------------------------------------------------------------------- ##
## Conditions: is performed an action when the conditions are satisfied.     ##
##                                                                           ##
## 1<NAME>-2<LOOP>-3<STRATEGY>-4<CONDITIONS>-5<ACTION>-6<RESOURCES>          ##
##                                                                           ##
## 1) NAME:                                                                  ##               
## -------------                                                             ##
## player name, prefix|INI:END                                               ##
##                                                                           ##
## 2) LOOP:                                                                  ##
## -------------                                                             ##
## quantity : time to wait                                                   ##
##                                                                           ##
## 3) STRATEGY:                                                              ##
## -------------                                                             ##
## 0 == aware:<parameters>                                                   ##
## 1 == cheatting:<paramters>                                                ##
## 2 == whitewashing:<parameters>                                            ##
## 3 == coalition:<parameters>                                               ##
##                                                                           ##
## 4) CONDITIONS:                                                            ##
## -------------                                                             ##
## * TIME_AFTER:                                                             ##
## * DIVISION..:                                                             ##
## * SCORE.....:                                                             ##
## * HISTORY...:                                                             ##
## * ACEPTS....:                                                             ##
## * REJECTS...:                                                             ##
## * RUNNING...:                                                             ##
## * FINISHED..:                                                             ##
## * NOTHING...: nothing to do.                                              ##
##                                                                           ##
## 5) ACTION:                                                                ##
## -------------                                                             ##
## ADD: addition new player.                                                 ##
## DEL: remove an existent player.                                           ##
## UPD: update player resources.                                             ##
##                                                                           ##
## 6) RESOURCES:                                                             ##
## -------------                                                             ## 
## *|20 -- * == random and |? is the mod randon.                             ##
##                                                                           ##
## ------------------------------------------------------------------------- ##


## Examples:
##
## create 100 players aware, iteract 100 times and waiting 5 minutes. 
#playerVirtual_0:99-100:300-0-NOTHING==1-ADD-1023_1047552_10230_50|*
#playerVirtual_10:99-100:300-0-NOTHING==1-ADD-1023_1047552_10230_0|0

playerVirtual_10:99-100:300-1-NOTHING==1-ADD-1023_1047552_10230_99|0
## EOF
