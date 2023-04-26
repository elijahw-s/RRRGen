import pandas as pd
import gendicts
import genfuncs
import math
from decimal import Decimal

class tally():
    def __init__(self, particles, power_W, tallyArea, settingsdf, energyBins, LSPosition = None):
        self.power_prefix = 'W' if power_W < 1000 else 'kW'
        self.power_W_disp = power_W if power_W < 1000 else power_W/1000
        self.power_W = power_W
        self.tallyArea = tallyArea
        self.LSPosition = LSPosition 
        self.settingsdf = settingsdf
        self.energyBins = energyBins
        self.bins = ''
        self.multiplier = 0
        self.card = ''
        self.optsCard = ''
        self.particles = str(particles).split(',') if pd.notnull(particles) else ['n']
        self.tallyNumber = 1000 * self.LSPosition + gendicts.TALLY_NUMBERS[self.tallyArea] if self.tallyArea == "Lazy Susan" else gendicts.TALLY_NUMBERS[self.tallyArea]
        self.cell = int(12100+self.LSPosition) if self.LSPosition else gendicts.TALLY_CELLS[self.tallyArea]

        self.getMultiplier()
        self.getEnergyBins()
        self.getCard()
        self.getOptsCard()

    def getMultiplier(self):
        self.multiplier = "{:.4e}".format(\
                                    self.settingsdf.loc[0,"Fission Neutrons/Fission"]*\
                                    self.settingsdf.loc[0,"Fissions/MeV"]*\
                                    self.settingsdf.loc[0,"Mev/J"]*\
                                    self.power_W)
        
    def getEnergyBins(self):
        if self.energyBins == 'Default':
            self.bins += '0.625E-6  1E-3  20'
        elif self.energyBins == 'Spectrum':
            for exp in range(-6,3,1):
                for iter in range(1,10):
                    self.bins += f'{iter/10}E{exp}{"  " if iter != 9 else ""}'
                self.bins += f'\n{"     " if exp != 2 else ""}'
        elif self.energyBins == 'Custom':
            energies = self.settingsdf.loc[:,"Custom Energy Bins:"].tolist()
            try:
                for energy in energies:
                    self.bins += f'{"{:.4e}".format(energy) if (math.ceil(energy) > 99 or energy < 0.1) else energy}  '.upper()
            except:
                print("FATAL. No inputted custom energy bins")
        
    def getCard(self):
        for i in range(len(self.particles)):
            number = (100000*i) + self.tallyNumber
            self.card += f'f{number}:{self.particles[i] + " "*((5-i)%10) + str(self.cell)}\n' \
                         f'fc{number}:{self.particles[i] + " "*((4-i)%10)}Flux of {self.tallyArea}{" position " + str(self.LSPosition)[:-2] if pd.notnull(self.LSPosition) else ""} at {self.power_W_disp} {self.power_prefix} - Cell {self.cell} - Particle: {self.particles[i]}\n' \
                         f'fm{number}:{self.particles[i] + " "*((4-i)%10) + str(self.multiplier)} $ {self.power_W_disp} {self.power_prefix}\n' \
                         f'e{number}:{self.particles[i] + " "*((5-i)%10) + self.bins}'
            self.card += genfuncs.make_cs(1)

    def getOptsCard(self):
        self.optsCard += f'c {self.tallyNumber} - {self.tallyArea}, cell {self.cell} at {self.power_W_disp} {self.power_prefix}, Particles: {", ".join(self.particles)}\n'