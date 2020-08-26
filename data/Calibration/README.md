# Final Cal Files:
- SD1022_Set6_2018Mission_Final.ecs
- SD1023_Set7_2018Mission_Final.ecs

# Overview
The following table is the list of dock calibrations completed for the 2018 mission (* indicates data used for final calibration):

| Date     | WBT Mini | Trandsucer | Freq. | Sphere    | EvFile(s)              |
|----------|----------|------------|-------|-----------|------------------------|
| 05/25/18 | 264033   | 106        | 38    | WC (#?)    | Set6_PreDeploy.EV      |
| 05/25/18 | 264033   | 106        | 200   | WC (#?)    | Set6_PreDeploy-200.EV  |
| 05/29/18 | 264033   | 106        | 38    | WC (#?)    | Set6_PreDeploy-2.EV    |
| 10/24/18 | 264033   | 106        | 38    | WC (#40)  | Set6_PostDeploy.EV     |
| 10/24/18 | 264033   | 106        | 200   | WC (#40)  | Set6_PostDeploy-200.EV* |
| 10/26/18 | 264033   | 106        | 38    | Cu (60mm) | Set6_PostDeployCu.EV*   |
| **Date** | **WBT Mini** | **Trandsucer** | **Freq.** |  **Sphere**  |  **EvFile(s)**  |
| 05/25/18 | 264037   | 107        | 38    | WC (#?)    | Set7_PreDeploy.EV      |
| 5/25/18  | 264037   | 107        | 200   | WC (#?)    | Set7_PreDeploy-200.EV  |
| 05/29/18 | 264037   | 107        | 38    | WC (#?)    | Set7_PreDeploy-2.EV    |
| 10/24/18 | 264037   | 107        | 38    | WC (#40)  | Set7_PostDeploy.EV     |
| 10/24/18 | 264037   | 107        | 200   | WC (#40)  | Set7_PostDeploy-200.EV* |
| 10/26/18 | 264037   | 107        | 38    | Cu (60mm) | Set7_PostDeployCu.EV*   |

In addition to the EV files listed above, to determine if the differences between post- and pre-deployment calibrations was due to the sphere, data was collected on 10/26/28 on set 7 (264037, 107) using both the WC (#40) and a different WC sphere that hadn't previously been used.  EV files were not saved but that data exists in the **Saildrone_Calibrations_Summer_2018.xlsx** spreadsheet for reference.

### Pre-deployment
- Two WBT Minis (Set 6, Set 7) were sent from Saildrone in late-May 2018.
- A dock calibration was done on 5/25/18 at the AFSC dock with a WC sphere
- The systems were brought out on the Hayes on 5/28/18 te be calibrated in deeper water.  I was unable to get a good swing or on axis.
- To confirm that there wasn't a system issue and to collect more data before deployment, the units were again dock calibrated at the AFSC dock on 5/29/18.

### Post-deployment
- Two WBT Minis were sent from Saildrone in late-October 2018, following arrival of the drones back in California.
- A calibration was done at the AFSC dock on 10/24/18 using a WC sphere, but on axis gains were found to be very different (.5-1 dB) from the pre-deployment cals.
- A calibration was done again on 10/26 using set 7 to see if the large variation is due to the sphere that was used.  On axis cals were done using 2 different WC spheres and a copper sphere, all of which were relatively similar to each other.
- Since the Cu sphere was deemed to be the most reliable, a copper sphere calibration was done for set 6.

### Final calibration
Final calibrations were calculated as described in the below sections.
- 38 kHz was done using the Cu sphere calibration conducted on 10/26/18.  EK80 was used for beam pattern, On axis gain determined in EV.
- 200 kHz calibration was done using WC sphere calibration conducted on 10/24/18 due to number of targets observed (60mm Cu sphere is on the edge of a null).  On axis gain determined in EV.

# 38 kHz split-beam calibration
*As of 10/31/18*

I'm using the Cu sphere calibrations collected on 10/26 for both the beam pattern and the on axis calibration.

1. Beam pattern values are determined from EK80 calibration.  Calibration XML files can be found in `'..\Saildrone\Calibration\OnAxis\38kHz'`:
- Set6_Copper_PostDeployment.xml
- Set7_Copper_PostDeployment.xml

Calibration results for beam pattern are also copied into *Saildrone_Calibrations_Summer_2018.xlsx*
2. On axis gain values are calculated from the EV files described above and the *Saildrone_Calibrations_Summer_2018.xlsx** spreadsheet.  

# 200 kHz single-beam calibration
The 200 kHz was calibrated according to the ICES CRP ([Demer et al., 2015](http://www.ices.dk/sites/pub/Publication%20Reports/Cooperative%20Research%20Report%20%28CRR%29/crr326/CRR326.pdf)).

1. Single target detections (single-beam, method 2) were made and exported (variable: 'Singlebeam Targets For Export') from Echoview (v9.0)
   - Set6_PreDeploy-200.EV: WC sphere on 5/25/18 at AFSC dock
      - Set6_PreDeploy200kHzSingleTargets.target.csv
   - Set6_PostDeploy-200.EV: WC sphere on 10/24/18 at AFSC dock
      - Set6_PostDeploy200kHzSingleTargets.target.csv
   - Set7_PreDeploy-200.EV: WC sphere on 5/25/18 at AFSC dock
      - Set7_PreDeploy200kHzSingleTargets.target.csv
   - Set7_PostDeploy-200.EV: WC sphere on 10/24/18 at AFSC dock
      - Set7_PostDeploy200kHzSingleTargets.target.csv
2. The mean TS and cutoff TS for the top 5% were found from the csv files using the [singlebeamCal notebook](https://github.com/leviner/ArcticEISII/blob/master/saildrone/code/acousticData/singlebeamCal.ipynb).  Targets were filtered by bounding the target depth based on visual inspection of TS vs. target range, and removal of strong targets observed in plots and sorted list ("'Clean' Max TS" below).

| Set 6    | 'Clean' Max TS | Mean 5% TS | Cutoff 5% TS | # Filtered Targets in 5% |
|----------|------------|------------|--------------|-----------|
| 5/25/18  |  -36.5 | -37.05293 |  -37.25264   |    57    |
| 10/24/18 |  -35.8 | -36.48801 |  -36.899158   |   169     |

| Set 7    | 'Clean' Max TS | Mean 5% TS | Cutoff 5% TS | # Filtered Targets in 5% |
|----------|------------|------------|--------------|-----------|
| 5/25/18  |  -36.3 |  -36.61490 | -36.79107    |    70     |
| 10/24/18 |  -36.6 |  -37.29704 |  -37.67367   |   144     |

3. Values determined above were used to filter single targets in Echoview by setting the thresholds in the 'Data' field of the single target detection (minimum = Cutoff 5% TS, maximum = 'Clean' Max TS).  The reduced pings were analyzed and integrated in the **Saildrone_Calibrations_Summer_2018.xlsx** spreadsheet.

4.  Final values for Calc gain and Calc Sa corr are taken from the spreadsheet calculations of the calibration on 10/24/18 due to the volume of targets >5%.

# Sound Speed
The sound speed for the entire survey (as well as the 2017 survey) is from the CTD data collected on the OS201701 survey.

1. Temperature, salinity, and pressure were read in from seabird .cnv files
    * Sound speed was calculated using the unesqo standard equation for all measurements of the cast deeper than 2m (the keel of the saildrone is ~1.9m)
    * The mean values for temperature, salinity, pressure, and sound speed at each lat/lon pair were saved
2. Mean sound speed of the entire OS201701 survey (1466.363268) and the saildrone survey region (1467.77236, bounded within the Chukchi Sea) were calculated, with a difference of < 1m/s, so the entire survey was used
3.  These values were compared to that of the CTD casts collected on HLY1801 cruise using the same procedure
4.  The % sensitivity of the on axis gain to *c* was calculated for reference

For calculation details and values, see the soundspeed notebook.
