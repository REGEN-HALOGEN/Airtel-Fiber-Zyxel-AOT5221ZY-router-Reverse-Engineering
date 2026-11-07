#!/bin/sh

# parameter 1 is the name of extracted header information file
file_name=$1 

# parameter 2 is the start byte count you want to retrieve in feature bits
start=`expr $2 + 1`

# parameter 3 is the end byte count you want to retrieve in feature bits
end=`expr $3 + 1`

#echo $start
#echo $end
#echo $file_name
product_model=
for i in $(seq $start $end)
do
	tmp=`cat $file_name | grep "features_bits" | sed -n '1p' | cut -d ' ' -f $i`
	product_model=$product_model$tmp
done

echo $product_model
