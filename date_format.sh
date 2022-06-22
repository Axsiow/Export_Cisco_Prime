awk -F',' 'BEGIN {OFS = FS}{$18 = strftime("%Y/%m/%d%T", substr($18,1,10))} 1' /fileTemp.csv > /fileDestination.csv
