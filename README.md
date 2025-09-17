## Soil Moisture Data at Marshall Field

Soil Moisture data from the early days of validating GPS interferometric Reflectometry
These are averages from 5 sensors at 2.5 cm and 5 sensors at 7.5 cm.

There were multiple GPS systems at Marshall. P041 is the official one, but to get 
the best data you must download the 1-Hz file. Only this file has L2C in it.

You are also welcome to use data from MFLE, which was installed by our group.
The L2C data are included in it (1-Hz file).

There is also a site called LOW3, which has L2C data in it.  This was 
on a tripod, and eventually the site decayed and was replaced with a real monument at MFLE.

The L1 data from these systems are not useable for soil moisture. The L2C data are great.

I have added the pboh2o data record for p041 (csv) so that you have access to the precipitation data.
These values have been converted to cumulative precipitation on one day. The raw data are 
stored at UNAVCO in the met area in the RINEX format. You have to be careful with the raw 
precipitation data as they are often wrong on snowy days (and it does snow at Marshall Field).
The pboh2o group tried hard to remove these data contaminated by snow.

There are static plots for [p041](https://gnss-reflections.org/pboh2o?station=p041) and 
[mfle](https://gnss-reflections.org/pboh2o?station=mfle) on my ad hoc archive site.

I wrote a small [python script](one_met_file.py) (with some functions) that will download and extract
precipitation from the RINEX met files. It also does temperature and pressure.  
It references some libraries in [gnssrefl](https://github.com/kristinemlarson/gnssrefl).

Access to all data from UNAVCO now requires an account/password. Please contact them directly
if you have any problems.

Updated by Kristine M. Larson
September 17, 2025
