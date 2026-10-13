#### Directory Structure

The directory is structured in the following way:

 - The file *"ids.csv"* is just one table line entry that has the ids of all the containters present in the dataset. Use this file has a helper to iterate over the dictionary.

 - The file *"INFO.csv"* has relevant data about the containers; namely *"Capacity"; "WasteType"; "Latitude"* and *"Longitude"*.

Then, for each container; there are four files that have the following naming:
 - Container_*ID*_recs_UnCorrected_with_metrics_.csv
 - Container_*ID*_fill_UnCorrected_with_metrics_.csv
 - Container_*ID*_recs_Corrected_with_metrics_.csv
 - Container_*ID*_fill_Corrected_with_metrics_.csv

The **fill** files have the information about the *Fill* level of the Container. Aditional columns are the *Max* and *Min* monotonic aproximations between each collection; along with their mean (middle point) value; The *"REC"* is a mask set to true for the first fill value measured after a collection is made; the *"Cidx"* wich is a unique indentifier for each fill value between each collection which allows to call _groupby_ on each event. The first *Date* columns is for when the collections happenned.

The  **rec** files have the information about the *Collections* made to that container. Aditional columns are the *End_Pointer* which is the row index for when that collection is made; along with *AVG_DIST* which is 100 minus the average difference between the *Max* and *Min* approximation until the next collection. And *"Spearman* which each the spearman coefficient for the fill values until the next collection scalled by 100.
