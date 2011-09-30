#max_lines=`wc -l $1`
#echo $max_lines
max_lines=22
OIFS=$IFS
IFS='  '
for line in $(tail -n 1 $1); do
		#echo $line
		distance=`echo ${line} 0.200 -0.200 | awk '{print ($1 < $2 && $1 > $3 && $1 != 0) ? "true" : "false" }'`	
		#echo $distance
		if [ "$distance" = "false" ]; then
			echo "0"
			exit
		fi
IFS=$OIFS
done

echo "1"
