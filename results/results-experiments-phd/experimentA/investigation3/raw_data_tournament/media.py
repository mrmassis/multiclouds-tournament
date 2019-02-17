#!/usr/bin/env python

import numpy as np;
import sys;






###############################################################################
## MAIN                                                                      ##
###############################################################################
if __name__ == "__main__":

    values = [];

    ## Open the file with all datas. Obtain the player' samples from the origi-
    ## nal file.
    fd = open(sys.argv[1], "r");
    for line in fd:
        fairness = line.split(" ")[0];

        ## Stored the sample in the list:
        values.append(float(fairness));


    ## Calculate the "variance" from fairness values stored in the player list. 
    variance = np.var(values);

    ## Calculate the "standard desviation" from fairness variance calculated be
    ## fore.
    standardDeviation = np.sqrt(variance);

    ## Calculate the mediam from player's values:
    median = np.mean(values);

    print variance, standardDeviation, median;

## EOF.
