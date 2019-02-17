#!/bin/bash




gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_1.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_iguais.dat" u 1:2 t "Miss Rebaixados (com d)" with linespoint ls 1 lw 4 ps 2, "" u 1:8 t "Miss Rebaixados (sem d)" with linespoint ls 2 lw 4 ps 2, "" u 1:4 t "Miss Promovidos (com d)" with linespoint ls 5 lw 4 ps 2, "" u 1:10 t "Miss Promovidos (sem d)" with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_2.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_iguais.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_3.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_iguais.dat" u 1:6 ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_4.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_e_p.dat" u 1:2 with linespoint ls 1 lw 4 ps 2, "" u 1:8 with linespoint ls 2 lw 4 ps 2, "" u 1:4 with linespoint ls 5 lw 4 ps 2, "" u 1:10 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_5.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_e_p.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_6.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_e_p.dat" u 1:6 with linespoint ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_7.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_ep.dat" u 1:2 with linespoint ls 1 lw 4 ps 2, "" u 1:8 with linespoint ls 2 lw 4 ps 2, "" u 1:4 with linespoint ls 5 lw 4 ps 2, "" u 1:10 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_8.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_ep.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Rebaixados" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_9.png"
set border 3
set pointintervalbox 3
plot "variando_demoted_pesos_d_ep.dat" u 1:6 with linespoint ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker






gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_10.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_iguais.dat" u 1:2 t "Miss Rebaixados (com d)" with linespoint ls 1 lw 4 ps 2, "" u 1:8 t "Miss Rebaixados (sem d)" with linespoint ls 2 lw 4 ps 2, "" u 1:4 t "Miss Promovidos (com d)" with linespoint ls 5 lw 4 ps 2, "" u 1:10 t "Miss Promovidos (sem d)" with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_11.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_iguais.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Não Considera Peso" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_12.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_iguais.dat" u 1:6 ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_13.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_e_p.dat" u 1:2 with linespoint ls 1 lw 4 ps 2, "" u 1:8 with linespoint ls 2 lw 4 ps 2, "" u 1:4 with linespoint ls 5 lw 4 ps 2, "" u 1:10 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_14.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_e_p.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes > Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_15.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_e_p.dat" u 1:6 with linespoint ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_16.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_ep.dat" u 1:2 with linespoint ls 1 lw 4 ps 2, "" u 1:8 with linespoint ls 2 lw 4 ps 2, "" u 1:4 with linespoint ls 5 lw 4 ps 2, "" u 1:10 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_17.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_ep.dat" u 1:3 with linespoint ls 1 lw 4 ps 2, "" u 1:9 with linespoint ls 2 lw 4 ps 2, "" u 1:5 with linespoint ls 5 lw 4 ps 2, "" u 1:11 with linespoint ls 6 lw 4 ps 2
EOFMarker

gnuplot -persist <<-EOFMarker
reset
set title "PRECISÃO - ORDENAMENTO SIMPLES \n Peso: Rebaixados > Existentes = Promovidos" font "sans, 20"
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set key invert samplen 4 spacing 1 width 0 height 0 
    
set key off
set yrange [0:25]
set xrange [0:30]
set grid y 
set tics font "2"
set boxwidth 0.95
set xtic scale 0.5
set ytic scale 0.5 
set ylabel "Número de Misses por Score e Recursos" font "sans, 16"
set xlabel "Número de Jogadores Promovidos" font "sans, 16"
set datafile separator ";"
set terminal pngcairo size 800,600
set output "experimentD_investigation1_18.png"
set border 3
set pointintervalbox 3
plot "variando_promoted_pesos_d_ep.dat" u 1:6 with linespoint ls 1 lw 4 ps 2, "" u 1:12 with linespoint ls 2 lw 4 ps 2, "" u 1:7 with linespoint ls 5 lw 4 ps 2, "" u 1:13 with linespoint ls 6 lw 4 ps 2
EOFMarker
