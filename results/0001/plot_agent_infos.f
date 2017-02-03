#!/usr/bin/gnuplot -persist

unset log
unset label
unset key

set autoscale
set grid
set xtic auto rotate by 45 right font ", 8"
set ytic auto font ", 8"
set datafile separator ";"
set terminal png truecolor
set xdata time
set terminal png truecolor
set autoscale
set xdata time
set timefmt "%Y-%m-%d_%H:%M:%S"
set format x '%y-%m-%d %H:%M:%S'
#set style line 1 lc rgb '#09ad00' lt 1 lw 1.5

set style line 1 lc rgb 'green' lt 1 lw 1.5
set style line 2 lc rgb 'red'   lt 2 lw 1.5
set style line 3 lc rgb 'blue'  lt 3 lw 1.5


## ------------------------------------------------------------------------- ##
## Plot all instances running in virtual players.
## ------------------------------------------------------------------------- ##
unset label
set style data impulses 
set output "charts/instances_tiny.png"
set title  "TOTAL OF THE INSTANCES TINY RUNNING IN ALL VIRTUAL PLAYERS"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
plot "formated_results/total_inst_running/total.dat" using 1:2 ls 1

unset label
set style data impulses 
set output "charts/instances_small.png"
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN ALL VIRTUAL PLAYERS"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
plot "formated_results/total_inst_running/total.dat" using 1:3 ls 2

unset label
set style data impulses 
set output "charts/instances_medium.png"
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN ALL VIRTUAL PLAYERS"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
plot "formated_results/total_inst_running/total.dat" using 1:4 ls 3


## ------------------------------------------------------------------------- ##
## Plot total instances by virtual player.
## ------------------------------------------------------------------------- ##
set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 0"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp0.png"
plot "formated_results/instance_in_player/playerVirtual0.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 0"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp0.png"
plot "formated_results/instance_in_player/playerVirtual0.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 0"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp0.png"
plot "formated_results/instance_in_player/playerVirtual0.dat" using 1:4 ls 3

unset label
set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 1"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp1.png"
plot "formated_results/instance_in_player/playerVirtual1.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 1"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp1.png"
plot "formated_results/instance_in_player/playerVirtual1.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 1"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp1.png"
plot "formated_results/instance_in_player/playerVirtual1.dat" using 1:4 ls 3

unset label
set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 2"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp2.png"
plot "formated_results/instance_in_player/playerVirtual2.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 2"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp2.png"
plot "formated_results/instance_in_player/playerVirtual2.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 2"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp2.png"
plot "formated_results/instance_in_player/playerVirtual2.dat" using 1:4 ls 3

unset label
set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 3"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp3.png"
plot "formated_results/instance_in_player/playerVirtual3.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 3"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp3.png"
plot "formated_results/instance_in_player/playerVirtual3.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 3"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp3.png"
plot "formated_results/instance_in_player/playerVirtual3.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 4"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp4.png"
plot "formated_results/instance_in_player/playerVirtual4.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 4"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp4.png"
plot "formated_results/instance_in_player/playerVirtual4.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 4"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp4.png"
plot "formated_results/instance_in_player/playerVirtual4.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 5"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp5.png"
plot "formated_results/instance_in_player/playerVirtual5.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 5"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp5.png"
plot "formated_results/instance_in_player/playerVirtual5.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 5"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp5.png"
plot "formated_results/instance_in_player/playerVirtual5.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 6"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp6.png"
plot "formated_results/instance_in_player/playerVirtual6.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 6"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp6.png"
plot "formated_results/instance_in_player/playerVirtual6.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 6"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp6.png"
plot "formated_results/instance_in_player/playerVirtual6.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 7"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp7.png"
plot "formated_results/instance_in_player/playerVirtual7.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 7"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp7.png"
plot "formated_results/instance_in_player/playerVirtual7.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 7"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp7.png"
plot "formated_results/instance_in_player/playerVirtual7.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 8"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp8.png"
plot "formated_results/instance_in_player/playerVirtual8.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 8"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp8.png"
plot "formated_results/instance_in_player/playerVirtual8.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 8"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp8.png"
plot "formated_results/instance_in_player/playerVirtual8.dat" using 1:4 ls 3

set title  "TOTAL OF THE INSTANCES TINY RUNNING IN VIRTUAL PLAYER 9"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_tiny_vp9.png"
plot "formated_results/instance_in_player/playerVirtual9.dat" using 1:2 ls 1

unset label
set title  "TOTAL OF THE INSTANCES SMALL RUNNING IN VIRTUAL PLAYER 9"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_small_vp9.png"
plot "formated_results/instance_in_player/playerVirtual9.dat" using 1:3 ls 2

unset label
set title  "TOTAL OF THE INSTANCES MEDIUM RUNNING IN VIRTUAL PLAYER 9"
set xlabel "Number of sample along of time"
set ylabel "Number of the instances running"
set output "charts/instances_medium_vp9.png"
plot "formated_results/instance_in_player/playerVirtual9.dat" using 1:4 ls 3

## ------------------------------------------------------------------------- ##
## Plot FAIRNESS in virtual player.
## ------------------------------------------------------------------------- ##
unset label
set title  "VIRTUAL PLAYER 0 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp0.png"
plot "formated_results/fairness_by_player/playerVirtual0_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 1 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp1.png"
plot "formated_results/fairness_by_player/playerVirtual1_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 2 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp2.png"
plot "formated_results/fairness_by_player/playerVirtual2_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 3 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp3.png"
plot "formated_results/fairness_by_player/playerVirtual3_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 4 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp4.png"
plot "formated_results/fairness_by_player/playerVirtual4_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 5 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp5.png"
plot "formated_results/fairness_by_player/playerVirtual5_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 6 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp6.png"
plot "formated_results/fairness_by_player/playerVirtual6_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 7 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp7.png"
plot "formated_results/fairness_by_player/playerVirtual7_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 8 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp8.png"
plot "formated_results/fairness_by_player/playerVirtual8_fairness.dat" using 1:2 ls 1

unset label
set title  "VIRTUAL PLAYER 9 FAIRNESS"
set xlabel "Number of sample along of time"
set ylabel "Fairness"
set output "charts/fairness_vp9.png"
plot "formated_results/fairness_by_player/playerVirtual9_fairness.dat" using 1:2 ls 1

## ------------------------------------------------------------------------- ##
## Plot total REQUESTS by virtual player.
## ------------------------------------------------------------------------- ##
unset label
set title  "VIRTUAL PLAYER 0 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp0.png"
plot "formated_results/requests_by_player/playerVirtual0_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 1 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp1.png"
plot "formated_results/requests_by_player/playerVirtual1_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 2 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp2.png"
plot "formated_results/requests_by_player/playerVirtual2_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 3 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp3.png"
plot "formated_results/requests_by_player/playerVirtual3_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 4 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp4.png"
plot "formated_results/requests_by_player/playerVirtual4_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 5 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp5.png"
plot "formated_results/requests_by_player/playerVirtual5_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 6 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp6.png"
plot "formated_results/requests_by_player/playerVirtual6_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 7 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp7.png"
plot "formated_results/requests_by_player/playerVirtual7_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 8 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp8.png"
plot "formated_results/requests_by_player/playerVirtual8_requests.dat" using 1:2 ls 2

unset label
set title  "VIRTUAL PLAYER 9 REQUESTS"
set xlabel "Number of sample along of time"
set ylabel "Requests"
set output "charts/requests_vp9.png"
plot "formated_results/requests_by_player/playerVirtual9_requests.dat" using 1:2 ls 2

## ------------------------------------------------------------------------- ##
## Plot total ACCEPTED by virtual player.
## ------------------------------------------------------------------------- ##
unset label
set title  "VIRTUAL PLAYER 0 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp0.png"
plot "formated_results/accepted_by_player/playerVirtual0_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 1 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp1.png"
plot "formated_results/accepted_by_player/playerVirtual1_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 2 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp2.png"
plot "formated_results/accepted_by_player/playerVirtual2_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 3 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp3.png"
plot "formated_results/accepted_by_player/playerVirtual3_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 4 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp4.png"
plot "formated_results/accepted_by_player/playerVirtual4_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 5 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp5.png"
plot "formated_results/accepted_by_player/playerVirtual5_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 6 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp6.png"
plot "formated_results/accepted_by_player/playerVirtual6_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 7 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp7.png"
plot "formated_results/accepted_by_player/playerVirtual7_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 8 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp8.png"
plot "formated_results/accepted_by_player/playerVirtual8_accepted.dat" using 1:2 ls 3

unset label
set title  "VIRTUAL PLAYER 9 ACCEPTED"
set xlabel "Number of sample along of time"
set ylabel "Accepted"
set output "charts/accepted_vp9.png"
plot "formated_results/accepted_by_player/playerVirtual9_accepted.dat" using 1:2 ls 3

