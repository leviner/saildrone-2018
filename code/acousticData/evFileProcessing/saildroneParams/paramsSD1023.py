# parameter library for Echoview processing

class sdParams(): # SD-specific metadata
    sdNum = 2 # SD id number
    sdSer = '1023' # SD Name
    sdEKSer = 264037 # WBT-Mini serial number
    sdXducerSer = 107 # Combi serial number
    sdMissionStart = '20180706'#'20180715' # 'YYYYMMDD' format of the starting date for making EV files (with buffer)
    sdMissionEnd = '20180710'#'20180924'# 'YYYYMMDD' format of the ending date for making EV files (with buffer)
    
class evParams(): # Echoview specific needs
    # Directories for input/output, template, and calibration
    dataAcousticDir = '..\\..\\data\\EK80\\arctic-2018\\echosounder\\sd-1023\\' # directory of *.raw data
    dataGPSDir = '..\\..\\data\\EK80\\arctic-2018\\gps_csv\\1023\\'# directory of *.gps.csv data
    outputDir = 'E:\\AIESII\\Saildrone\\Submission\\data\\EV\\EVFiles\\SD1023\\' # directory for created EV files
    evTemplateFile = '..\\..\\data\\EV\\SD_2018_template.EV' # EV template for file creation
    calFile = 'E:\\AIESII\\Saildrone\\Submission\\data\\Calibration\\SD1023_Set7_2018Mission_Final.ecs' # ecs file for specific wbat
    filePrefix = '38kHzFiltered'#'freqResp'
    newRaw = 0 # set new raw file directory

    # Parameters for file building
    scrutinize = 0 # pause during batch for scrutinize
    numMb = 3000 # number of megabytes to include per file
    numFiles = 0 # number of files to create.  if '0', create ALL
    rawFileset = 'EK80' # Fileset name to add raw files
    gpsFileset = 'GPS' # Fileset name to add GPS files

    # EvVar and line definitions
    bottomPickVar = '38 kHz XxY 3x3 convolution' # variable for picking the bottom
    bottomExclusionOffset = -.912 #1 meter minus 1 cell (.088m), for setting bottom exclusion line from pick
    bottomPickLine = 'bottom_pick' # name of bottom pick line (virtual line)
    excludeAbove = 'surface_exclusion' # surface exclusion line name
    excludeBelow = 'bottom_exclusion' # bottom explusion line name
    editVar = 'EK80: Sv pings T1 (channel 1)' # Variable for all activty (where to draw lines, etc.)
    exportVar = 'final SD data_reduced pings'#'200kHz No Fish'#'final SD data_reduced pings'#
    classExport = 'Fish'
    singleTargetVar = '38 kHz Nv filtered single targets' #or '38 kHz Nv filtered single targets' # Variable of single targets for fish track detection
    singleTargetExportVar = '38 kHz Nv filtered single targets'
    freqResponseFishVar = '200/38 Fish for Export'
    classTracks = 'Tracks' # class name for fish track assignment

    # Parameters for file exports
    gridX = .1 # export grid, horizontal dimension (distance, nmi)
    gridY = 5 # export grid, vertical dimension (meters)
