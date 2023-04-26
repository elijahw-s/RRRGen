import fuelgen
import genfuncs
import gendicts
import controlrodgen
import othergen
import codesnippets
import tallies
import pandas as pd
import numpy as np
import xlrd, openpyxl
import os



class coreGen():
    def __init__(self, filepath, df, fueldf, tallydf, settingsdf, row = 0):
        self.filePath = filepath
        self.df = df
        self.fueldf = fueldf
        self.tallydf = tallydf
        self.settingsdf = settingsdf
        self.row = row
        self.simOptions = None
        self.fuelElements = {}
        self.controlRods = None
        self.ls = None
        self.graphite = None
        self.coreConfig = None
        self.water = None
        self.gridPlates = None
        self.sources = None
        self.waterTest = None
        self.graphiteReflector = None
        self.ct = None
        self.fluxWires = None
        self.housing = None
        self.rabbit = None
        self.neutronDetectors = None
        self.void = None
        self.tallyOptions = None
        self.tallies = {}
        self.coreLayout = {
            "B" : {key:None for key in range(1,7)},     # dictionary for the b ring
            "C" : {key:None for key in range(1,13)},    # dictionary for the c ring
            "D" : {key:None for key in range(1,19)},    # dictionary for the d ring
            "E" : {key:None for key in range(1,25)},    # dictionary for the e ring
            "F" : {key:None for key in range(1,31)},    # dictionary for the f ring
        }
        self.matLibs = None
        self.core = ''
        self.fuelCellCards = ''         # string with all fuel cell cards
        self.fuelMatCards = ''          # string with all fuel mat cards
        self.graphiteCellCard = ''
        self.gridPlateCards = ''
        self.coreSources = ''
        self.controlRodSurfaces = ''    # string with control rod surfaces (these change the change rod heights)
        self.controlRodCells = ''
        self.lsCellCards = ''           # string with all lazy susan cell cards
        self.coreConfigfill = ''
        self.waterUniverse = ''
        self.waterMat = ''
        self.coreWaterCells = ''
        self.universes = ''
        self.waterTestCard = ''
        self.voidCells = ''
        self.graphiteReflectorCards = ''
        self.ctCard = ''
        self.fluxWiresCard = ''
        self.housingCard = ''
        self.rabbitCells = ''
        self.ndCells = ''
        self.tallycards = ''
        self.simOptsCard = 'c Settings:\n'
        self.tallyOptsCard = 'c Tallies:\n'
        
        self.averageDensity = 0

        self.getSimOptions()
        self.getFuel()
        self.getFuelCellCards()
        self.getFuelMatCards()
        self.getCoreSources()
        self.getGraphiteCellCard()
        self.getControlRodSurfaces()
        self.getControlRodCells()
        self.getWater()
        self.getLSCellCards()
        self.getCoreConfig()
        self.getUniverses()
        self.getVoidCells()
        self.getGridPlates()
        self.getGraphiteReflector()
        self.getNeutronDetectors()
        self.getCT()
        self.getFluxWires()
        self.getPoolHousing()
        self.getRabbit()
        self.getTallyOptions()
        self.getTallies()
        self.getSimOptionsCard()

    def getSimOptions(self):
        row = self.df.iloc[self.row]    # reads only the current sim row from the dataframe
        self.simOptions = {"AddSm" : True if row["Add Sm"] == "Yes" else False,     # sets bool for samarium
                           "H2OTemp" : row["Water Temperature (C)"] + 273.15,       # converts inputted temperature to C 
                           "H2OTemp_MeV" : "{:.6e}".format(genfuncs.k_to_mev(row["Water Temperature (C)"] + 273.15)),    # converts temperature to MeV
                           "FTemp" : row["Fuel Temperature (C)"] + 273.15,          # converts inputted temperature to C
                           "FTemp_MeV" : "{:.6e}".format(genfuncs.k_to_mev(row["Fuel Temperature (C)"] + 273.15)),       # converts temperature to MeV
                           "CoreNo" : int(row["Core Number"]),      # integer value for the core number
                           "HZR_Ratio": row["H:Zr Ratio"],          # decimal value for H:Zr Ration
                           "H2O_Density" : row["H2O Density"] if pd.notnull(row["H2O Density"]) else None,      # this is normally calculated with the first fuel element
                           "H2O_Void_Percent" : row["H2O Void Percent"] if pd.notnull(row["H2O Void Percent"]) else 0,  # this is normally 0
                           "Graphite" : row["Graphite Core Pos"].split(","),        # makes a list of graphite element core positions
                           "AmBe" : row["AmBe Core Pos"] if pd.notnull(row["AmBe Core Pos"]) else print("   fatal. no AmBe source"),    # sets location for AmBe source
                           "Ir" : row["Ir Core Pos"] if pd.notnull(row["Ir Core Pos"]) else None,      # sets location for Ir source, not a fatal generation error because of possible source removal
                           "Shim" : row["Shim Rod"] if pd.notnull(row["Shim Rod"]) else print("   fatal. no shim rod height"),  # sets shim rod height as a percent
                           "Safe" : row["Safe Rod"] if pd.notnull(row["Safe Rod"]) else print("   fatal. no safe rod height"),  # same for safe rod
                           "Reg" : row["Reg Rod"] if pd.notnull(row["Reg Rod"]) else print("   fatal. no reg rod height"),      # safe for reg rod
                           "P_Importance" : row["Particle Transports"].replace(" ","").split(","),      # makes a list of particle transports
                           "CT_Open" : True if row["Beam Open"] == "Yes" else False,        # sets bool for if the beam is open (replaces beam water with nitrogen)
                           "Rabbit_In" : True if row["Rabbit in Core"] == "Yes" else False,  # sets bool for if the rabbit is in the core (replaces some of the air cells with plastic)
                           "Core Only" : True if row["Scale"] == "Core" else False
                           }
        for elem in self.simOptions["Graphite"]:                # sets core layout universe for graphite elements
            self.coreLayout[elem[0]][int(elem[1:])] = 80        # universe code for graphite elements
        if self.simOptions["AmBe"] != None:                     # sets core layout universe for AmBe source
            self.coreLayout[self.simOptions["AmBe"][0]][int(self.simOptions["AmBe"][1:])] = 60  # universe code for AmBe Source
        if self.simOptions["Ir"] != None:                       # sets core layout universe for Ir source
            self.coreLayout[self.simOptions["Ir"][0]][int(self.simOptions["Ir"][1:])] = 70      # universe code for Ir Source  
        self.coreLayout['C'][5] = 'Safe'
        self.coreLayout['C'][9] = 'Shim'
        self.coreLayout['E'][1] = 'Reg'
        self.coreLayout['F'][9] = 'Rabbit'
        
    def getSimOptionsCard(self):
        for option in self.simOptions.keys():   # iterates through sim options and writes a line for each option
            self.simOptsCard += f'c {option} = {self.simOptions[option] if type(self.simOptions[option]) != list else ", ".join(self.simOptions[option])}\n'
    
    def getFuel(self):
        fuelDict = self.fueldf.to_dict('index') # this splits the fueldf dataframe on its rows 
        for item in fuelDict.keys():
            self.fuelElements[fuelDict[item]["Fuel Element"]] = {"data":fuelDict[item]} # item is the row number that its at, "Fuel Element" elemenent id which is in the item-th row and the "Fuel Element" column
            self.fuelElements[fuelDict[item]["Fuel Element"]]["fuelCards"] = fuelgen.fuelGen(
                f"Core {self.simOptions['CoreNo']}",
                self.fuelElements[fuelDict[item]["Fuel Element"]]["data"],
                self.simOptions["H2OTemp"],
                self.simOptions["H2OTemp_MeV"],
                self.simOptions["H2O_Density"],
                self.simOptions["H2O_Void_Percent"],
                self.simOptions["FTemp"],
                self.simOptions["FTemp_MeV"],
                self.simOptions["AddSm"],
                self.simOptions["HZR_Ratio"],
                self.simOptions["P_Importance"],
                self.matLibs
                )
            if self.simOptions["H2O_Density"] == None:  # if H2O Density was not inputed, get the calculated value from the first fuel card
                self.simOptions["H2O_Density"] = self.fuelElements[fuelDict[item]["Fuel Element"]]["fuelCards"].H2ODensity

            if self.matLibs == None:
                self.matLibs = self.fuelElements[fuelDict[item]["Fuel Element"]]["fuelCards"].matLibs
            
            if type(self.fuelElements[fuelDict[item]["Fuel Element"]]["data"][f"Core {self.simOptions['CoreNo']}"]) == str:     # checks to make sure it is in the desired core configuration
                ring = self.fuelElements[fuelDict[item]["Fuel Element"]]["data"][f"Core {self.simOptions['CoreNo']}"][0]        # gets the ring that its in
                pos = int(self.fuelElements[fuelDict[item]["Fuel Element"]]["data"][f"Core {self.simOptions['CoreNo']}"][1:])   # gets the position in the ring
                self.coreLayout[ring][pos] = self.fuelElements[fuelDict[item]["Fuel Element"]]["data"]["Fuel Element"] if self.coreLayout[ring][pos] == None else print(f"\n   fatal. multiple element assignments to position {ring}{pos}")    # places the element
        for ring in self.coreLayout:
            for pos in self.coreLayout[ring].keys():
                if self.coreLayout[ring][pos] == None:
                    self.coreLayout[ring][pos] = 18     # 18 is a water element universe so this makes sure there aren't voids in the 
                    print(f"   warning. no element in position {ring}{pos} --- sim {self.row + 1}")
        # print(self.fuelElements)

    def getAverageDensity(self):
        elementCount = 0
        totalDensity = 0
        for ring in self.coreLayout:
            for pos in self.coreLayout[ring].keys():
                try:
                    totalDensity += self.fuelElements[self.coreLayout[ring][pos]]["fuelCards"].fuelDensity
                    elementCount += 1
                except:
                    pass
        self.averageDensity = totalDensity / elementCount

    def getCoreConfig(self):
        self.coreConfig = fuelgen.coreConfig(self.coreLayout, self.simOptions["P_Importance"])
        self.coreConfigfill += 'c -----------------------------------\n' \
                               'c ----- Begin Core Configuration ----\n' \
                               'c -----------------------------------\n' 
        self.coreConfigfill += genfuncs.make_cs(3)
        self.coreConfigfill += self.coreConfig.coreConfig
        self.coreConfigfill += genfuncs.make_cs(3)
        self.coreConfigfill += 'c -----------------------------------\n' \
                               'c ------ End Core Configuration -----\n' \
                               'c -----------------------------------\n' \

    def getFuelCellCards(self):
        self.getAverageDensity()
        self.fuelCellCards += 'c -----------------------------------\n' \
                              'c ------ Begin Fuel Cell Cards ------\n' \
                              'c -----------------------------------\n'
        self.fuelCellCards += genfuncs.make_cs(3)
        self.fuelCellCards += f"c Fuel meat density auto-generated from '{self.filePath}'\n" \
                               "c Calculated fuel meat volume = 387.7713768 cm^3\n" \
                              f"c Average fuel meat density = {'{:.6f}'.format(self.averageDensity)} g/cm^3\n"
        for ring in self.coreLayout:
            for pos in self.coreLayout[ring].keys():
                try:
                    self.fuelCellCards += self.fuelElements[self.coreLayout[ring][pos]]["fuelCards"].cellCard + '\n'
                except:
                    pass
        self.fuelCellCards += 'c -----------------------------------\n' \
                              'c ------- End Fuel Cell Cards -------\n' \
                              'c -----------------------------------\n'
    
    def getFuelMatCards(self):
        self.fuelMatCards += 'c -----------------------------------\n' \
                             'c ---- Begin Fuel Material Cards ----\n' \
                             'c -----------------------------------\n'
        self.fuelCellCards += genfuncs.make_cs(3)
        for ring in self.coreLayout:
            for pos in self.coreLayout[ring].keys():
                try:
                    self.fuelMatCards += self.fuelElements[self.coreLayout[ring][pos]]["fuelCards"].matCard + '\n'
                except:
                    pass
        self.fuelCellCards += genfuncs.make_cs(3)
        self.fuelMatCards += 'c -----------------------------------\n' \
                             'c ----- End Fuel Material Cards -----\n' \
                             'c -----------------------------------\n'

    def getCoreSources(self):
        self.sources = fuelgen.sourceGen(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"],self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["AmBe"],self.simOptions["Ir"],self.simOptions["P_Importance"])
        self.coreSources += 'c -----------------------------------\n' \
                            'c -------- Begin Core Sources -------\n' \
                            'c -----------------------------------\n'

        self.coreSources += genfuncs.make_cs(3)
        self.coreSources += self.sources.AmBe
        self.coreSources += genfuncs.make_cs(3)
        if self.simOptions["Ir"]:
            self.coreSources += self.sources.Ir
            self.coreSources += genfuncs.make_cs(3)

        self.coreSources += 'c -----------------------------------\n' \
                            'c --------- End Core Sources --------\n' \
                            'c -----------------------------------\n'

    def getControlRodSurfaces(self):
        self.controlRods = controlrodgen.controlRodGen(safeHeight=self.simOptions['Safe'], shimHeight=self.simOptions['Shim'], regHeight=self.simOptions['Reg'], h2o_temp_K=self.simOptions["H2OTemp"], h2o_temp_mev=self.simOptions["H2OTemp_MeV"], h2o_density=self.simOptions["H2O_Density"], h2o_void_percent=self.simOptions["H2O_Void_Percent"], P_imp=self.simOptions["P_Importance"],coreOnly=self.simOptions["Core Only"])
        self.controlRodSurfaces += 'c -----------------------------------\n' \
                                   'c ---- Begin Control Rod Surfaces ---\n' \
                                   'c -----------------------------------\n'
        self.controlRodSurfaces += genfuncs.make_cs(3) + self.controlRods.safeSurfaces + genfuncs.make_cs(3) + self.controlRods.shimSurfaces + genfuncs.make_cs(3) + self.controlRods.regSurfaces + genfuncs.make_cs(3)
        self.controlRodSurfaces += 'c -----------------------------------\n' \
                                   'c ----- End Control Rod Surfaces ----\n' \
                                   'c -----------------------------------\n'

    def getControlRodCells(self):
        self.controlRodCells += 'c -----------------------------------\n' \
                                'c ----- Begin Control Rod Cells -----\n' \
                                'c -----------------------------------\n'
        self.controlRodCells += genfuncs.make_cs(3)
        self.controlRodCells += self.controlRods.safeCellCard + genfuncs.make_cs(3) + self.controlRods.shimCellCard + genfuncs.make_cs(3) + self.controlRods.regCellCard + genfuncs.make_cs(3)
        self.controlRodCells += 'c -----------------------------------\n' \
                                'c ------ End Control Rod Cells ------\n' \
                                'c -----------------------------------\n'
        
    def getLSCellCards(self):
        self.ls = othergen.lsGen(self.simOptions["P_Importance"])
        self.lsCellCards += 'c -----------------------------------\n' \
                            'c ------- Begin LS Cell Cards -------\n' \
                            'c -----------------------------------\n'
        self.lsCellCards += genfuncs.make_cs(3)
        self.lsCellCards += self.ls.enclosure
        self.lsCellCards += genfuncs.make_cs(3)
        self.lsCellCards += self.ls.sampleHolders
        self.lsCellCards += genfuncs.make_cs(3)
        self.lsCellCards += 'c -----------------------------------\n' \
                            'c -------- End LS Cell Cards --------\n' \
                            'c -----------------------------------\n'

    def getWater(self):
        self.water = othergen.waterGen(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"],self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["P_Importance"],self.matLibs, self.simOptions["Core Only"])
        self.waterUniverse += 'c -----------------------------------\n' \
                              'c ---------- Water Universe ---------\n' \
                              'c -----------------------------------\n'
        self.waterUniverse += genfuncs.make_cs(3)
        self.waterUniverse += self.water.waterUniverse

        self.coreWaterCells += 'c -----------------------------------\n' \
                               'c ------ Begin Core Water Cells -----\n' \
                               'c -----------------------------------\n'
        self.coreWaterCells += genfuncs.make_cs(3)
        self.coreWaterCells += self.water.coreWaterCells
        self.coreWaterCells += genfuncs.make_cs(3)
        self.coreWaterCells += 'c -----------------------------------\n' \
                               'c ------- End Core Water Cells ------\n' \
                               'c -----------------------------------\n'

        self.waterTestCard += self.water.testCell

        self.waterMat += self.water.waterMat

    def getGridPlates(self):
        self.gridPlates = othergen.gridPlatesGen(self.simOptions["P_Importance"])

        self.gridPlateCards += 'c -----------------------------------\n' \
                               'c --------- Grid Plate Cards --------\n' \
                               'c -----------------------------------\n'
        self.gridPlateCards += genfuncs.make_cs(3)
        self.gridPlateCards += self.gridPlates.gridPlates
        self.gridPlateCards += genfuncs.make_cs(3)
        self.gridPlateCards += self.gridPlates.altLowerPlate

    def getGraphiteReflector(self):
        self.graphiteReflector = othergen.graphiteReflector(self.simOptions["P_Importance"])

        self.graphiteReflectorCards += 'c -----------------------------------\n' \
                                       'c ----- Graphite Reflector Cards ----\n' \
                                       'c -----------------------------------\n'
        self.graphiteReflectorCards += genfuncs.make_cs(3)
        self.graphiteReflectorCards += self.graphiteReflector.reflectorCells

    def getVoidCells(self):
        self.void = othergen.voidCells(self.simOptions["P_Importance"], self.simOptions["Core Only"])
        self.voidCells += 'c -----------------------------------\n' \
                          'c --------- Void Cell Cards ---------\n' \
                          'c -----------------------------------\n'
        self.voidCells += genfuncs.make_cs(3)
        self.voidCells += self.void.voidCells

    def getGraphiteCellCard(self):
        self.graphite = fuelgen.graphiteGen(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"], self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["P_Importance"])
        self.graphiteCellCard += 'c -----------------------------------\n' \
                                 'c -------- Graphite Cell Card -------\n' \
                                 'c -----------------------------------\n'
        self.graphiteCellCard += genfuncs.make_cs(3)
        self.graphiteCellCard += self.graphite.cellCard

    def getUniverses(self):
        self.universes += 'c -----------------------------------\n' \
                          'c --------- Begin Universes ---------\n' \
                          'c -----------------------------------\n'

        self.universes += genfuncs.make_cs(5)
        self.universes += self.graphiteCellCard
        self.universes += genfuncs.make_cs(5)
        self.universes += self.waterUniverse
        self.universes += genfuncs.make_cs(5)
        self.universes += self.fuelCellCards
        self.universes += genfuncs.make_cs(5)
        self.universes += self.coreSources
        self.universes += genfuncs.make_cs(5)

        self.universes += 'c -----------------------------------\n' \
                          'c ---------- End Universes ----------\n' \
                          'c -----------------------------------\n'

    def getCT(self):
        self.ct = othergen.centralThimbleGen(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"],self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["CT_Open"],self.simOptions["P_Importance"],self.simOptions["Core Only"])
        self.ctCard += 'c -----------------------------------\n' \
                       'c --------- Central Thimble ---------\n' \
                       'c -----------------------------------\n'
        self.ctCard += genfuncs.make_cs(3)
        self.ctCard += self.ct.ctCells

    def getFluxWires(self):
        self.fluxWires = othergen.fluxWires(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"],self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["P_Importance"])
        self.fluxWiresCard += 'c -----------------------------------\n' \
                              'c ------------ Flux Wires -----------\n' \
                              'c -----------------------------------\n'
        self.fluxWiresCard += genfuncs.make_cs(3)
        self.fluxWiresCard += self.fluxWires.fluxWireCard

    def getPoolHousing(self):
        self.housing = othergen.poolHousing(self.simOptions["P_Importance"])
        self.housingCard += 'c -----------------------------------\n' \
                            'c ----------- Pool Housing ----------\n' \
                            'c -----------------------------------\n'
        self.housingCard += genfuncs.make_cs(3)
        self.housingCard += self.housing.housingCells

    def getRabbit(self):
        self.rabbit = othergen.rabbit(self.simOptions["H2O_Density"],self.simOptions["H2OTemp"],self.simOptions["H2OTemp_MeV"],self.simOptions["H2O_Void_Percent"],self.simOptions["Rabbit_In"],self.simOptions["P_Importance"])
        self.rabbitCells += 'c -----------------------------------\n' \
                            'c -------- Begin Rabbit Cells -------\n' \
                            'c -----------------------------------\n'
        self.rabbitCells += genfuncs.make_cs(3)
        self.rabbitCells += self.rabbit.rabbitCells
        self.rabbitCells += genfuncs.make_cs(3)
        self.rabbitCells += 'c -----------------------------------\n' \
                            'c --------- End Rabbit Cells --------\n' \
                            'c -----------------------------------\n'

    def getNeutronDetectors(self):
        self.neutronDetectors = othergen.neutronDetectors(self.simOptions["P_Importance"])
        self.ndCells += 'c -----------------------------------\n' \
                        'c -------- Neutron Detectors --------\n' \
                        'c -----------------------------------\n'
        self.ndCells += genfuncs.make_cs(3)
        self.ndCells += self.neutronDetectors.ndCells

    def getTallyOptions(self):
        tallyDict = self.tallydf.to_dict('index') # this splits the tallydf dataframe on its rows
        for tally in tallyDict.values():
            if tally["Tally Area"] == "Lazy Susan":
                for position in tally["Lazy Susan Positions"].split(","):
                    self.tallies[gendicts.TALLY_NUMBERS[tally["Tally Area"]] + int(position)*1000] = tallies.tally(
                                                  tally["Particles"],
                                                  tally["Power (W)"],
                                                  tally["Tally Area"],
                                                  self.settingsdf,
                                                  tally["Energy Bins"],
                                                  int(position)
            )
            else:
                self.tallies[gendicts.TALLY_NUMBERS[tally["Tally Area"]]] = tallies.tally(
                                                    tally["Particles"],
                                                    tally["Power (W)"],
                                                    tally["Tally Area"],
                                                    self.settingsdf,
                                                    tally["Energy Bins"],
                                                    LSPosition=None
                )

    def getTallies(self):
        self.tallycards += 'c -----------------------------------\n' \
                           'c ----------- Tally Cards -----------\n' \
                           'c -----------------------------------\n'
        self.tallycards += genfuncs.make_cs(3)
        for tally in self.tallies.keys():
            self.tallycards += self.tallies[tally].card
            self.tallycards += genfuncs.make_cs(2)
            self.tallyOptsCard += self.tallies[tally].optsCard
        # print(self.tallycards)

    def writeFile(self):
        cellCardOpener = "c ----------------------------------------------------------------------------------------------------\n" \
                         "c -------------------------------------------- CELL CARDS --------------------------------------------\n" \
                         "c ----------------------------------------------------------------------------------------------------\n"
        surfaceCardOpener = "\nc ----------------------------------------------------------------------------------------------------\n" \
                            "c ------------------------------------------- SURFACE CARDS ------------------------------------------\n" \
                            "c ----------------------------------------------------------------------------------------------------\n"
        dataCardOpener = "\nc ----------------------------------------------------------------------------------------------------\n" \
                          "c -------------------------------------------- DATA CARDS --------------------------------------------\n" \
                          "c ----------------------------------------------------------------------------------------------------\n"
        genMatsOpener = 'c -----------------------------------\n' \
                        'c -------- General Materials --------\n' \
                        'c -----------------------------------\n'
        sourceDefOpener = 'c -----------------------------------\n' \
                          'c -------- Source Definition --------\n' \
                          'c -----------------------------------\n'
        dirPath = './Exports'
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        filePath = f'./Exports/reedCore{self.simOptions["CoreNo"]}_{self.row+1}_{self.simOptions["Safe"]}_{self.simOptions["Shim"]}_{self.simOptions["Reg"]}'
        try:
            f = open(f'{filePath}.i', 'x')
        except:
            filePath = genfuncs.find_available_name(filePath)
            f = open(f'{filePath}.i', 'x')

        '''
        Write Preamble
        '''
        f.write(codesnippets.reedReactorTitle)
        f.write(genfuncs.make_cs(10))
        f.write(self.simOptsCard)
        f.write(genfuncs.make_cs(10))
        if self.tallies != {}:
            f.write(self.tallyOptsCard)
            f.write(genfuncs.make_cs(10))
        
        '''
        Writing Cell Cards
        '''
        f.write(cellCardOpener)
        f.write(genfuncs.make_cs(10))
        f.write(self.coreConfigfill)
        f.write(genfuncs.make_cs(5))
        f.write(self.universes)
        f.write(genfuncs.make_cs(5))
        f.write(self.waterTestCard)
        f.write(genfuncs.make_cs(5))
        f.write(self.voidCells)
        f.write(genfuncs.make_cs(5))
        f.write(self.gridPlateCards)
        f.write(genfuncs.make_cs(5))
        f.write(self.graphiteReflectorCards)
        f.write(genfuncs.make_cs(5))
        f.write(self.lsCellCards)
        f.write(genfuncs.make_cs(5))
        f.write(self.coreWaterCells)
        if not self.simOptions["Core Only"]:
            f.write(genfuncs.make_cs(5))
            f.write(self.housingCard)
        f.write(genfuncs.make_cs(5))
        f.write(self.ctCard)
        f.write(genfuncs.make_cs(5))
        f.write(self.fluxWiresCard)
        f.write(genfuncs.make_cs(5))
        f.write(self.rabbitCells)
        f.write(genfuncs.make_cs(5))
        f.write(self.controlRodCells)
        f.write(genfuncs.make_cs(5))
        f.write(self.ndCells)
        f.write(genfuncs.make_cs(5))

        '''
        Writing Surface Cards
        '''
        f.write(surfaceCardOpener)
        f.write(genfuncs.make_cs(10))
        if self.simOptions["Core Only"]:
            f.write(codesnippets.modelSurfacesCore)
        else:
            f.write(codesnippets.modelSurfacesFull)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.gridPlateSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.graphiteReflectorSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.lsSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.ndSurfaces)
        f.write(genfuncs.make_cs(5))
        if self.simOptions["Core Only"]:
            f.write(codesnippets.coreWaterSurfacesCore)
        else:
            f.write(codesnippets.coreWaterSurfacesFull)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.ctSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.sourcesSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.rabbitSurfaces)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.controlRodTubes)
        f.write(genfuncs.make_cs(3))
        f.write(self.controlRodSurfaces)
        f.write(genfuncs.make_cs(5))
        if not self.simOptions["Core Only"]:
            f.write(codesnippets.poolHousingSurfaces)
            f.write(genfuncs.make_cs(5))
        f.write(codesnippets.fuelSurfaces)
        f.write(genfuncs.make_cs(5))

        '''
        Writing Data Cards
        '''
        f.write(dataCardOpener)
        f.write(genfuncs.make_cs(10))
        f.write(genMatsOpener)
        f.write(genfuncs.make_cs(5))
        f.write(codesnippets.airMat)
        f.write(genfuncs.make_cs(3))
        if self.simOptions["CT_Open"]:
            f.write(codesnippets.nitrogenMat)
            f.write(genfuncs.make_cs(3))
        f.write(self.waterMat)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.alMat_1)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.alMat_2)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.ssMat)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.graphiteMat)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.b4cMat)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.zirconiumMat)
        f.write(genfuncs.make_cs(3))
        if not self.simOptions["Core Only"]:
            f.write(codesnippets.concreteMat)
            f.write(genfuncs.make_cs(3))
        if self.simOptions["Rabbit_In"]:
            f.write(codesnippets.plasticMat)
            f.write(genfuncs.make_cs(3))
        f.write(genfuncs.make_cs(2))
        f.write(self.fuelMatCards)
        f.write(genfuncs.make_cs(5))
        if self.tallies != {}:
            f.write(self.tallycards)
            f.write(genfuncs.make_cs(5))
        f.write(sourceDefOpener)
        f.write(genfuncs.make_cs(3))
        f.write(codesnippets.sourceDef)
        f.write(genfuncs.make_cs(5))
        f.write('mode ' + ' '.join(self.simOptions["P_Importance"]) + '\n')
        f.write(genfuncs.make_cs(3))
        f.write('kcode 100000 1 15 115 $ kcode card, NIST default is 20000 neutrons, discard 5, run 105 total active cycles\n')
        f.write(genfuncs.make_cs(3))
        f.write('kopts blocksize=10 kinetics=yes precursor=yes\nc')
        
        
        

        f.close()

        print(f'created {filePath}')

def run(filePath):
    simdf = pd.read_excel(filePath, sheet_name="Setup", usecols="A:R", engine="openpyxl")
    simdf.dropna(subset="Core Number", inplace=True) #removes rows that contain empty values
    fueldf = pd.read_excel(filePath, sheet_name="Fuel Info", usecols="A:Y", engine="openpyxl")
    tallydf = pd.read_excel(filePath, sheet_name="Tallies", usecols="A:G", engine="openpyxl")
    tallydf.dropna(subset="Power (W)", inplace=True) #removes rows that contain empty values
    settingsdf = pd.read_excel(filePath, sheet_name="Settings", usecols="B:F", engine="openpyxl")
    # print(settingsdf)
    cores = {}
    for row in range(len(simdf.index)):
        cores[row] = coreGen(filePath, simdf, fueldf, tallydf, settingsdf, row)
        cores[row].writeFile()
            

run("./MCNPCoreGen.xlsx")