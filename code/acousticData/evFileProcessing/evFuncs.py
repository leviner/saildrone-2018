import win32com.client
import time
import pandas as pd
import numpy as np
from datetime import datetime
from glob import glob
import os
'''
Created by R. Levine, found at github.com/leviner/ArcticEISII
###################################################################
evFuncs contains functions used in the creation/reading of EV data
*THIS VERSION IS FORMATTED SPECIFICALLY FOR USE WITH SAILDRONE DATA*
###################################################################
####evFiles Class####

evRawFileSorter:
- Creates filesets (i.e., EKfileSets = [[EV1 data list], [EV2 data list],...]) of *.raw files required by evBuilder

evGPSFileSorter:
- Creates filesets (i.e., GPSfileSets = [[EV1 gps file list], [EV2 gps file list],...]) of *.gps.csv files required by evBuilder

evImages:
- Creates temporary EV file from data in fileset list
- Sets lines at 20m
- Saves a .png file of the entire 38kHz variable

evBuilder:
- Create a new file from params-defined template EV file
- Add *.raw files as outlined in 'EKfileSets' (i.e., EKfileSets = [[EV1 data list], [EV2 data list],...])
- Add *.gps.csv files as outlined in 'GPSfileSets' (i.e., GPSfileSets = [[EV1 gps file list], [EV2 gps file list],...])
- Create a new surface exclusion line by adding a -2 meter offset to the surface threshold offset line
- Insert ST and ET markers at the first and last ping, assigning transect name by ct of fileSets
- Save and close file

evExporter (UNDER CONSTRICTION):
- Opens an EV file
- Sets integration thresholds
- Applies export grid
- Exports defined variables within analysis regions

####evExports Class####
readEvExports:
- Pulls basic sA data from EV exports into pandas dataframe

##############################################################
To Do:
- Currently there is only an exporter variable option for a primary Sv variables
    - single target is separate EVCOM option, needs to be its own export tool
- Rebuild mooring version with the revised functionality

'''

class evFiles():

    def evRawFileSorter(processParams):
        startDate = datetime.strptime(processParams.sdParams.sdMissionStart,'%Y%m%d')
        endDate = datetime.strptime(processParams.sdParams.sdMissionEnd,'%Y%m%d')
        rawFiles = sorted(glob(processParams.evParams.dataAcousticDir + '*.raw'))
        fileSizeList = []
        for file in rawFiles:
            fileSizeList.append(os.path.getsize(file)/1000000) # pull out all the date strings
        fileDateList = []
        for file in rawFiles:
            fileDateList.append(file[-22:-14]) # pull out all the date strings
        dayList = sorted(set(fileDateList), key=lambda x: fileDateList.index(x)) # keep track of the unique days
        # print out some info for the user
        print('Found '+ str(len(rawFiles)) +' .raw files \n'+
            'First Wakeup: '+ rawFiles[0][-23:-6] +'\n'+
           'Last Wakeup: '+ rawFiles[-1][-23:-6] +'\n'+
            'Total deployment: ' +str(len(dayList))+' days \n'+
             'Mission days for EV files: '+str((endDate-startDate).days))
        mbInFile = []
        rawFileGroups = []
        files = []
        for i in range(len(rawFiles)):
            if sum(mbInFile)+fileSizeList[i] <= processParams.evParams.numMb:
                if (datetime.strptime(fileDateList[i],'%Y%m%d') >= startDate) & (datetime.strptime(fileDateList[i],'%Y%m%d') <= endDate):
                    mbInFile.append(fileSizeList[i])
                    files.append(rawFiles[i])
            else:
                if (datetime.strptime(fileDateList[i],'%Y%m%d') >= startDate) & (datetime.strptime(fileDateList[i],'%Y%m%d') <= endDate):
                    rawFileGroups.append(files)
                    files = []
                    mbInFile = []
                    mbInFile.append(fileSizeList[i])
                    files.append(rawFiles[i])
        rawFileGroups.append(files) # to get the last group of files that never hit the Mb limit
        print('Grouping results in '+ str(len(rawFileGroups)) +' EV files \n'+
              'We skipped  ' +str(len(rawFiles)-len([item for sublist in rawFileGroups for item in sublist]))+' raw files')
        return rawFileGroups

    def evGPSFileSorter(rawFileGroups,processParams):
        gpsFiles = sorted(glob(processParams.evParams.dataGPSDir + '*.gps.csv'))
        gpsFileGroups = []
        gpsHold = []
        for i in range(len(rawFileGroups)):
            startRawTime = datetime.strptime(rawFileGroups[i][0][-23:-6], 'D%Y%m%d-T%H%M%S')
            endRawTime =  datetime.strptime(rawFileGroups[i][-1][-23:-6], 'D%Y%m%d-T%H%M%S')
            for j in range(len(gpsFiles)):
                startGPSTime = datetime.strptime(gpsFiles[j][-43:-26], '%Y-%m-%dT%H%M%S')
                endGPSTime = datetime.strptime(gpsFiles[j][-25:-8], '%Y-%m-%dT%H%M%S')
                if (startGPSTime < startRawTime)&(endGPSTime > startRawTime): # This coveres scenario 1 and 4
                    gpsHold.append(gpsFiles[j])
                elif (startGPSTime < endRawTime)&(endGPSTime > startRawTime)&(endGPSTime < endRawTime): # Scenario 2
                    gpsHold.append(gpsFiles[j])
                elif (startGPSTime < endRawTime)&(endGPSTime > endRawTime): # Scenario 2
                    gpsHold.append(gpsFiles[j])
                else:
                    continue
            gpsFileGroups.append(gpsHold)
            gpsHold = []
        print('We have '+ str(len(gpsFileGroups))+ ' GPS groupings to go with our '+str(len(rawFileGroups))+' raw file groups')
        return gpsFileGroups

    def evBuilder(EKfileSets,GPSfileSets,processParams): # where fileSets is
        newFiles = []
        EvApp = win32com.client.Dispatch("EchoviewCom.EvApplication")
        EvApp.Minimize()
        if processParams.evParams.numFiles == 0:
            fileCt = len(EKfileSets)
        else:
            fileCt = processParams.evParams.numFiles
        for i in np.arange(fileCt):
            start = time.time()
            print('\r Working on file '+str(i+1)+' of '+ str(fileCt))
            # Create new file from template
            EvFile = EvApp.NewFile(processParams.evParams.evTemplateFile)
            # Find EK80 fileset
            EKFileSet = EvFile.FileSets.FindByName(processParams.evParams.rawFileset) # replace with params value
            # Set calibration file
            EKFileSet.SetCalibrationFile(processParams.evParams.calFile)
            # Load in .raw files
            for file in EKfileSets[i]:
                EKFileSet.Datafiles.Add(file)
            # Load in GPS files
            GPSFileSet = EvFile.FileSets.FindByName(processParams.evParams.gpsFileset) # replace with params value
            for file in GPSfileSets[i]:
                GPSFileSet.Datafiles.Add(file)

            # Do the bottom pick
            EvVar =  EvFile.Variables.FindByName(processParams.evParams.bottomPickVar) # select the variable to do the bottom pick on
            EvNewLine = EvFile.Lines.CreateLinePick(EvVar,1) # do the bottom pick, currently uses "best bottom candidate" method
            EvLine = EvFile.Lines.FindByName(processParams.evParams.bottomPickLine) # find the old bottom pick line
            EvLine.OverwriteWith(EvNewLine) # now overwrite it
            EvFile.Lines.Delete(EvNewLine)# remove the line you no longer need

            # Update bottom exclusion line
            EvNewLine = EvFile.Lines.CreateOffsetLinear(EvLine,1,processParams.evParams.bottomExclusionOffset,1);
            EvLineOld = EvFile.Lines.FindByName(processParams.evParams.excludeBelow);
            EvLineOld.OverwriteWith(EvNewLine)
            EvFile.Lines.Delete(EvNewLine)

            try:
                # Make the ST marker
                EvVar = EvFile.Variables.FindByName(processParams.evParams.editVar)
                start_marker = 'ST_'+str(i+1)
                EvUpperLine = EvFile.Lines.FindByName(processParams.evParams.excludeAbove)
                EvLowerLine = EvFile.Lines.FindByName(processParams.evParams.excludeBelow)
                Region1 = EvVar.CreateLineRelativeRegion(start_marker,EvUpperLine,EvLowerLine,0,1)
                RegClassObj = EvFile.RegionClasses.FindByName('Unclassified regions')
                EvFile.Regions.FindByName(start_marker).RegionClass = RegClassObj
                EvFile.Regions.FindByName(start_marker).RegionType = 2 # 2 is marker, 1 is for analysis
            except:
                print('File '+str(i+1)+' '+EKfileSets[i][0][-22:-14]+' ST marker failed')
            
            try:
                # Make the ET marker
                end_marker = 'ET_'+str(i+1)
                EvUpperLine = EvFile.Lines.FindByName(processParams.evParams.excludeAbove)
                EvLowerLine = EvFile.Lines.FindByName(processParams.evParams.excludeBelow)
                Region1 = EvVar.CreateLineRelativeRegion(end_marker,EvUpperLine,EvLowerLine,EvVar.MeasurementCount-4,EvVar.MeasurementCount);
                RegClassObj = EvFile.RegionClasses.FindByName('Unclassified regions')
                EvFile.Regions.FindByName(end_marker).RegionClass = RegClassObj
                EvFile.Regions.FindByName(end_marker).RegionType = 2 # 1 is for analysis
            except:
                print('File '+str(i+1)+' '+EKfileSets[i][0][-22:-14]+' ET marker failed')

            EvFile.SaveAs(processParams.evParams.outputDir +'LoadedData-'+processParams.sdParams.sdSer +'-'+EKfileSets[i][0][-22:-14]+'-'+EKfileSets[i][-1][-22:-14]+'.EV')
            EvFile.Close()
            print('File Created. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
            newFiles.append(processParams.evParams.outputDir +'LoadedData-'+processParams.sdParams.sdSer +'-'+EKfileSets[i][0][-22:-14]+'-'+EKfileSets[i][-1][-22:-14]+'.EV')
        EvApp.Quit()
        print('Done')
        return newFiles

    def evImages(fileSets, processParams): # where fileSets is
        newFiles = []
        EvApp = win32com.client.Dispatch("EchoviewCom.EvApplication")
        EvApp.Minimize()
        if processParams.evParams.numFiles == 0:
            fileCt = len(fileSets)
        else:
            fileCt = processParams.evParams.numFiles
        for i in np.arange(fileCt):
            start = time.time()
            print('\r Working on file '+str(i+1)+' of '+ str(fileCt))
            # this will all be in a subloop, for i len total num files, e.g.
            EvFile = EvApp.NewFile(processParams.evParams.evTemplateFile)
            EvFileSet = EvFile.FileSets.FindByName('Fileset1') # replace with params value
            EvFileSet.SetCalibrationFile(processParams.evParams.calFile)
            for file in fileSets[i]:
                EvFileSet.Datafiles.Add(file)
            EvVar = EvFile.Variables.FindByName(processParams.evParams.editVar)
            EvVar.Properties.Grid.SetDepthRangeGrid(1,20);
            imgFile = processParams.evParams.outputDir +'Image-'+processParams.sdParams.sdSer +'-'+fileSets[i][0][-22:-14]+'-'+fileSets[i][-1][-22:-14]+'.png'
            EvVar.ExportEchogramToImage(imgFile,500)
            EvFile.Close()
            print('File Created. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
            newFiles.append(imgFile)
        EvApp.Quit()
        print('Done')
        return newFiles
    '''
    evExporter will:
    - Open file/files specified in the function call
    - Create line-relative region between exclude above and exclude below lines as defined in parameters
    - set analysis max/min thresholds
    - apply grid as defined by params
    - set analysis exclusion lines
    - export and close EV file
    '''
    def evExporter(evFiles, processParams): # where evFiles is a list of *.EV files (with complete path)
        newFiles = []
        EvApp = win32com.client.Dispatch("EchoviewCom.EvApplication")
        EvApp.Minimize()
        for file in evFiles:
            start = time.time()
            EvFile = EvApp.OpenFile(file)
            EvVar = EvFile.Variables.FindByName(processParams.evParams.exportVar)

            EvUpperLine = EvFile.Lines.FindByName(processParams.evParams.excludeAbove);
            EvLowerLine = EvFile.Lines.FindByName(processParams.evParams.excludeBelow);
            Region1 = EvVar.CreateLineRelativeRegion(processParams.evParams.classExport,EvUpperLine,EvLowerLine);
            RegClassObj = EvFile.RegionClasses.FindByName(processParams.evParams.classExport);
            EvFile.Regions.FindByName(processParams.evParams.classExport).RegionClass = RegClassObj;
            EvFile.Regions.FindByName(processParams.evParams.classExport).RegionType = 1 # 1 is for anlysis

            EvVar.Properties.Data.ApplyMinimumThreshold= 0;
            EvVar.Properties.Data.MinimumThreshold= -70;
            EvVar.Properties.Data.ApplyMaximumThreshold= 0;
            EvVar.Properties.Data.MaximumThreshold=-30;
            ## Export 5m Grid
            #  set grid settings for range in m and distance in nmi as defined by VL
            EvVar.Properties.Grid.SetDepthRangeGrid(1,processParams.evParams.gridY)
            EvVar.Properties.Grid.SetTimeDistanceGrid(2, processParams.evParams.gridX)# 1 is for time, 2 for GPS, 3 is for nmi

            # set exclusion lines
            EvVar.Properties.Analysis.ExcludeAboveLine = processParams.evParams.excludeAbove
            EvVar.Properties.Analysis.ExcludeBelowLine = processParams.evParams.excludeBelow

            EvFile.Properties.Export.Variables.Item('PRC_NASC').Enabled=1
            ExportFileName=processParams.evParams.outputDir +'exports\\'+processParams.evParams.filePrefix+'-'+processParams.sdParams.sdSer + '-'+\
                 str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv'
            exporttest = EvVar.ExportIntegrationByRegionsByCellsAll(ExportFileName);
            
            if exporttest:
                print('File Exported. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
            else:
                print('File Export Failed')
            ## Export 1m grid
            EvVar.Properties.Grid.SetDepthRangeGrid(1,1)
            EvVar.Properties.Grid.SetTimeDistanceGrid(2, processParams.evParams.gridX)# 1 is for time, 2 for GPS, 3 is for nmi

            # set exclusion lines
            EvVar.Properties.Analysis.ExcludeAboveLine = processParams.evParams.excludeAbove
            EvVar.Properties.Analysis.ExcludeBelowLine = processParams.evParams.excludeBelow

            EvFile.Properties.Export.Variables.Item('PRC_NASC').Enabled=1
            ExportFileName=processParams.evParams.outputDir +'exports\\'+processParams.evParams.filePrefix+'-'+processParams.sdParams.sdSer + '-'+\
                 '1m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv'
            exporttest = EvVar.ExportIntegrationByRegionsByCellsAll(ExportFileName);
            
            if exporttest:
                print('File Exported. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
                newFiles.append(processParams.evParams.outputDir +'exports\\'+processParams.evParams.filePrefix+'-'+processParams.sdParams.sdSer + '-'+\
                                str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
            else:
                print('File Export Failed')
            ## Export single targets    
            EvVar = EvFile.Variables.FindByName(processParams.evParams.singleTargetVar)
            EvVar.Properties.Data.ApplyMinimumThreshold= 1;
            EvVar.Properties.Data.ApplyMaximumThreshold= 1;
            EvVar.Properties.Data.LockSvMinimum= 0;
            EvVar.Properties.Data.LockSvMaximum= 0;
            EvVar.Properties.Data.MinimumThreshold= -70;
            EvVar.Properties.Data.MaximumThreshold=-30;
            EvVar.Properties.Grid.SetDepthRangeGrid(1,processParams.evParams.gridY)
            EvVar.Properties.Grid.SetTimeDistanceGrid(2, processParams.evParams.gridX)# 1 is for time, 2 for GPS, 3 is for nmi

            # set exclusion lines
            EvVar.Properties.Analysis.ExcludeAboveLine = processParams.evParams.excludeAbove
            EvVar.Properties.Analysis.ExcludeBelowLine = processParams.evParams.excludeBelow

            ExportFileName=processParams.evParams.outputDir +'exports\\SingleTargetsNv-'+processParams.sdParams.sdSer + '-'+\
                 str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv'
            exporttest = EvVar.ExportData(ExportFileName);
            if exporttest:
                print('File 2 Exported. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
                newFiles.append(processParams.evParams.outputDir +'exports\\SingleTargetsNv-'+processParams.sdParams.sdSer + '-'+\
                                str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
            else:
                print('File 2 Export Failed')
                
            EvFile.Close()
        EvApp.Quit()
        print('Done')
        return newFiles
    
    def evTargetExporter(evFiles, processParams): # where evFiles is a list of *.EV files (with complete path)
        newFiles = []
        EvApp = win32com.client.Dispatch("EchoviewCom.EvApplication")
        EvApp.Minimize()
        for file in evFiles:
            start = time.time()
            EvFile = EvApp.OpenFile(file)
            if processParams.evParams.newRaw ==1:
                EvFile.Properties.DataPaths.Add(processParams.evParams.dataAcousticDir)
                EvFile.SaveAs(file)
                EvApp.CloseFile(EvFile)
                EvFile = EvApp.OpenFile(file)
            Evfileset = EvFile.Filesets.FindByName(processParams.evParams.rawFileset)
            calfiletest = Evfileset.SetCalibrationFile(processParams.evParams.calFile)
            EvVar = EvFile.Variables.FindByName(processParams.evParams.singleTargetVar)
            EvVar.Properties.Data.ApplyMinimumThreshold= 0;
            EvVar.Properties.Data.ApplyMaximumThreshold= 0;
            EvVar.Properties.Data.LockSvMinimum= 0;
            EvVar.Properties.Data.LockSvMaximum= 0;
            EvVar.Properties.Data.MinimumThreshold= -70;
            EvVar.Properties.Data.MaximumThreshold=-30;
            EvVar1 = EvFile.Variables.FindByName('38 kHz single targets')
            EvVar1.Properties.SingleTargetDetectionParameters.TsThreshold = -70
            
            #  set grid settings for range in m and distance in nmi as defined by VL
           # EvVar = EvFile.Variables.FindByName('38 kHz Single Targets wFR')
           # EvVar.Properties.Grid.SetDepthRangeGrid(1,processParams.evParams.gridY)
           # EvVar.Properties.Grid.SetTimeDistanceGrid(2, processParams.evParams.gridX)# 1 is for time, 2 for GPS, 3 is for nmi

            # set exclusion lines
           # EvVar.Properties.Analysis.ExcludeAboveLine = processParams.evParams.excludeAbove
           # EvVar.Properties.Analysis.ExcludeBelowLine = processParams.evParams.excludeBelow

            #ExportFileName=processParams.evParams.outputDir +'exports\\SingleTargetsFRNv-'+processParams.sdParams.sdSer + '-'+\
            #     str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv'
            #exporttest = EvVar.ExportData(ExportFileName);
            #if exporttest:
            #    print('File 1 Exported. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
            #    newFiles.append(processParams.evParams.outputDir +'exports\\SingleTargetsFRNv-'+processParams.sdParams.sdSer + '-'+\
            #                    str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
            #else:
            #    print('File 1 Export Failed')
            
            EvVar = EvFile.Variables.FindByName('38 kHz Nv filtered single targets')
            EvVar.Properties.Grid.SetDepthRangeGrid(1,processParams.evParams.gridY)
            EvVar.Properties.Grid.SetTimeDistanceGrid(2, processParams.evParams.gridX)# 1 is for time, 2 for GPS, 3 is for nmi

            # set exclusion lines
            EvVar.Properties.Analysis.ExcludeAboveLine = processParams.evParams.excludeAbove
            EvVar.Properties.Analysis.ExcludeBelowLine = processParams.evParams.excludeBelow

            ExportFileName=processParams.evParams.outputDir +'exports\\SingleTargetsNv-'+processParams.sdParams.sdSer + '-'+\
                 str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv'
            exporttest = EvVar.ExportData(ExportFileName);
            if exporttest:
                print('File 2 Exported. Total time: ' + str(int(np.floor((time.time()-start)/60)))+'m '+str(round((time.time()-start)%60))+ 's')
                newFiles.append(processParams.evParams.outputDir +'exports\\SingleTargetsNv-'+processParams.sdParams.sdSer + '-'+\
                                str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
            else:
                print('File 2 Export Failed')
            EvFile.Close()
        EvApp.Quit()
        print('Done')
        return newFiles

    def evFishTracks(evFiles):
        newFiles = []
        EvApp = win32com.client.Dispatch("EchoviewCom.EvApplication")
        EvApp.Minimize()
        for file in evFiles:
            start = time.time()
            EvFile = EvApp.OpenFile(file)
            EvVar = EvFile.Variables.FindByName(processParams.evParams.singleTargetVar) # Add to the params file
            EvVar.DetectFishTracks(processParams.evParams.classTracks);
            EvVar.ExportFishTracksByCellsAll(processParams.evParams.outputDir +'exports\\FishTracks-'+processParams.sdParams.sdSer +'-'+\
                                str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
            newFiles.append(processParams.evParams.outputDir +'exports\\FishTracks-'+processParams.sdParams.sdSer + '-'+\
                                str(processParams.evParams.gridY)+'m'+'-'+file[-20:-12]+'-'+file[-11:-3]+'.csv')
        EvApp.Quit()
        print('Done')
        return newFiles

class evExports():
        # return pandas dataframe of datetime, layer number, and sA as long as 'Layer','PRC_NASC','Date_M', and 'Time_S' are in the export
    # export files can be a list of n-length of the csv files (full path)
    def readEvExports(exportFiles):
        nascDF = pd.DataFrame({'layer':[],'sA':[],'datetime':[]})
        for file in exportFiles:
            curFile = pd.read_csv(file)
            holding = {'layer':curFile[' Layer'].values,'sA':curFile[' PRC_NASC'].values,'lat':curFile[' Lat_M'],'lon':curFile[' Lon_M'], 'datetime':pd.to_datetime(curFile[' Date_M'].map(str)+curFile[' Time_M'].map(str))}
            holdingDF = pd.DataFrame(holding)
            nascDF = nascDF.append(holdingDF)
        nascDF.set_index(nascDF["datetime"],inplace=True)
        return nascDF
