import re
import pandas as pd
import fuelgendicts
import genfuncs
from scipy import constants

class fuelGen():
    def __init__(self, core_configuration_col, # column in the spreadsheet that houses core config information
                       df_Row,                 # pass in a pd dataframe row
                       h2o_temp_K=294,
                       h2o_temp_mev=2.533494e-08,
                       h2o_density=None,
                       h2o_void_percent=0,
                       uzrh_temp_K=294,        # used in: rcty
                       uzrh_temp_mev=2.533494e-08,
                       add_samarium=True,      # include samarium in model?
                       HZR_Ratio=1.575,        # allows to change the Hydrogen Zirconium Ratio
                       P_imp=None,             # which particles are being traced
                       matLibs=None):            
        self.data = df_Row
        self.id = self.data['Fuel Element']
        self.loc = self.data[core_configuration_col]
        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_K
        self.h2o_temp_mev = h2o_temp_mev
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.uzrh_temp_K = uzrh_temp_K
        self.uzrh_temp_mev = uzrh_temp_mev
        self.add_samarium = add_samarium
        self.HZR_Ratio = HZR_Ratio # TS allows 1.55 to 1.60. This is an ATOM ratio
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'
        self.massGrams = {'U':self.data['Uranium Now'], 'U235':self.data['U-235 Now'], 'U238':self.data['Uranium Now']-self.data['U-235 Now'], 'PU239':self.data['Pu-239 Now']}     # dictionary of all the different itotopes / elements and their mass in grams
        self.numAtoms = {}  #same thing but it is number of atoms instead of grams
        self.matLibs = matLibs          #material ids for a given fuel temp
        for mat in self.massGrams.keys():      #get atom numbers for everything in the massGrams
            try:
                self.numAtoms[mat] = self.massGrams[mat] / fuelgendicts.MOLARS[mat] * constants.Avogadro
            except:
                pass
        if self.add_samarium:
            self.numAtoms['SM149'] = self.numAtoms['U235'] / 6880 # from Eq. 3 in U.S. Patent 2843539 
            self.massGrams['SM149'] = self.numAtoms['SM149'] * fuelgendicts.MOLARS['SM149'] / constants.Avogadro
        

        self.massGrams['ZRH'] = (self.massGrams['U'] + self.massGrams['PU239']) / 8.5 * (100-8.5) # assume rest of FE mass is ZrH, do not factor in Sm-149 bc not present in fresh fuel construction
        self.numAtoms['ZR'] = self.massGrams['ZRH']/(fuelgendicts.MOLARS['ZR']/constants.Avogadro + self.HZR_Ratio*fuelgendicts.MOLARS['H']/constants.Avogadro)
        self.numAtoms['H'] = self.HZR_Ratio * self.numAtoms['ZR']   # uses atom ratio to determine number of hydrogen atoms
        self.massGrams['ZR'] = self.numAtoms['ZR'] * fuelgendicts.MOLARS['ZR'] / constants.Avogadro
        self.massGrams['H'] = self.numAtoms['H'] * fuelgendicts.MOLARS['H'] / constants.Avogadro

        self.fuelDensity = (self.massGrams['U'] + self.massGrams['PU239'] + self.massGrams['ZRH'] + (self.massGrams['SM149'] if self.add_samarium else 0))/ 387.7713768

        self.cellCard = f'c\nc --- {self.id} - {self.loc} - ({self.data["Drawing Number"]}) - Universe ---\nc\n'    #cell card
        self.matCard = 'c\nc\n'    #mat card

        self.zircDensity = 0.0425391        # atoms/barn-cm
        self.ssDensity = 7.85               # g/cm3
        self.graphiteDensity = 1.582        # g/cm3

        if not self.matLibs:
            self.findMatLibs()
            self.findMtLibs()

        self.getMatCard()
        self.getCellCard()

    def findMatLibs(self):
        '''
        Finds which materials are used for the mat card, accounts for inputted temperature.
        '''
        self.matLibs = {'U235':None, 'U238':None, 'PU239':None, 'SM149':None, 'ZR':None, 'H':None, 'O':None, 'ZRH':None, 'HZR':None, 'H2O':None}
        matList = [[None, fuelgendicts.U235_TEMPS_K_XS_DICT, 'U235'], 
                    [None, fuelgendicts.U238_TEMPS_K_XS_DICT, 'U238'],
                    [None, fuelgendicts.PU239_TEMPS_K_XS_DICT, 'PU239'],
                    [None, fuelgendicts.SM149_TEMPS_K_XS_DICT, 'SM149'],
                    [None, fuelgendicts.ZR_TEMPS_K_XS_DICT, 'ZR'],
                    [None, fuelgendicts.H_TEMPS_K_XS_DICT, 'H'], # used in fuel mats, NOT when interpolating h mats
                    [None, fuelgendicts.O_TEMPS_K_XS_DICT, 'O'],]  # used in light water mat, EVEN WHEN interpolating h mats
        for elem in matList:
            try:
                elem[0] = elem[0][self.uzrh_temp_K]
            except:
                closest_temp_K = genfuncs.find_closest_value(self.uzrh_temp_K,list(elem[1].keys()))     #finds closest temperature available material temps
                elem[0] = elem[1][closest_temp_K]
                # print(f"\n   comment. {elem[2]} cross-section (xs) data at {self.uzrh_temp_K} K does not exist")
                # print(f"   comment.   using closest available xs data at temperature: {closest_temp_K} K")
        for mat in matList:
            self.matLibs[mat[2]] = mat[0]

    def findMtLibs(self):
        try:
            self.matLibs['H2O'] = fuelgendicts.H2O_TEMPS_K_SAB_DICT[self.h2o_temp_K]
        except:
            closest_temp_K = genfuncs.find_closest_value(self.h2o_temp_K,list(fuelgendicts.H2O_TEMPS_K_SAB_DICT.keys()))
            self.matLibs['H2O'] = fuelgendicts.H2O_TEMPS_K_SAB_DICT[closest_temp_K]
            # print(f"\n   comment. light water scattering S(a,B) data at {self.h2o_temp_K} K does not exist")
                # print(f"   comment.   using closest available S(a,B) data at temperature: {closest_temp_K} K")

        mt_list = [[None, fuelgendicts.ZR_H_TEMPS_K_SAB_DICT, 'zr_h'],
                   [None, fuelgendicts.H_ZR_TEMPS_K_SAB_DICT, 'h_zr']]

        for i in range(0,len(mt_list)):
            try:
                mt_list[i][0] = mt_list[i][1][self.uzrh_temp_K]
            except:
                closest_temp_K = genfuncs.find_closest_value(self.uzrh_temp_K,list(mt_list[i][1].keys()))
                mt_list[i][0] = mt_list[i][1][closest_temp_K]
                # print(f"\n   comment. {mt_list[i][2]} scattering S(a,B) data at {self.uzrh_temp_K} does not exist")
                # print(f"   comment.   using closest available S(a,B) data at temperature: {closest_temp_K} K")

        self.matLibs['ZRH'], self.matLibs['HZR'] = mt_list[0][0], mt_list[1][0]

    def getCellCard(self):
        '''
        Generates fuel cell card for given fuel element
        '''
        self.cellCard += f'{self.id}01   105   -{"{:.2f}".format(self.ssDensity)}        312300 -312301 -311302           {self.P_imp}   u={self.id}                    $ Lower grid plate pin\n'
        self.cellCard += f'{self.id}02   102   -{self.H2ODensity}    312300 -312301  311302 -311306   {self.P_imp}   u={self.id}   tmp={self.h2o_temp_mev} $ Water around grid plate pin\n'
        self.cellCard += f'{self.id}03   105   -{"{:.2f}".format(self.ssDensity)}        312301 -312302 -311305           {self.P_imp}   u={self.id}                    $ Bottom casing\n'
        self.cellCard += f'{self.id}04   102   -{self.H2ODensity}    312301 -312306  311305 -311306   {self.P_imp}   u={self.id}   tmp={self.h2o_temp_mev} $ Water around fuel element\n'
        self.cellCard += f'{self.id}05   106   -{self.graphiteDensity}       312302 -312303 -311304           {self.P_imp}   u={self.id}                    $ Lower graphite slug\n'
        self.cellCard += f'{self.id}06   105   -{"{:.2f}".format(self.ssDensity)}        312302 -312305  311304 -311305   {self.P_imp}   u={self.id}                    $ Fuel cladding\n'
        self.cellCard += f'{self.id}07   108    {self.zircDensity}   312303 -312304 -311301           {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Zirc pin (Density src: https://doi.org/10.1016/S0306-4549(99)00094-8)\n'
        self.cellCard += f'{self.id}08  {self.id}   -{"{:.6f}".format(self.fuelDensity)}    312303 -302303  311301 -311304   {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Fuel meat section 1\n'
        self.cellCard += f'{self.id}09  {self.id}   -{"{:.6f}".format(self.fuelDensity)}    302303 -302306  311301 -311304   {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Fuel meat section 2\n'
        self.cellCard += f'{self.id}10  {self.id}   -{"{:.6f}".format(self.fuelDensity)}    302306 -302309  311301 -311304   {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Fuel meat section 3\n'
        self.cellCard += f'{self.id}11  {self.id}   -{"{:.6f}".format(self.fuelDensity)}    302309 -302312  311301 -311304   {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Fuel meat section 4\n'
        self.cellCard += f'{self.id}12  {self.id}   -{"{:.6f}".format(self.fuelDensity)}    302312 -312304  311301 -311304   {self.P_imp}   u={self.id}   tmp={self.uzrh_temp_mev} $ Fuel meat section 5\n'
        self.cellCard += f'{self.id}13   106   -{self.graphiteDensity}       312304 -312305 -311304           {self.P_imp}   u={self.id}                    $ Upper graphite spacer\n'
        self.cellCard += f'{self.id}14   105   -{"{:.2f}".format(self.ssDensity)}        312305 -312306 -311305           {self.P_imp}   u={self.id}                    $ SS top cap\n'
        self.cellCard += f'{self.id}15   105   -{"{:.2f}".format(self.ssDensity)}        312306 -312307 -311303           {self.P_imp}   u={self.id}                    $ Tri-flute\n'
        self.cellCard += f'{self.id}16   102   -{self.H2ODensity}    312306 -312307  311303 -311306   {self.P_imp}   u={self.id}   tmp={self.h2o_temp_mev} $ Water around tri-flute\n'
        self.cellCard += f'{self.id}17   105   -{"{:.2f}".format(self.ssDensity)}        312307 -312308 -311302           {self.P_imp}   u={self.id}                    $ Fuel tip\n'
        self.cellCard += f'{self.id}18   102   -{self.H2ODensity}    312307 -312308  311302 -311306   {self.P_imp}   u={self.id}   tmp={self.h2o_temp_mev} $ Water around fuel tip\n'
        self.cellCard += f'{self.id}19   102   -{self.H2ODensity}    312308 -312309 -311306           {self.P_imp}   u={self.id}   tmp={self.h2o_temp_mev} $ Water above fuel element\nc\nc'


    def getMatCard(self):
        '''
        Generates fuel material card for given fuel element, material card is in the form:
        m{fuel id}
            92235.00c {# of U235 atoms} $ U-235 {mass in grams} g
            92238.00c {# of U238 atoms} $ U-238 {mass in grams} g
            94239.00c {# of PU239 atoms} $ PU-239 {mass in grams} g
            62149.00c {# of SM149 atoms} $ SM-149 {mass in grams} g
            40000.00c {# of ZR atoms} $ ZR {mass in grams} g
            1001.00c {# of H atoms} $ H {mass in grams} g
        mt{fuel id} h-zrh.40t zr-zrh.40t
        '''
        self.matCard += f'm{self.id} $ Position {self.loc}\n'  # fuel id number
        for mat in self.numAtoms.keys():    # iterates through materials that have atom numbers
            self.matCard += f'   {self.matLibs[mat]} {"{:.6e}".format(self.numAtoms[mat])} $ {mat} {"{:.6f}".format(self.massGrams[mat])} g\n'   # creates a material line for each material 
        self.matCard += f'mt{self.id} {self.matLibs["HZR"]} {self.matLibs["ZRH"]}\n' # adds Zr materials
        self.matCard += 'c\nc'   # more comment lines after

class graphiteGen():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       P_imp = None):
        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.ssDensity = 2.70
        self.graphiteDensity = 1.698

        self.tmp = h2o_temp_mev

        self.cellCard = ''

        self.getCellCard()

    def getCellCard(self):
        self.cellCard += f'8001  104  -{"{:.2f}".format(self.ssDensity)}       312300 -312301 -311302          {self.P_imp} u=80                    $ Lower grid plate pin\n' \
                         f'8002  102  -{"{:.6f}".format(self.H2ODensity)}   312300 -312301  311302 -311306  {self.P_imp} u=80   tmp={self.tmp} $ Water around lower grid plate pin\n' \
                         f'8003  104  -{"{:.2f}".format(self.ssDensity)}       312301 -312302 -311305          {self.P_imp} u=80                    $ Bottom casing\n' \
                         f'8004  102  -{"{:.6f}".format(self.H2ODensity)}   312301 -312306  311305 -311306  {self.P_imp} u=80   tmp={self.tmp} $ Water around element\n' \
                         f'8005  106  -{"{:.3f}".format(self.graphiteDensity)}      312302 -312305 -311304          {self.P_imp} u=80                    $ Graphite slug\n' \
                         f'8006  104  -{"{:.2f}".format(self.ssDensity)}       312302 -312305  311304 -311305  {self.P_imp} u=80                    $ Element cladding\n' \
                         f'8007  104  -{"{:.2f}".format(self.ssDensity)}       312305 -312306 -311305          {self.P_imp} u=80                    $ SS top cap\n' \
                         f'8008  104  -{"{:.2f}".format(self.ssDensity)}       312306 -312307 -311303          {self.P_imp} u=80                    $ Tri-flute\n' \
                         f'8009  102  -{"{:.6f}".format(self.H2ODensity)}   312306 -312307  311303 -311306  {self.P_imp} u=80   tmp={self.tmp} $ Water around tri-flute\n' \
                         f'8010  104  -{"{:.2f}".format(self.ssDensity)}       312307 -312308 -311302          {self.P_imp} u=80                    $ Element tip\n' \
                         f'8011  102  -{"{:.6f}".format(self.H2ODensity)}   312307 -312308  311302 -311306  {self.P_imp} u=80   tmp={self.tmp} $ Water around tip\n' \
                         f'8012  102  -{"{:.6f}".format(self.H2ODensity)}   312308 -312309 -311306          {self.P_imp} u=80   tmp={self.tmp} $ Water above element\n'

class sourceGen():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       AmBe_loc = None,
                       Ir_loc = None,
                       P_imp = None):
        
        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.AmBe_loc = AmBe_loc
        self.Ir_loc = Ir_loc

        self.alDensity = 2.70
        self.airDensity = 0.0012922

        self.tmp = h2o_temp_mev

        self.AmBe = ''
        self.Ir = ''
    
        self.getAmBe()
        self.getIr()

    def getAmBe(self):
        self.AmBe += f'c ------ AmBe source ({self.AmBe_loc})\n' \
                      'c\n' \
                     f'62301   103  -{"{:.2f}".format(self.alDensity)}        -172303  172302 -171301           {self.P_imp}   u=60   $ cylindrical section beneath cavity\n' \
                     f'62302   103  -{"{:.2f}".format(self.alDensity)}        -172304  172303 -171301  173301   {self.P_imp}   u=60   $ cylindrical section containing bottommost cavity cone\n' \
                     f'62303   103  -{"{:.2f}".format(self.alDensity)}        -172305  172304 -171301  171302   {self.P_imp}   u=60   $ aluminum encasing cylindrical part of cavity\n' \
                     f'62304   101  -{"{:.7f}".format(self.airDensity)}   -172306  172305 -173302           {self.P_imp}   u=60   $ half cone atop source cavity\n' \
                     f'62305   103  -{"{:.2f}".format(self.alDensity)}        -172306  172305 -171301  173302   {self.P_imp}   u=60   $ aluminum around half cone part of cavity\n' \
                     f'62306   101  -{"{:.7f}".format(self.airDensity)}   -172308  172306 -171303           {self.P_imp}   u=60   $ cylinder component of source cavity cap\n' \
                     f'62307   103  -{"{:.2f}".format(self.alDensity)}        -172308  172306 -171301  171303   {self.P_imp}   u=60   $ aluminum around cylindrical component of source cavity cap\n' \
                     f'62308   101  -{"{:.2f}".format(self.alDensity)}        -172309  172308 -173303           {self.P_imp}   u=60   $ cone on top of cavity cap\n' \
                     f'62309   103  -{"{:.2f}".format(self.alDensity)}        -172309  172308 -171301  173303   {self.P_imp}   u=60   $ aluminum encasing cone on top of cavity cap\n' \
                     f'62310   101  -{"{:.7f}".format(self.airDensity)}   -172305  172304 -171302           {self.P_imp}   u=60   $ inner cavity cylinder\n' \
                     f'62311   101  -{"{:.7f}".format(self.airDensity)}   -172304  172303 -173301           {self.P_imp}   u=60   $ inner cavity bottom cone\n' \
                     f'62312   103  -{"{:.2f}".format(self.alDensity)}        -172311  172309 -171301           {self.P_imp}   u=60   $ source holder above cavity\n' \
                     f'62313   103  -{"{:.2f}".format(self.alDensity)}        -172312  172311 -171306           {self.P_imp}   u=60   $ cap on source holder that rests on grid plate\n' \
                     f'62314   103  -{"{:.2f}".format(self.alDensity)}        -172313  172312 -171305           {self.P_imp}   u=60   $ cylindrical base on knob\n' \
                     f'62315   103  -{"{:.2f}".format(self.alDensity)}        -172314  172313 -173304           {self.P_imp}   u=60   $ lower half of corset on knob\n' \
                     f'62316   103  -{"{:.2f}".format(self.alDensity)}        -172315  172314 -173305           {self.P_imp}   u=60   $ upper half of corset on knob\n' \
                     f'62317   103  -{"{:.2f}".format(self.alDensity)}        -172316  172315 -171305           {self.P_imp}   u=60   $ upper cylindrical part of knob\n' \
                     f'62318   103  -{"{:.2f}".format(self.alDensity)}        -172317  172316 -173306           {self.P_imp}   u=60   $ upper cone on knob\n' \
                     f'62319   102  -{self.H2ODensity}    -172314  172313 -171305  173304   {self.P_imp}   u=60   tmp={self.tmp} $ water in nook of bottom half of corset on knob\n' \
                     f'62320   102  -{self.H2ODensity}    -172315  172314 -171305  173305   {self.P_imp}   u=60   tmp={self.tmp} $ water in nook of top half of corset on knob\n' \
                     f'62321   102  -{self.H2ODensity}    -172317  172316 -171305  173306   {self.P_imp}   u=60   tmp={self.tmp} $ water around cone on end of knob\n' \
                     f'62322   102  -{self.H2ODensity}     172302 -112305  171301 -171306   {self.P_imp}   u=60   tmp={self.tmp} $ water around source\n' \
                     f'62323   102  -{self.H2ODensity}     10     -172302 -171306           {self.P_imp}   u=60   tmp={self.tmp} $ water below source\n' \
                     f'62324   102  -{self.H2ODensity}     172312 -11      171305 -171306   {self.P_imp}   u=60   tmp={self.tmp} $ Water around top\n' \
                     f'62325   102  -{self.H2ODensity}     172317 -11     -171305           {self.P_imp}   u=60   tmp={self.tmp} $ Water above top\n'

    def getIr(self):
        self.Ir += f'c ------ IR-192 source ({self.Ir_loc})\n' \
                    'c\n' \
                   f'62501   103  -{"{:.2f}".format(self.alDensity)}        -172303  172302 -171310           {self.P_imp}   u=70   $ cylindrical section beneath cavity\n' \
                   f'62502   103  -{"{:.2f}".format(self.alDensity)}        -172304  172303 -171310  173310   {self.P_imp}   u=70   $ cylindrical section containing bottommost cavity cone\n' \
                   f'62503   103  -{"{:.2f}".format(self.alDensity)}        -172305  172304 -171310  171311   {self.P_imp}   u=70   $ aluminum encasing cylindrical part of cavity\n' \
                   f'62504   101  -{"{:.7f}".format(self.airDensity)}   -172306  172305 -173311           {self.P_imp}   u=70   $ half cone atop source cavity\n' \
                   f'62505   103  -{"{:.2f}".format(self.alDensity)}        -172306  172305 -171310  173311   {self.P_imp}   u=70   $ aluminum around half cone part of cavity\n' \
                   f'62506   101  -{"{:.7f}".format(self.airDensity)}   -172308  172306 -171312           {self.P_imp}   u=70   $ cylinder component of source cavity cap\n' \
                   f'62507   103  -{"{:.2f}".format(self.alDensity)}        -172308  172306 -171310  171312   {self.P_imp}   u=70   $ aluminum around cylindrical component of source cavity cap\n' \
                   f'62508   101  -{"{:.2f}".format(self.alDensity)}        -172309  172308 -173312           {self.P_imp}   u=70   $ cone on top of cavity cap\n' \
                   f'62509   103  -{"{:.2f}".format(self.alDensity)}        -172309  172308 -171310  173312   {self.P_imp}   u=70   $ aluminum encasing cone on top of cavity cap\n' \
                   f'62510   101  -{"{:.7f}".format(self.airDensity)}   -172305  172304 -171311           {self.P_imp}   u=70   $ inner cavity cylinder\n' \
                   f'62511   101  -{"{:.7f}".format(self.airDensity)}   -172304  172303 -173310           {self.P_imp}   u=70   $ inner cavity bottom cone\n' \
                   f'62512   103  -{"{:.2f}".format(self.alDensity)}        -172311  172309 -171310           {self.P_imp}   u=70   $ source holder above cavity\n' \
                   f'62513   103  -{"{:.2f}".format(self.alDensity)}        -172312  172311 -171315           {self.P_imp}   u=70   $ cap on source holder that rests on grid plate\n' \
                   f'62514   103  -{"{:.2f}".format(self.alDensity)}        -172313  172312 -171314           {self.P_imp}   u=70   $ cylindrical base on knob\n' \
                   f'62515   103  -{"{:.2f}".format(self.alDensity)}        -172314  172313 -173313           {self.P_imp}   u=70   $ lower half of corset on knob\n' \
                   f'62516   103  -{"{:.2f}".format(self.alDensity)}        -172315  172314 -173314           {self.P_imp}   u=70   $ upper half of corset on knob\n' \
                   f'62517   103  -{"{:.2f}".format(self.alDensity)}        -172316  172315 -171314           {self.P_imp}   u=70   $ upper cylindrical part of knob\n' \
                   f'62518   103  -{"{:.2f}".format(self.alDensity)}        -172317  172316 -173315           {self.P_imp}   u=70   $ upper cone on knob\n' \
                   f'62519   102  -{self.H2ODensity}    -172314  172313 -171314  173313   {self.P_imp}   u=70   tmp={self.tmp} $ water in nook of bottom half of corset on knob\n' \
                   f'62520   102  -{self.H2ODensity}    -172315  172314 -171314  173314   {self.P_imp}   u=70   tmp={self.tmp} $ water in nook of top half of corset on knob\n' \
                   f'62521   102  -{self.H2ODensity}    -172317  172316 -171314  173315   {self.P_imp}   u=70   tmp={self.tmp} $ water around cone on end of knob\n' \
                   f'62522   102  -{self.H2ODensity}     172302 -112305  171310 -171315   {self.P_imp}   u=70   tmp={self.tmp} $ water around source\n' \
                   f'62523   102  -{self.H2ODensity}     10     -172302 -171315           {self.P_imp}   u=70   tmp={self.tmp} $ water below source\n' \
                   f'62524   102  -{self.H2ODensity}     172312 -11      171314 -171315   {self.P_imp}   u=70   tmp={self.tmp} $ Water around top\n' \
                   f'62525   102  -{self.H2ODensity}     172317 -11     -171314           {self.P_imp}   u=70   tmp={self.tmp} $ Water above top\n'

class coreConfig():
    def __init__(self, coreConfigDict,
                       P_imp):
        self.coreConfigDict = coreConfigDict
        self.coreConfig = ''
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.getCoreConfig()

    def getCoreConfig(self):
        self.coreConfig += 'c B Ring\n' \
                          f'201 0 10 -11 -20 trcl=(0.00000  4.05384 0)      {self.P_imp} fill={self.coreConfigDict["B"][1]} $\n' \
                          f'202 0 10 -11 -20 trcl=(3.51053  2.02692 0)      {self.P_imp} fill={self.coreConfigDict["B"][2]} $\n' \
                          f'203 0 10 -11 -20 trcl=(3.51053 -2.02692 0)      {self.P_imp} fill={self.coreConfigDict["B"][3]} $\n' \
                          f'204 0 10 -11 -20 trcl=( 0.00000 -4.05384 0)     {self.P_imp} fill={self.coreConfigDict["B"][4]} $\n' \
                          f'205 0 10 -11 -20 trcl=(-3.51053 -2.02692 0)     {self.P_imp} fill={self.coreConfigDict["B"][5]} $\n' \
                          f'206 0 10 -11 -20 trcl=(-3.51053  2.02692 0)     {self.P_imp} fill={self.coreConfigDict["B"][6]} $\n' \
                           'c\n' \
                           'c C Ring\n' \
                          f'301 0 10 -11 -20 trcl=( 0.00000  7.98068 0)     {self.P_imp} fill={self.coreConfigDict["C"][1]} $\n' \
                          f'302 0 10 -11 -20 trcl=( 3.99034  6.91134 0)     {self.P_imp} fill={self.coreConfigDict["C"][2]} $\n' \
                          f'303 0 10 -11 -20 trcl=( 6.91134  3.99034 0)     {self.P_imp} fill={self.coreConfigDict["C"][3]} $\n' \
                          f'304 0 10 -11 -20 trcl=( 7.98068  0.00000 0)     {self.P_imp} fill={self.coreConfigDict["C"][4]} $\n' \
                           'c Safe Rod\n' \
                          f'306 0 10 -11 -20 trcl=( 3.99034 -6.91134 0)     {self.P_imp} fill={self.coreConfigDict["C"][6]} $\n' \
                          f'307 0 10 -11 -20 trcl=( 0.00000 -7.98068 0)     {self.P_imp} fill={self.coreConfigDict["C"][7]} $\n' \
                          f'308 0 10 -11 -20 trcl=(-3.99034 -6.91134 0)     {self.P_imp} fill={self.coreConfigDict["C"][8]} $\n' \
                           'c Shim Rod\n' \
                          f'310 0 10 -11 -20 trcl=(-7.98068  0.00000 0)     {self.P_imp} fill={self.coreConfigDict["C"][10]} $\n' \
                          f'311 0 10 -11 -20 trcl=(-6.91130  3.99030 0)     {self.P_imp} fill={self.coreConfigDict["C"][11]} $\n' \
                          f'312 0 10 -11 -20 trcl=(-3.99030  6.91130 0)     {self.P_imp} fill={self.coreConfigDict["C"][12]} $\n' \
                           'c\n' \
                           'c D Ring\n' \
                          f'401 0 10 -11 -20 trcl=( 0.00000  11.9456 0)     {self.P_imp} fill={self.coreConfigDict["D"][1]} $\n' \
                          f'402 0 10 -11 -20 trcl=( 4.08530  11.2253 0)     {self.P_imp} fill={self.coreConfigDict["D"][2]} $\n' \
                          f'403 0 10 -11 -20 trcl=( 7.67870  9.15040 0)     {self.P_imp} fill={self.coreConfigDict["D"][3]} $\n' \
                          f'404 0 10 -11 -20 trcl=( 10.3449  5.97280 0)     {self.P_imp} fill={self.coreConfigDict["D"][4]} $\n' \
                          f'405 0 10 -11 -20 trcl=( 11.7640  2.07370 0)     {self.P_imp} fill={self.coreConfigDict["D"][5]} $\n' \
                          f'406 0 10 -11 -20 trcl=( 11.7640 -2.07370 0)     {self.P_imp} fill={self.coreConfigDict["D"][6]} $\n' \
                          f'407 0 10 -11 -20 trcl=( 10.3449 -5.97280 0)     {self.P_imp} fill={self.coreConfigDict["D"][7]} $\n' \
                          f'408 0 10 -11 -20 trcl=( 7.67870 -9.15040 0)     {self.P_imp} fill={self.coreConfigDict["D"][8]} $\n' \
                          f'409 0 10 -11 -20 trcl=( 4.08530 -11.2253 0)     {self.P_imp} fill={self.coreConfigDict["D"][9]} $\n' \
                          f'410 0 10 -11 -20 trcl=( 0.00000 -11.9456 0)     {self.P_imp} fill={self.coreConfigDict["D"][10]} $\n' \
                          f'411 0 10 -11 -20 trcl=(-4.08530 -11.2253 0)     {self.P_imp} fill={self.coreConfigDict["D"][11]} $\n' \
                          f'412 0 10 -11 -20 trcl=(-7.67870 -9.15040 0)     {self.P_imp} fill={self.coreConfigDict["D"][12]} $\n' \
                          f'413 0 10 -11 -20 trcl=(-10.3449 -5.97280 0)     {self.P_imp} fill={self.coreConfigDict["D"][13]} $\n' \
                          f'414 0 10 -11 -20 trcl=(-11.7640 -2.07370 0)     {self.P_imp} fill={self.coreConfigDict["D"][14]} $\n' \
                          f'415 0 10 -11 -20 trcl=(-11.7640  2.07370 0)     {self.P_imp} fill={self.coreConfigDict["D"][15]} $\n' \
                          f'416 0 10 -11 -20 trcl=(-10.3449  5.97280 0)     {self.P_imp} fill={self.coreConfigDict["D"][16]} $\n' \
                          f'417 0 10 -11 -20 trcl=(-7.67870  9.15040 0)     {self.P_imp} fill={self.coreConfigDict["D"][17]} $\n' \
                          f'418 0 10 -11 -20 trcl=(-4.08530  11.2253 0)     {self.P_imp} fill={self.coreConfigDict["D"][18]} $\n' \
                           'c\n' \
                           'c E Ring\n' \
                           'c Reg Rod ( 0.0000000  15.915600 0)\n' \
                          f'502 0 10 -11 -20 trcl=( 4.1189000  15.372800 0) {self.P_imp} fill={self.coreConfigDict["E"][2]} $\n' \
                          f'503 0 10 -11 -20 trcl=( 7.9578000  13.782800 0) {self.P_imp} fill={self.coreConfigDict["E"][3]} $\n' \
                          f'504 0 10 -11 -20 trcl=( 11.254000  11.254000 0) {self.P_imp} fill={self.coreConfigDict["E"][4]} $\n' \
                          f'505 0 10 -11 -20 trcl=( 13.874200  7.9578000 0) {self.P_imp} fill={self.coreConfigDict["E"][5]} $\n' \
                          f'506 0 10 -11 -20 trcl=( 15.372800  4.1189000 0) {self.P_imp} fill={self.coreConfigDict["E"][6]} $\n' \
                          f'507 0 10 -11 -20 trcl=( 15.915600  0.0000000 0) {self.P_imp} fill={self.coreConfigDict["E"][7]} $\n' \
                          f'508 0 10 -11 -20 trcl=( 15.372800 -4.1189000 0) {self.P_imp} fill={self.coreConfigDict["E"][8]} $\n' \
                          f'509 0 10 -11 -20 trcl=( 13.874200 -7.9578000 0) {self.P_imp} fill={self.coreConfigDict["E"][9]} $\n' \
                          f'510 0 10 -11 -20 trcl=( 11.254000 -11.254000 0) {self.P_imp} fill={self.coreConfigDict["E"][10]} $\n' \
                          f'511 0 10 -11 -20 trcl=( 7.9578000 -13.782800 0) {self.P_imp} fill={self.coreConfigDict["E"][11]} $\n' \
                          f'512 0 10 -11 -20 trcl=( 4.1189000 -15.372800 0) {self.P_imp} fill={self.coreConfigDict["E"][12]} $\n' \
                          f'513 0 10 -11 -20 trcl=( 0.0000000 -15.915600 0) {self.P_imp} fill={self.coreConfigDict["E"][13]} $\n' \
                          f'514 0 10 -11 -20 trcl=(-4.1189000 -15.372800 0) {self.P_imp} fill={self.coreConfigDict["E"][14]} $\n' \
                          f'515 0 10 -11 -20 trcl=(-7.9578000 -13.782800 0) {self.P_imp} fill={self.coreConfigDict["E"][15]} $\n' \
                          f'516 0 10 -11 -20 trcl=(-11.254000 -11.254000 0) {self.P_imp} fill={self.coreConfigDict["E"][16]} $\n' \
                          f'517 0 10 -11 -20 trcl=(-13.874200 -7.9578000 0) {self.P_imp} fill={self.coreConfigDict["E"][17]} $\n' \
                          f'518 0 10 -11 -20 trcl=(-15.372800 -4.1189000 0) {self.P_imp} fill={self.coreConfigDict["E"][18]} $\n' \
                          f'519 0 10 -11 -20 trcl=(-15.915600  0.0000000 0) {self.P_imp} fill={self.coreConfigDict["E"][19]} $\n' \
                          f'520 0 10 -11 -20 trcl=(-15.372800  4.1189000 0) {self.P_imp} fill={self.coreConfigDict["E"][20]} $\n' \
                          f'521 0 10 -11 -20 trcl=(-13.874200  7.9578000 0) {self.P_imp} fill={self.coreConfigDict["E"][21]} $\n' \
                          f'522 0 10 -11 -20 trcl=(-11.254000  11.254000 0) {self.P_imp} fill={self.coreConfigDict["E"][22]} $\n' \
                          f'523 0 10 -11 -20 trcl=(-7.9578000  13.782800 0) {self.P_imp} fill={self.coreConfigDict["E"][23]} $\n' \
                          f'524 0 10 -11 -20 trcl=(-4.1189000  15.372800 0) {self.P_imp} fill={self.coreConfigDict["E"][24]} $\n' \
                           'c\n' \
                           'c F Ring\n' \
                          f'601 0 10 -11 -20 trcl=( 0.0000000  19.888200 0) {self.P_imp} fill={self.coreConfigDict["F"][1]} $\n' \
                          f'602 0 10 -11 -20 trcl=( 4.1348660  19.452590 0) {self.P_imp} fill={self.coreConfigDict["F"][2]} $\n' \
                          f'603 0 10 -11 -20 trcl=( 8.0886300  18.157860 0) {self.P_imp} fill={self.coreConfigDict["F"][3]} $\n' \
                          f'604 0 10 -11 -20 trcl=( 11.690350  16.089630 0) {self.P_imp} fill={self.coreConfigDict["F"][4]} $\n' \
                          f'605 0 10 -11 -20 trcl=( 14.778990  13.307314 0) {self.P_imp} fill={self.coreConfigDict["F"][5]} $\n' \
                          f'606 0 10 -11 -20 trcl=( 17.223232  9.9441000 0) {self.P_imp} fill={self.coreConfigDict["F"][6]} $\n' \
                          f'607 0 10 -11 -20 trcl=( 18.915634  6.1455300 0) {self.P_imp} fill={self.coreConfigDict["F"][7]} $\n' \
                          f'608 0 10 -11 -20 trcl=( 19.777202  2.0706080 0) {self.P_imp} fill={self.coreConfigDict["F"][8]} $\n' \
                           'c Rabbit ( 19.777202 -2.0706080 0)\n' \
                          f'610 0 10 -11 -20 trcl=( 18.915634 -6.1455300 0) {self.P_imp} fill={self.coreConfigDict["F"][10]} $\n' \
                          f'611 0 10 -11 -20 trcl=( 17.223232 -9.9441000 0) {self.P_imp} fill={self.coreConfigDict["F"][11]} $\n' \
                          f'612 0 10 -11 -20 trcl=( 14.778990 -13.307314 0) {self.P_imp} fill={self.coreConfigDict["F"][12]} $\n' \
                          f'613 0 10 -11 -20 trcl=( 11.690350 -16.089630 0) {self.P_imp} fill={self.coreConfigDict["F"][13]} $\n' \
                          f'614 0 10 -11 -20 trcl=( 8.0886300 -18.167858 0) {self.P_imp} fill={self.coreConfigDict["F"][14]} $\n' \
                          f'615 0 10 -11 -20 trcl=( 4.1348660 -19.452590 0) {self.P_imp} fill={self.coreConfigDict["F"][15]} $\n' \
                          f'616 0 10 -11 -20 trcl=( 0.0000000 -19.888200 0) {self.P_imp} fill={self.coreConfigDict["F"][16]} $\n' \
                          f'617 0 10 -11 -20 trcl=(-4.1348660 -19.452590 0) {self.P_imp} fill={self.coreConfigDict["F"][17]} $\n' \
                          f'618 0 10 -11 -20 trcl=(-8.0886300 -18.167858 0) {self.P_imp} fill={self.coreConfigDict["F"][18]} $\n' \
                          f'619 0 10 -11 -20 trcl=(-11.690350 -16.089630 0) {self.P_imp} fill={self.coreConfigDict["F"][19]} $\n' \
                          f'620 0 10 -11 -20 trcl=(-14.778990 -13.307314 0) {self.P_imp} fill={self.coreConfigDict["F"][20]} $\n' \
                          f'621 0 10 -11 -20 trcl=(-17.223232 -9.9441000 0) {self.P_imp} fill={self.coreConfigDict["F"][21]} $\n' \
                          f'622 0 10 -11 -20 trcl=(-18.915634 -6.1455300 0) {self.P_imp} fill={self.coreConfigDict["F"][22]} $\n' \
                          f'623 0 10 -11 -20 trcl=(-19.777202 -2.0706080 0) {self.P_imp} fill={self.coreConfigDict["F"][23]} $\n' \
                          f'624 0 10 -11 -20 trcl=(-19.777202  2.0706080 0) {self.P_imp} fill={self.coreConfigDict["F"][24]} $\n' \
                          f'625 0 10 -11 -20 trcl=(-18.915634  6.1455300 0) {self.P_imp} fill={self.coreConfigDict["F"][25]} $\n' \
                          f'626 0 10 -11 -20 trcl=(-17.223232  9.9441000 0) {self.P_imp} fill={self.coreConfigDict["F"][26]} $\n' \
                          f'627 0 10 -11 -20 trcl=(-14.778990  13.307314 0) {self.P_imp} fill={self.coreConfigDict["F"][27]} $\n' \
                          f'628 0 10 -11 -20 trcl=(-11.690350  16.089630 0) {self.P_imp} fill={self.coreConfigDict["F"][28]} $\n' \
                          f'629 0 10 -11 -20 trcl=(-8.0886300  18.167858 0) {self.P_imp} fill={self.coreConfigDict["F"][29]} $\n' \
                          f'630 0 10 -11 -20 trcl=(-4.1348660  19.452590 0) {self.P_imp} fill={self.coreConfigDict["F"][30]} $\n'