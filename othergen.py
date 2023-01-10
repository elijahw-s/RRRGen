import genfuncs

class lsGen():
    def __init__(self,
                 P_imp=None):           # which particles are being traced
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport

        self.airDensity = 0.001225      # g/cm3
        self.alDensity = 2.70           # g/cm3

        self.enclosure = ''
        self.sampleHolders = 'c ------ Rotary rack Sample Holders\n'

        self.getCellCard()

    def getCellCard(self):
        '''
        Generates Cell cards for each ls sample tube
        '''
        self.enclosure += 'c ------ Rotary rack enclosure\n' \
                          'c\n' \
                         f'12012  103  -{"{:.2f}".format(self.alDensity)}      122309 -122310  121390 -121305   {self.P_imp}   $ Top cap of enclosure\n' \
                         f'12013  103  -{"{:.2f}".format(self.alDensity)}      122306 -122309  121390 -121391   {self.P_imp}   $ Lip wall of enclosure\n' \
                         f'12014  103  -{"{:.2f}".format(self.alDensity)}      122304 -122309  121392 -121305   {self.P_imp}   $ Outer wall of enclosure\n' \
                         f'12015  103  -{"{:.2f}".format(self.alDensity)}      122306 -122308  121391 -121393   {self.P_imp}   $ Bottom of LS lip\n' \
                         f'12016  103  -{"{:.2f}".format(self.alDensity)}      122304 -122306  121304 -121393   {self.P_imp}   $ Inner wall of enclosure\n' \
                         f'12017  103  -{"{:.2f}".format(self.alDensity)}      122304 -122307  121393 -121392   {self.P_imp}   $ Bottom wall of enclosure\n' \
                          'c\n' \
                         f'12018  101  -{self.airDensity}  122307 -122311  121393 -121392   {self.P_imp}   $ Air under specimen holders\n' \
                         f'12019  101  -{self.airDensity}  122315 -122309  121391 -121392   {self.P_imp}   $ Air above rotary rack\n' \
                         f'12020  101  -{self.airDensity}  122313 -122315  121395 -121392   {self.P_imp}   $ Air around rack \n' \
                         f'12021  101  -{self.airDensity}  122308 -122313  121391 -121393   {self.P_imp}   $ Air under rack support annulus\n' \
                          'c\n' \
                         f'12022  103  -{"{:.2f}".format(self.alDensity)}      122313 -122315  121391 -121394   {self.P_imp}   $ Rack support annulus\n'

        for pos in range(1,41):
            pos_str = pos if pos >= 10 else "0" + str(pos)
            rad_0 = (pos-1)%20 if (pos-1)%20 >= 10 else "0" + str((pos-1)%20)   # radial disks appear on opposite ends of the ring, so values for those surfaces are calculated mod(20)
            rad_1 = pos%20 if pos%20 >= 10 else "0" + str(pos%20)
            rad_0_neg = ' ' if (pos - 2) % 40 >= 20 else '-'    # some values in LS cell cards are negative depending on the tube location
            rad_1_neg = ' ' if (pos - 1) % 40 <= 19 else '-'
            tempCard = 'c\nc\n' \
                    f'c ---- Position {pos} ----\n' \
                    'c\n' \
                    f'121{pos_str}  101  -{self.airDensity}    122312 -122314 -1214{pos_str}            {self.P_imp}   $ Air inside sample tube\n' \
                    f'122{pos_str}  103  -{"{:.2f}".format(self.alDensity)}        122311 -122312 -1214{pos_str}            {self.P_imp}   $ Bottom cap of tube\n' \
                    f'123{pos_str}  103  -{"{:.2f}".format(self.alDensity)}        122311 -122314  1214{pos_str} -1214{pos+40}    {self.P_imp}   $ Sample tube\n' \
                    'c\n' \
                    f'124{pos_str}  103  -{"{:.2f}".format(self.alDensity)}        122313  1233{pos_str}  121394 -121395\n' \
                    f'                        {rad_0_neg}1220{rad_0} -122315 {rad_1_neg}1220{rad_1}  1214{pos+40}    {self.P_imp}   $ Sample ring around position\n' \
                    'c\n' \
                    f'125{pos_str}  101  -{self.airDensity}    122314 -122315 -1233{pos_str}  121394\n' \
                    f'                        -121395 {rad_0_neg}1220{rad_0} {rad_1_neg}1220{rad_1}            {self.P_imp}   $ Air above sample tube bevel\n' \
                    'c\n' \
                    f'126{pos_str}  101  -{self.airDensity}    122311 -122313  121393 -121392\n' \
                    f'                         1214{pos+40} {rad_0_neg}1220{rad_0} {rad_1_neg}1220{rad_1}            {self.P_imp}   $ Air around sample tube\n'
            if pos >= 15:
                tempCard += f'c\n127{pos_str}  103  -{"{:.2f}".format(self.alDensity)}       -122314  1214{pos+40} -1233{pos_str}  192350    {self.P_imp}   $ sample tube hole fix\n'
            self.sampleHolders += tempCard

class waterGen():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       P_imp = None,
                       matLibs = None,
                       coreOnly = True):

        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'
        self.tmp = h2o_temp_mev

        self.matLibs = matLibs if matLibs else None

        self.coreOnly = coreOnly

        self.coreWaterCells = ''
        self.waterUniverse = ''
        self.testCell = ''
        self.waterMat = ''

        self.getWaterTestCell()
        self.getCoreWaterCells()
        self.getWaterUniverse()
        if self.matLibs:
            self.getWaterMat()
        else:
            print('no mat libs imported to "class waterGen()"')

    def getWaterUniverse(self):
        '''
        These are the water cell equivalent of a fuel element (same parts but each is replaced with water material to make it an empty cell)
        '''
        self.waterUniverse += f'1801 102 -{self.H2ODensity}     312300 -312301 -311302           {self.P_imp} u=18   tmp={self.tmp} $ Lower grid plate pin\n' \
                              f'1802 102 -{self.H2ODensity}     312300 -312301  311302 -311306   {self.P_imp} u=18   tmp={self.tmp} $ Water around grid plate pin\n' \
                              f'1803 102 -{self.H2ODensity}     312301 -312302 -311305           {self.P_imp} u=18   tmp={self.tmp} $ Bottom casing\n' \
                              f'1804 102 -{self.H2ODensity}     312301 -312306  311305 -311306   {self.P_imp} u=18   tmp={self.tmp} $ Water around fuel element\n' \
                              f'1805 102 -{self.H2ODensity}     312302 -312303 -311304           {self.P_imp} u=18   tmp={self.tmp} $ Lower graphite slug\n' \
                              f'1806 102 -{self.H2ODensity}     312302 -312305  311304 -311305   {self.P_imp} u=18   tmp={self.tmp} $ Fuel cladding\n' \
                              f'1807 102 -{self.H2ODensity}     312303 -312304 -311301           {self.P_imp} u=18   tmp={self.tmp} $ Zirc pin\n' \
                              f'1808 102 -{self.H2ODensity}     312303 -302303  311301 -311304   {self.P_imp} u=18   tmp={self.tmp} $ Fuel meat section 1\n' \
                              f'1809 102 -{self.H2ODensity}     302303 -302306  311301 -311304   {self.P_imp} u=18   tmp={self.tmp} $ Fuel meat section 2\n' \
                              f'1810 102 -{self.H2ODensity}     302306 -302309  311301 -311304   {self.P_imp} u=18   tmp={self.tmp} $ Fuel meat section 3\n' \
                              f'1811 102 -{self.H2ODensity}     302309 -302312  311301 -311304   {self.P_imp} u=18   tmp={self.tmp} $ Fuel meat section 4\n' \
                              f'1812 102 -{self.H2ODensity}     302312 -312304  311301 -311304   {self.P_imp} u=18   tmp={self.tmp} $ Fuel meat section 5\n' \
                              f'1813 102 -{self.H2ODensity}     312304 -312305 -311304           {self.P_imp} u=18   tmp={self.tmp} $ Upper graphite spacer\n' \
                              f'1814 102 -{self.H2ODensity}     312305 -312306 -311305           {self.P_imp} u=18   tmp={self.tmp} $ SS top cap\n' \
                              f'1815 102 -{self.H2ODensity}     312306 -312307 -311303           {self.P_imp} u=18   tmp={self.tmp} $ Tri-flute\n' \
                              f'1816 102 -{self.H2ODensity}     312306 -312307  311303 -311306   {self.P_imp} u=18   tmp={self.tmp} $ Water around tri-flute\n' \
                              f'1817 102 -{self.H2ODensity}     312307 -312308 -311302           {self.P_imp} u=18   tmp={self.tmp} $ Fuel tip\n' \
                              f'1818 102 -{self.H2ODensity}     312307 -312308  311302 -311306   {self.P_imp} u=18   tmp={self.tmp} $ Water around fuel tip\n' \
                              f'1819 102 -{self.H2ODensity}     312308 -312309 -311306           {self.P_imp} u=18   tmp={self.tmp} $ Water above fuel element\n'

    def getCoreWaterCells(self):
        self.coreWaterCells += 'c ------ Replacement water for debugging\n' \
                               'c\n' \
                              f'13501  102  -{self.H2ODensity}   10     -112304  111397 -131302\n' \
                              f'                   902019  902029  902039  902049  902059  902069   {self.P_imp}   tmp={self.tmp} $ Inner core water B ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13502  102  -{self.H2ODensity}   10     -112304  131302 -131303\n' \
                               '                   903019  903029  903039  903049  903059  903069\n' \
                              f'                   903079  903089  903099  903109  903119  903129   {self.P_imp}   tmp={self.tmp} $ Inner core water C ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13503  102  -{self.H2ODensity}   10     -112304  131303 -131304\n' \
                               '                   904019  904029  904039  904049  904059  904069\n' \
                               '                   904079  904089  904099  904109  904119  904129\n' \
                              f'                   904139  904149  904159  904169  904179  904189   {self.P_imp}   tmp={self.tmp} $ Inner core water D ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13504  102  -{self.H2ODensity}   10     -112304  131304 -131305\n' \
                               '                   905019  905029  905039  905049  905059  905069\n' \
                               '                   905079  905089  905099  905109  905119  905129\n' \
                               '                   905139  905149  905159  905169  905179  905189\n' \
                              f'                   905199  905209  905219  905229  905239  905249   {self.P_imp}   tmp={self.tmp} $ Inner core water E ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13505  102  -{self.H2ODensity}   10     -112304  131305 -121301\n' \
                               '                   906019  906029  906039  906049  906059  906069\n' \
                               '                   906079  906089  906099  906109  906119  906129\n' \
                               '                   906139  906149  906159  906169  906179  906189\n' \
                               '                   906199  906209  906219  906229  906239  906249\n' \
                              f'                   906259  906269  906279  906289  906299  906309   {self.P_imp}   tmp={self.tmp} $ Inner core water E ring\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                              f'13601  102  -{self.H2ODensity}   112305 -11      111397 -131302\n' \
                              f'                   902019  902029  902039  902049  902059  902069   {self.P_imp}   tmp={self.tmp} $ Upper core water B ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13602  102  -{self.H2ODensity}   112305 -11      131302 -131303\n' \
                               '                   903019  903029  903039  903049  903059  903069\n' \
                              f'                   903079  903089  903099  903109  903119  903129   {self.P_imp}   tmp={self.tmp} $ Upper core water C ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13603  102  -{self.H2ODensity}   112305 -11      131303 -131304\n' \
                               '                   904019  904029  904039  904049  904059  904069\n' \
                               '                   904079  904089  904099  904109  904119  904129\n' \
                              f'                   904139  904149  904159  904169  904179  904189   {self.P_imp}   tmp={self.tmp} $ Upper core water D ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13604  102  -{self.H2ODensity}   112305 -11      131304 -131305  501307\n' \
                               '                   905019  905029  905039  905049  905059  905069\n' \
                               '                   905079  905089  905099  905109  905119  905129\n' \
                               '                   905139  905149  905159  905169  905179  905189\n' \
                              f'                   905199  905209  905219  905229  905239  905249   {self.P_imp}   tmp={self.tmp} $ Upper core water E ring\n' \
                               'c\n' \
                               'c\n' \
                              f'13605  102  -{self.H2ODensity}   112305 -11      131305 -121390\n' \
                               '                   906019  906029  906039  906049  906059  906069\n' \
                               '                   906079  906089  501307  906109  906119  906129\n' \
                               '                   906139  906149  906159  906169  906179  906189\n' \
                               '                   906199  906209  906219  906229  906239  906249\n' \
                              f'                   906259  906269  906279  906289  906299  906309   {self.P_imp}   tmp={self.tmp} $ Upper core water E ring\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                               'c\n' \
                               'c ------ Main outer core water cells\n' \
                               'c\n' \
                               'c\n' \
                              f'13301  102   -{self.H2ODensity}   11     {"-192301" if self.coreOnly else "-130002"}  111397 -121390  \n' \
                              f'                  903059  903099  905019  501307     {self.P_imp} tmp={self.tmp} $ Water above upper grid plate\n' \
                               'c\n' \
                              f'13302  102   -{self.H2ODensity}   122306 -112304  121301 -121390     {self.P_imp}   tmp={self.tmp} $ Water under upper grid plate\n' \
                              f'13303  102   -{self.H2ODensity}   112304 -112305  111399 -121390     {self.P_imp}   tmp={self.tmp} $ Water above upper grid plate\n' \
                               'c\n' \
                              f'13304  102   -{self.H2ODensity}   122310 {"-192301" if self.coreOnly else "-130002"}  121390 -121305     {self.P_imp}   tmp={self.tmp} $ Water above LS assy\n' \
                              f'13305  102   -{self.H2ODensity}   122306 {"-192301" if self.coreOnly else "-130002"}  121305 -121308     {self.P_imp}   tmp={self.tmp} $ Water above outer section of reflector assy\n' \
                              f'13306  102   -{self.H2ODensity}   {"192399" if self.coreOnly else "130001"} {"-192301" if self.coreOnly else "-130002"}  121308 -{"130003" if self.coreOnly else "191301"}\n' \
                               '                   (150001:-150002:150011)\n' \
                               '                   (150001:-150002:150021)\n' \
                               '                   (150001:-150002:150031)\n' \
                              f'                   (150001:-150002:150041)                {self.P_imp}   tmp={self.tmp} $ Water around reflector assy\n' \
                               'c\n' \
                              f'13307  102   -{self.H2ODensity}   {"192399" if self.coreOnly else "130001"} -112301  111397 -121308     {self.P_imp}   tmp={self.tmp} $ Water below lower grid plate\n' \
                              f'13308  102   -{self.H2ODensity}   112301 -122301  121301 -121308     {self.P_imp}   tmp={self.tmp} $ Water below reflector assy\n' \
                              f'13309  102   -{self.H2ODensity}   112301 -10      111398 -121301     {self.P_imp}   tmp={self.tmp} $ Water around lower grid plate\n' \
                               'c\n'
        if not self.coreOnly:
            self.coreWaterCells +=  f'13310  102   -{self.H2ODensity}   (-130051:-130052:-130053) 130003   {self.P_imp}   tmp={self.tmp} $ Rest of pool water\n' \
                               'c\n'

    def getWaterTestCell(self):
        self.testCell += f'2000 102 -{self.H2ODensity} 312300 -312309 -311306 {self.P_imp} u=2 tmp={self.tmp} $ Water test cell\n'

    def getWaterMat(self):
        self.waterMat += 'c ------ Water\n' \
                         'c\n' \
                         'c   Water inside and outside the core, under the control rods, and inside the CT\n' \
                         'c   Assumed to be (1/3) Oxygen and (2/3) Hydrogen\n' \
                         'c\n' \
                         'c\n' \
                        f'm102   {self.matLibs["H"]} 2.0000\n' \
                        f'       {self.matLibs["O"]} 1.0000\n' \
                         'c\n' \
                        f'mt102  {self.matLibs["H2O"]}\n'

class gridPlatesGen():
    def __init__(self, P_imp = None):
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.alDensity = 2.70

        self.gridPlates = ''
        self.altLowerPlate = ''

        self.getGridPlates()
        self.getAltLowerPlate()

    def getGridPlates(self):
        self.gridPlates += 'c ------ Upper grid plate\n' \
                           'c\n' \
                          f'11001   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132008 -132034  111300 -131302\n' \
                          f'      902019                                                         {self.P_imp}  $ Upper grid plate above B1\n' \
                           'c\n' \
                          f'11002   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132008 -132021  111300 -131302\n' \
                          f'      902029  111312                                                 {self.P_imp}  $ Upper grid plate above B2\n' \
                           'c\n' \
                          f'11003   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132034  132021  111300 -131302\n' \
                          f'      902039  111312  111307  111306                                 {self.P_imp}  $ Upper grid plate above B3\n' \
                           'c\n' \
                          f'11004   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132008  132034  111300 -131302\n' \
                          f'      902049                                                         {self.P_imp}  $ Upper grid plate above B4\n' \
                           'c\n' \
                          f'11005   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132008  132021  111300 -131302\n' \
                          f'      902059  111301                                                 {self.P_imp}  $ Upper grid plate above B5\n' \
                           'c\n' \
                          f'11006   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132034 -132021  111300 -131302\n' \
                          f'      902069  111301                                                 {self.P_imp}  $ Upper grid plate above B6\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                          f'11007   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132037 -132005  131302 -131303\n' \
                          f'      903019                                                         {self.P_imp}  $ Upper grid plate above C1\n' \
                           'c\n' \
                          f'11008   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132005 -132011  131302 -131303\n' \
                          f'      903029                                                         {self.P_imp}  $ Upper grid plate above C2\n' \
                           'c\n' \
                          f'11009   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132011 -132018  131302 -131303\n' \
                          f'      903039                                                         {self.P_imp}  $ Upper grid plate above C3\n' \
                           'c\n' \
                          f'11010   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132018 -132024  131302 -131303\n' \
                          f'      903049  111307                                                 {self.P_imp}  $ Upper grid plate above C4\n' \
                           'c\n' \
                          f'11011   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132024 -132031  131302 -131303\n' \
                          f'      903059  111306  111307  111308                                 {self.P_imp}  $ Upper grid plate above C5\n' \
                           'c\n' \
                          f'11012   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132031 -132037  131302 -131303\n' \
                          f'      903069  111306                                                 {self.P_imp}  $ Upper grid plate above C6\n' \
                           'c\n' \
                          f'11013   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132037  132005  131302 -131303\n' \
                          f'      903079                                                         {self.P_imp}  $ Upper grid plate above C7\n' \
                           'c\n' \
                          f'11014   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132005  132011  131302 -131303\n' \
                          f'      903089                                                         {self.P_imp}  $ Upper grid plate above C8\n' \
                           'c\n' \
                          f'11015   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132011  132018  131302 -131303\n' \
                          f'      903099                                                         {self.P_imp}  $ Upper grid plate above C9\n' \
                           'c\n' \
                          f'11016   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132018  132024  131302 -131303\n' \
                          f'      903109                                                         {self.P_imp}  $ Upper grid plate above C10\n' \
                           'c\n' \
                          f'11017   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132024  132031  131302 -131303\n' \
                          f'      903119                                                         {self.P_imp}  $ Upper grid plate above C11\n' \
                           'c\n' \
                          f'11018   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132031  132037  131302 -131303\n' \
                          f'      903129                                                         {self.P_imp}  $ Upper grid plate above C12\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                          f'11019   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132004 -132038  131303 -131304\n' \
                          f'      904019                                                         {self.P_imp}  $ Upper grid plate above D1\n' \
                           'c\n' \
                          f'11020   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132004 -132008  131303 -131304\n' \
                          f'      904029                                                         {self.P_imp}  $ Upper grid plate above D2\n' \
                           'c\n' \
                          f'11021   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132008 -132012  131303 -131304\n' \
                          f'      904039                                                         {self.P_imp}  $ Upper grid plate above D3\n' \
                           'c\n' \
                          f'11022   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132012 -132017  131303 -131304\n' \
                          f'      904049                                                         {self.P_imp}  $ Upper grid plate above D4\n' \
                           'c\n' \
                          f'11023   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132017 -132021  131303 -131304\n' \
                          f'      904059  111313  111314                                         {self.P_imp}  $ Upper grid plate above D5\n' \
                           'c\n' \
                          f'11024   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132021 -132025  131303 -131304\n' \
                          f'      904069  111308  111309  111313  111314                         {self.P_imp}  $ Upper grid plate above D6\n' \
                           'c\n' \
                          f'11025   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132025 -132030  131303 -131304\n' \
                          f'      904079  111308  111309                                         {self.P_imp}  $ Upper grid plate above D7\n' \
                           'c\n' \
                          f'11026   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132030 -132034  131303 -131304\n' \
                          f'      904089                                                         {self.P_imp}  $ Upper grid plate above D8\n' \
                           'c\n' \
                          f'11027   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132034 -132038  131303 -131304\n' \
                          f'      904099                                                         {self.P_imp}  $ Upper grid plate above D9\n' \
                           'c\n' \
                          f'11028   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132004  132038  131303 -131304\n' \
                          f'      904109                                                         {self.P_imp}  $ Upper grid plate above D10\n' \
                           'c\n' \
                          f'11029   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132004  132008  131303 -131304\n' \
                          f'      904119                                                         {self.P_imp}  $ Upper grid plate above D11\n' \
                           'c\n' \
                          f'11030   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132008  132012  131303 -131304\n' \
                          f'      904129                                                         {self.P_imp}  $ Upper grid plate above D12\n' \
                           'c\n' \
                          f'11031   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132012  132017  131303 -131304\n' \
                          f'      904139                                                         {self.P_imp}  $ Upper grid plate above D13\n' \
                           'c\n' \
                          f'11032   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132017  132021  131303 -131304\n' \
                          f'      904149  111302  111303                                         {self.P_imp}  $ Upper grid plate above D14\n' \
                           'c\n' \
                          f'11033   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132021  132025  131303 -131304\n' \
                          f'      904159  111302  111303                                         {self.P_imp}  $ Upper grid plate above D15\n' \
                           'c\n' \
                          f'11034   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132025  132030  131303 -131304\n' \
                          f'      904169                                                         {self.P_imp}  $ Upper grid plate above D16\n' \
                           'c\n' \
                          f'11035   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132030  132034  131303 -131304\n' \
                          f'      904179                                                         {self.P_imp}  $ Upper grid plate above D17\n' \
                           'c\n' \
                          f'11036   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132034  132038  131303 -131304\n' \
                          f'      904189                                                         {self.P_imp}  $ Upper grid plate above D18\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                          f'11037   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132003 -132039  131304 -131305\n' \
                          f'      905019                                                         {self.P_imp}  $ Upper grid plate above E1\n' \
                           'c\n' \
                          f'11038   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132003 -132007  131304 -131305\n' \
                          f'      905029                                                         {self.P_imp}  $ Upper grid plate above E2\n' \
                           'c\n' \
                          f'11039   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132007 -132009  131304 -131305\n' \
                          f'      905039                                                         {self.P_imp}  $ Upper grid plate above E3\n' \
                           'c\n' \
                          f'11040   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132009 -132013  131304 -131305\n' \
                          f'      905049                                                         {self.P_imp}  $ Upper grid plate above E4\n' \
                           'c\n' \
                          f'11041   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132013 -132016  131304 -131305\n' \
                          f'      905059                                                         {self.P_imp}  $ Upper grid plate above E5\n' \
                           'c\n' \
                          f'11042   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132016 -132020  131304 -131305\n' \
                          f'      905069                                                         {self.P_imp}  $ Upper grid plate above E6\n' \
                           'c\n' \
                          f'11043   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132020 -132022  131304 -131305\n' \
                          f'      905079                                                         {self.P_imp}  $ Upper grid plate above E7\n' \
                           'c\n' \
                          f'11044   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132022 -132026  131304 -131305\n' \
                          f'      905089  111309  111310                                         {self.P_imp}  $ Upper grid plate above E8\n' \
                           'c\n' \
                          f'11045   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132026 -132029  131304 -131305\n' \
                          f'      905099  111309  111310                                         {self.P_imp}  $ Upper grid plate above E9\n' \
                           'c\n' \
                          f'11046   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132029 -132033  131304 -131305\n' \
                          f'      905109                                                         {self.P_imp}  $ Upper grid plate above E10\n' \
                           'c\n' \
                          f'11047   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132033 -132035  131304 -131305\n' \
                          f'      905119                                                         {self.P_imp}  $ Upper grid plate above E11\n' \
                           'c\n' \
                          f'11048   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132035 -132039  131304 -131305\n' \
                          f'      905129                                                         {self.P_imp}  $ Upper grid plate above E12\n' \
                           'c\n' \
                          f'11049   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132003  132039  131304 -131305\n' \
                          f'      905139                                                         {self.P_imp}  $ Upper grid plate above E13\n' \
                           'c\n' \
                          f'11050   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132003  132007  131304 -131305\n' \
                          f'      905149                                                         {self.P_imp}  $ Upper grid plate above E14\n' \
                           'c\n' \
                          f'11051   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132007  132009  131304 -131305\n' \
                          f'      905159                                                         {self.P_imp}  $ Upper grid plate above E15\n' \
                           'c\n' \
                          f'11052   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132009  132013  131304 -131305\n' \
                          f'      905169                                                         {self.P_imp}  $ Upper grid plate above E16\n' \
                           'c\n' \
                          f'11053   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132013  132016  131304 -131305\n' \
                          f'      905179                                                         {self.P_imp}  $ Upper grid plate above E17\n' \
                           'c\n' \
                          f'11054   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132016  132020  131304 -131305\n' \
                          f'      905189                                                         {self.P_imp}  $ Upper grid plate above E18\n' \
                           'c\n' \
                          f'11055   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132020  132022  131304 -131305\n' \
                          f'      905199                                                         {self.P_imp}  $ Upper grid plate above E19\n' \
                           'c\n' \
                          f'11056   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132022  132026  131304 -131305\n' \
                          f'      905209                                                         {self.P_imp}  $ Upper grid plate above E20\n' \
                           'c\n' \
                          f'11057   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132026  132029  131304 -131305\n' \
                          f'      905219                                                         {self.P_imp}  $ Upper grid plate above E21\n' \
                           'c\n' \
                          f'11058   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132029  132033  131304 -131305\n' \
                          f'      905229                                                         {self.P_imp}  $ Upper grid plate above E22\n' \
                           'c\n' \
                          f'11059   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132033  132035  131304 -131305\n' \
                          f'      905239                                                         {self.P_imp}  $ Upper grid plate above E23\n' \
                           'c\n' \
                          f'11060   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132035  132039  131304 -131305\n' \
                          f'      905249                                                         {self.P_imp}  $ Upper grid plate above E24\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                           'c\n' \
                          f'11061   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132040 -132002  131305 -111399\n' \
                          f'      906019                                                         {self.P_imp}  $ Upper grid plate above F1\n' \
                           'c\n' \
                          f'11062   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132002 -132006  131305 -111399\n' \
                          f'      906029                                                         {self.P_imp}  $ Upper grid plate above F2\n' \
                           'c\n' \
                          f'11063   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132006 -132008  131305 -111399\n' \
                          f'      906039                                                         {self.P_imp}  $ Upper grid plate above F3\n' \
                           'c\n' \
                          f'11064   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132008 -132010  131305 -111399\n' \
                          f'      906049                                                         {self.P_imp}  $ Upper grid plate above F4\n' \
                           'c\n' \
                          f'11065   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132010 -132014  131305 -111399\n' \
                          f'      906059                                                         {self.P_imp}  $ Upper grid plate above F5\n' \
                           'c\n' \
                          f'11066   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132014 -132015  131305 -111399\n' \
                          f'      906069                                                         {self.P_imp}  $ Upper grid plate above F6\n' \
                           'c\n' \
                          f'11067   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132015 -132019  131305 -111399\n' \
                          f'      906079  111316                                                 {self.P_imp}  $ Upper grid plate above F7\n' \
                           'c\n' \
                          f'11068   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132019 -132021  131305 -111399\n' \
                          f'      906089  111315  111316                                         {self.P_imp}  $ Upper grid plate above F8\n' \
                           'c\n' \
                          f'11069   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132021 -132023  131305 -111399\n' \
                          f'      906099  111315                                                 {self.P_imp}  $ Upper grid plate above F9\n' \
                           'c\n' \
                          f'11070   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132023 -132027  131305 -111399\n' \
                          f'      906109  111310  111311                                         {self.P_imp}  $ Upper grid plate above F10\n' \
                           'c\n' \
                          f'11071   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132027 -132028  131305 -111399\n' \
                          f'      906119  111310  111311                                         {self.P_imp}  $ Upper grid plate above F11\n' \
                           'c\n' \
                          f'11072   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132028 -132032  131305 -111399\n' \
                          f'      906129                                                         {self.P_imp}  $ Upper grid plate above F12\n' \
                           'c\n' \
                          f'11073   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132032 -132034  131305 -111399\n' \
                          f'      906139                                                         {self.P_imp}  $ Upper grid plate above F13\n' \
                           'c\n' \
                          f'11074   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132034 -132036  131305 -111399\n' \
                          f'      906149                                                         {self.P_imp}  $ Upper grid plate above F14\n' \
                           'c\n' \
                          f'11075   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132036 -132040  131305 -111399\n' \
                          f'      906159                                                         {self.P_imp}  $ Upper grid plate above F15\n' \
                           'c\n' \
                          f'11076   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305  132040  132002  131305 -111399\n' \
                          f'      906169                                                         {self.P_imp}  $ Upper grid plate above F16\n' \
                           'c\n' \
                          f'11077   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132002  132006  131305 -111399\n' \
                          f'      906179                                                         {self.P_imp}  $ Upper grid plate above F17\n' \
                           'c\n' \
                          f'11078   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132006  132008  131305 -111399\n' \
                          f'      906189                                                         {self.P_imp}  $ Upper grid plate above F18\n' \
                           'c\n' \
                          f'11079   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132008  132010  131305 -111399\n' \
                          f'      906199                                                         {self.P_imp}  $ Upper grid plate above F19\n' \
                           'c\n' \
                          f'11080   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132010  132014  131305 -111399\n' \
                          f'      906209                                                         {self.P_imp}  $ Upper grid plate above F20\n' \
                           'c\n' \
                          f'11081   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132014  132015  131305 -111399\n' \
                          f'      906219                                                         {self.P_imp}  $ Upper grid plate above F21\n' \
                           'c\n' \
                          f'11082   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132015  132019  131305 -111399\n' \
                          f'      906229  111305                                                 {self.P_imp}  $ Upper grid plate above F22\n' \
                           'c\n' \
                          f'11083   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132019  132021  131305 -111399\n' \
                          f'      906239  111304  111305                                         {self.P_imp}  $ Upper grid plate above F23\n' \
                           'c\n' \
                          f'11084   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132021  132023  131305 -111399\n' \
                          f'      906249  111304                                                 {self.P_imp}  $ Upper grid plate above F24\n' \
                           'c\n' \
                          f'11085   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132023  132027  131305 -111399\n' \
                          f'      906259                                                         {self.P_imp}  $ Upper grid plate above F25\n' \
                           'c\n' \
                          f'11086   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132027  132028  131305 -111399\n' \
                          f'      906269                                                         {self.P_imp}  $ Upper grid plate above F26\n' \
                           'c\n' \
                          f'11087   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132028  132032  131305 -111399\n' \
                          f'      906279                                                         {self.P_imp}  $ Upper grid plate above F27\n' \
                           'c\n' \
                          f'11088   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132032  132034  131305 -111399\n' \
                          f'      906289                                                         {self.P_imp}  $ Upper grid plate above F28\n' \
                           'c\n' \
                          f'11089   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132034  132036  131305 -111399\n' \
                          f'      906299                                                         {self.P_imp}  $ Upper grid plate above F20\n' \
                           'c\n' \
                          f'11090   103  -{"{:.2f}".format(self.alDensity)}  112304 -112305 -132036  132040  131305 -111399\n' \
                          f'      906309                                                         {self.P_imp}  $ Upper grid plate above F30\n'

    def getAltLowerPlate(self):
        self.altLowerPlate += 'c ------ Alternate lower grid plate for error reduction\n' \
                              'c\n' \
                             f'77001  103  -{"{:.2f}".format(self.alDensity)}  112301 -10  111397 -131302   {self.P_imp}   $ Lower grid plate B ring\n' \
                             f'77002  103  -{"{:.2f}".format(self.alDensity)}  112301 -10  131302 -131303   {self.P_imp}   $ Lower grid plate C ring\n' \
                             f'77003  103  -{"{:.2f}".format(self.alDensity)}  112301 -10  131303 -131304   {self.P_imp}   $ Lower grid plate D ring\n' \
                             f'77004  103  -{"{:.2f}".format(self.alDensity)}  112301 -10  131304 -131305   {self.P_imp}   $ Lower grid plate E ring\n' \
                             f'77005  103  -{"{:.2f}".format(self.alDensity)}  112301 -10  131305 -111398   {self.P_imp}   $ Lower grid plate E ring\n'

class graphiteReflector():
    def __init__(self, P_imp = None):

        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.alDensity = 2.70
        self.graphiteDensity = 1.60

        self.reflectorCells = ''

        self.getReflectorCells()

    def getReflectorCells(self):
        self.reflectorCells += f'12001  106  -{"{:.2f}".format(self.graphiteDensity)}      122302 -122305  121302 -121303   {self.P_imp}  $ Inner graphite blank\n' \
                               f'12002  106  -{"{:.2f}".format(self.graphiteDensity)}      122302 -122303  121303 -121306   {self.P_imp}  $ LS channel region graphite blank\n' \
                               f'12003  106  -{"{:.2f}".format(self.graphiteDensity)}      122302 -122305  121306 -121307   {self.P_imp}  $ Outer graphite blank\n' \
                                'c\n' \
                               f'12004  103  -{"{:.2f}".format(self.alDensity)}      122301 -122306  121301 -121302   {self.P_imp}  $ Inner reflector container wall\n' \
                               f'12005  103  -{"{:.2f}".format(self.alDensity)}      122303 -122306  121303 -121304   {self.P_imp}  $ Inner LS channel container wall\n' \
                               f'12006  103  -{"{:.2f}".format(self.alDensity)}      122303 -122306  121305 -121306   {self.P_imp}  $ Outer LS channel container wall\n' \
                               f'12007  103  -{"{:.2f}".format(self.alDensity)}      122301 -122306  121307 -121308   {self.P_imp}  $ Outer reflector assembly container wall\n' \
                                'c\n' \
                               f'12008  103  -{"{:.2f}".format(self.alDensity)}      122301 -122302  121302 -121307   {self.P_imp}  $ Reflector assembly bottom container annulus \n' \
                               f'12009  103  -{"{:.2f}".format(self.alDensity)}      122305 -122306  121302 -121303   {self.P_imp}  $ Reflector assembly top inner container annulus\n' \
                               f'12010  103  -{"{:.2f}".format(self.alDensity)}      122303 -122304  121304 -121305   {self.P_imp}  $ LS channel bottom container annulus\n' \
                               f'12011  103  -{"{:.2f}".format(self.alDensity)}      122305 -122306  121306 -121307   {self.P_imp}  $ Reflector assembly top outer container annulus\n'

class centralThimbleGen():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       CT_open = False,
                       P_imp = None,
                       coreOnly = True):

        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'
        self.CT_open = CT_open
        self.tmp = h2o_temp_mev

        self.coreOnly = coreOnly

        self.alDensity = 2.70
        self.nDensity = 0.0012506

        self.ctCells = ''

        self.getCT()

    def getCT(self):
        self.ctCells += f'14000  103   -{"{:.2f}".format(self.alDensity)}        142302 {"-192301" if self.coreOnly else "-130002"}  141300 -111300   {self.P_imp}                    $ Central thimble main tube\n' \
                        f'14001  102   -{self.H2ODensity}    142302 -142303 -141300           {self.P_imp}   tmp={self.tmp} $ Central thimble inevacuable water\n' \
                         'c\n'
        if self.CT_open:    # uses a line with materal as nitrogen if the beam is open      (m7=elemental nitrogen) src:https://www.osti.gov/servlets/purl/1323135
            self.ctCells += f'14002  7     -{self.nDensity}   142303 {"-192301" if self.coreOnly else "-130002"} -141300           {self.P_imp}                    $ Evacuated water replaced with nitrogen in central thimble\n'
        else:               # otherwise the would be beam is filled with water
            self.ctCells += f'14002  102   -{self.H2ODensity}    142303 -192301 -141300           {self.P_imp}   tmp={self.tmp} $ Central thimble evacuable water\n'
        self.ctCells += 'c\n' \
                       f'14003  103   -{"{:.2f}".format(self.alDensity)}        142301 -142302 -111300           {self.P_imp}                    $ Central thimble bottom cap\n' \
                       f'14004  102   -{self.H2ODensity}    142301 -112304  111300 -111397   {self.P_imp}   tmp={self.tmp} $ Water around central thimble below upper grid plate\n' \
                       f'14005  102   -{self.H2ODensity}    112305 {"-192301" if self.coreOnly else "-130002"}  111300 -111397   {self.P_imp}   tmp={self.tmp} $ Water around central thimble above upper grid plate\n' \
                       f'14006  102   -{self.H2ODensity}    {"192399" if self.coreOnly else "130001"}-142301 -111397           {self.P_imp}   tmp={self.tmp} $ Water below central thimble\n'

class fluxWires():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       P_imp = None):
        
        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'
        self.tmp = h2o_temp_mev

        self.fluxWireCard = ''

        self.getFluxWires()

    def getFluxWires(self):
        self.fluxWireCard += f'17001  102  -{self.H2ODensity}  -111301  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole A  upper grid area\n' \
                             f'17002  102  -{self.H2ODensity}  -111302  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole B  upper grid area\n' \
                             f'17003  102  -{self.H2ODensity}  -111303  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole C  upper grid area\n' \
                             f'17004  102  -{self.H2ODensity}  -111304  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole D  upper grid area\n' \
                             f'17005  102  -{self.H2ODensity}  -111305  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole E  upper grid area\n' \
                             f'17006  102  -{self.H2ODensity}  -111306  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole F  upper grid area\n' \
                             f'17007  102  -{self.H2ODensity}  -111307  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole G  upper grid area\n' \
                             f'17008  102  -{self.H2ODensity}  -111308  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole H  upper grid area\n' \
                             f'17009  102  -{self.H2ODensity}  -111309  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole J  upper grid area\n' \
                             f'17010  102  -{self.H2ODensity}  -111310  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole K  upper grid area\n' \
                             f'17011  102  -{self.H2ODensity}  -111311  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole L  upper grid area\n' \
                             f'17012  102  -{self.H2ODensity}  -111312  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole A1 upper grid area\n' \
                             f'17013  102  -{self.H2ODensity}  -111313  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole B1 upper grid area\n' \
                             f'17014  102  -{self.H2ODensity}  -111314  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole C1 upper grid area\n' \
                             f'17015  102  -{self.H2ODensity}  -111315  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole D1 upper grid area\n' \
                             f'17016  102  -{self.H2ODensity}  -111316  112304 -112305  {self.P_imp} tmp={self.tmp} $ Flux wire insertion hole E1 upper grid area\n'

class poolHousing():
    def __init__(self, P_imp=None):
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.alDensity = 2.70
        self.ccDensity = 2.30

        self.housingCells = ''
        
        self.getHousing()

    def getHousing(self):
        self.housingCells += f'15001  103  -{"{:.2f}".format(self.alDensity)}    (-132101:-132102:-132103)  130051  130052  130053   {self.P_imp}  $ Aluminum shell\n' \
                             f'15002   97  -{self.ccDensity}    (-132201:-132202:-132203)  132101  132102  132103   {self.P_imp}  $ Concrete shell\n'

class rabbit():
    def __init__(self, h2o_density = None,
                       h2o_temp_k = 294, 
                       h2o_temp_mev = 2.533494e-08,
                       h2o_void_percent = 0,
                       rabbit_in = True,
                       P_imp = None):
        
        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_k
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'
        self.tmp = h2o_temp_mev
        self.rabbitIn = rabbit_in

        self.alDensity = 2.70
        self.airDensity = 0.001225
        self.polyDensity = 0.97

        self.rabbitCells = ''

        self.getRabbitAl()
        self.getRabbitWater()
        self.getRabbitAir()
        self.getRabbitOther()

    def getRabbitAl(self):
        self.rabbitCells += 'c ------ Aluminum components\n' \
                            'c\n' \
                           f'60901  103  -{"{:.2f}".format(self.alDensity)}  10     -502301 -503301           {self.P_imp}   $ Lower taper \n' \
                           f'60902  103  -{"{:.2f}".format(self.alDensity)}  502301 -502302 -501306           {self.P_imp}   $ Lower section\n' \
                           f'60903  103  -{"{:.2f}".format(self.alDensity)}  502302 -502303 -503302           {self.P_imp}   $ Lower section upper taper\n' \
                            'c\n' \
                           f'60904  103  -{"{:.2f}".format(self.alDensity)}  502303 -502304 -503303           {self.P_imp}   $ Mid section lower taper\n' \
                           f'60905  103  -{"{:.2f}".format(self.alDensity)}  502304 -502305 -501306           {self.P_imp}   $ Mid section\n' \
                           f'60906  103  -{"{:.2f}".format(self.alDensity)}  502305 -502306 -503304           {self.P_imp}   $ Mid section upper taper\n' \
                           f'60907  103  -{"{:.2f}".format(self.alDensity)}  502306 -502307 -501301           {self.P_imp}   $ Upper post\n' \
                           f'60908  103  -{"{:.2f}".format(self.alDensity)}  503304 -502306 -501301           {self.P_imp}   $ Upper post correction             ------ big problems here ---- \n' \
                            'c\n' \
                            'c\n' \
                           f'60909  103  -{"{:.2f}".format(self.alDensity)}  502307 -502308 -501306           {self.P_imp}   $ Main section lower portion\n' \
                           f'60910  103  -{"{:.2f}".format(self.alDensity)}  502308 -502309  501304 -501306   {self.P_imp}   $ Main section lower bezel\n' \
                           f'60911  103  -{"{:.2f}".format(self.alDensity)}  502309 -502310  501305 -501306   {self.P_imp}   $ Main section thin tube\n' \
                           f'60912  103  -{"{:.2f}".format(self.alDensity)}  502310 -192301  501305 -501307   {self.P_imp}   $ Main section thick tube    ------ big problems here ----  \n' \
                            'c\n' \
                           f'60913  103  -{"{:.2f}".format(self.alDensity)}  502311 -502312  501308 -501303   {self.P_imp}   $ Sample holder annulus\n' \
                           f'60914  103  -{"{:.2f}".format(self.alDensity)}  502312 -192301  501302 -501303   {self.P_imp}   $ Inner tube\n'
        self.rabbitCells += genfuncs.make_cs(3)

    def getRabbitWater(self):
        self.rabbitCells += 'c ----- Water components -----\n' \
                            'c\n' \
                           f'60920  102  -{self.H2ODensity}   10     -502301  503301 -906099           {self.P_imp}   tmp={self.tmp} $ Water around lower bevel\n' \
                           f'60921  102  -{self.H2ODensity}   502301 -502302  501306 -906099           {self.P_imp}   tmp={self.tmp} $ Water around lower section\n' \
                           f'60922  102  -{self.H2ODensity}   502302 -502303  503302 -906099           {self.P_imp}   tmp={self.tmp} $ Water around lower section upper bevel\n' \
                           f'60923  102  -{self.H2ODensity}   502303 -502304  503303 -906099           {self.P_imp}   tmp={self.tmp} $ Water around mid section lower bevel\n' \
                           f'60924  102  -{self.H2ODensity}   502304 -502305  501306 -906099           {self.P_imp}   tmp={self.tmp} $ Water around mid section\n' \
                           f'60925  102  -{self.H2ODensity}   502305 -502306  503304 -906099  501301   {self.P_imp}   tmp={self.tmp} $ Water around mid section upper bevel\n' \
                           f'60926  102  -{self.H2ODensity}   502306 -502307  501301 -906099           {self.P_imp}   tmp={self.tmp} $ Water around post\n' \
                           f'60927  102  -{self.H2ODensity}   502307 -502310  501306 -906099           {self.P_imp}   tmp={self.tmp} $ Water around rabbit tube\n' \
                           f'60928  102  -{self.H2ODensity}   112305 -502310  906099 -501307           {self.P_imp}   tmp={self.tmp} $ Water above upper grid plate around thin tube    ----- so many problems -----\n'
        self.rabbitCells += genfuncs.make_cs(3)

    def getRabbitAir(self):
        self.rabbitCells += 'c ------ Air elements\n' \
                            'c\n' \
                           f'60930  101  -{self.airDensity}   502308 -502309 -501304                   {self.P_imp}   $ Air in bezel\n' \
                           f'60931  101  -{self.airDensity}   502309 -502311 -501305                   {self.P_imp}   $ Air under sample holder\n' \
                           f'60932  101  -{self.airDensity}   502311 -502312 -501308                   {self.P_imp}   $ Air in sample holder \n' \
                           f'60933  101  -{self.airDensity}   502311 -192301  501303 -501305           {self.P_imp}   $ Air b/w inside and outside tube\n' \
                            'c\n' \
                           f'42069  101  -{self.airDensity}   552305 -552307 -501311                   {self.P_imp}   $ Air inside inner vial    ----- this is the cell on which to do the F4 tally -----\n' \
                           f'60935  101  -{self.airDensity}   552303 -552308  501312 -501313           {self.P_imp}   $ Air around inner vial\n' \
                           f'60936  101  -{self.airDensity}   552308 -552309 -501313                   {self.P_imp}   $ Air inside outer vial\n' \
                           f'60937  101  -{self.airDensity}   552310 -552314 -501308                   {self.P_imp}   $ Air inside rabbit tube\n' \
                            'c\n' \
                           f'60950  101  -{self.airDensity}   502312 -552304  553301 -501302           {self.P_imp}   $ Air around lower bevel lower section\n' \
                           f'60951  101  -{self.airDensity}   552304 -552306  553302 -501302           {self.P_imp}   $ Air around lower bevel upper section\n' \
                           f'60952  101  -{self.airDensity}   552306 -502313  501301 -501302           {self.P_imp}   $ Air around rabbit tube\n' \
                           f'60953  101  -{self.airDensity}   502313 -552311  501301  553303 -501302   {self.P_imp}   $ Air around upper bevel lower section\n' \
                           f'60954  101  -{self.airDensity}   552311  553303 -501302 -552313           {self.P_imp}   $ Air around upper bevel mid section\n' \
                           f'60955  101  -{self.airDensity}   501317 -552313 -553303  552311 -501302   {self.P_imp}   $ Air around upper bevel top section\n' \
                           f'60956  101  -{self.airDensity}   552313 -552315  501318 -501302           {self.P_imp}   $ Air around rabbit tube cap\n' \
                           f'60957  101  -{self.airDensity}   552315 -192301 -501302                   {self.P_imp}   $ Air in rabbit\n'
        self.rabbitCells += genfuncs.make_cs(3)

    def getRabbitOther(self):
        if self.rabbitIn:
            mat = 109
            den = self.polyDensity
            fill = 'Poly elements'
        else:
            mat = 101
            den = self.airDensity
            fill = 'More air elements'

        self.rabbitCells += f'c ------ {fill}\n' \
                             'c\n' \
                            f'60940  {mat}  -{den}   502312 -552302 -501308                   {self.P_imp}   $ bottom of rabbit tube\n' \
                            f'60941  {mat}  -{den}   502312 -552312  501308 -501301           {self.P_imp}   $ Main section rabbit tube\n' \
                            f'60942  {mat}  -{den}   502312 -552304  501301 -501318 -553301   {self.P_imp}   $ Rabbit tube lower bevel lower section\n' \
                            f'60943  {mat}  -{den}   552304 -552306  501301 -501318 -553302   {self.P_imp}   $ Rabbit tube lower bevel upper section\n' \
                            f'60944  {mat}  -{den}  -552312  501301 -553303  552310 -501317   {self.P_imp}   $ Rabbit tube upper bevel\n' \
                            f'60945  {mat}  -{den}   552312 -552313  501308 -501317           {self.P_imp}   $ Rabbit tube upper section\n' \
                            f'60946  {mat}  -{den}   552314 -552315 -501318                   {self.P_imp}   $ Rabbit tube cap upper section\n' \
                            f'60947  {mat}  -{den}   552313 -552314  501308 -501318           {self.P_imp}   $ Rabbit tube tube\n' \
                             'c\n' \
                            f'60960  {mat}  -{den}   552302 -552303 -501308                   {self.P_imp}   $ Outer vial bottom\n' \
                            f'60961  {mat}  -{den}   552303 -552309  501313 -501308           {self.P_imp}   $ Outer vial tube\n' \
                            f'60962  {mat}  -{den}   552309 -552310 -501308                   {self.P_imp}   $ Outer vial top\n' \
                             'c\n' \
                            f'60963  {mat}  -{den}   552303 -552305 -501312                   {self.P_imp}   $ Inner vial bottom\n' \
                            f'60964  {mat}  -{den}   552305 -552307  501311 -501312           {self.P_imp}   $ Inner vial tube\n' \
                            f'60965  {mat}  -{den}   552307 -552308 -501312                   {self.P_imp}   $ Inner vial top\n'
        
class neutronDetectors():
    def __init__(self, P_imp=None):
        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.alDensity = 2.70

        self.ndCells = ''

        self.getNeutronDetectors()

    def getNeutronDetectors(self):
        self.ndCells += f'70001  103  -{"{:.2f}".format(self.alDensity)}  -150001  150002  -150011  {self.P_imp}  $ NE - linear\n' \
                        f'70002  103  -{"{:.2f}".format(self.alDensity)}  -150001  150002  -150021  {self.P_imp}  $ SE - % power\n' \
                        f'70003  103  -{"{:.2f}".format(self.alDensity)}  -150001  150002  -150031  {self.P_imp}  $ SW - logarithmic\n' \
                        f'70004  103  -{"{:.2f}".format(self.alDensity)}  -150001  150002  -150041  {self.P_imp}  $ NW - empty\n'

class voidCells():
    def __init__(self, P_imp=None, coreOnly=True):
        self.P_imp = f'imp:{",".join(P_imp)}=0' if P_imp else 'imp:n=1'

        self.coreOnly = coreOnly
        
        self.voidCells = ''

        self.getVoidCells()

    def getVoidCells(self):
        if self.coreOnly:
            self.voidCells += f'10001  0  -192399                  {self.P_imp}  $ Void below model\n' \
                              f'10002  0   192399 -192301 -191301  {self.P_imp}  $ Void around model\n' \
                              f'10003  0   192301                  {self.P_imp}  $ Void above model\n'
        else:
            self.voidCells += f'10001  0  -192399                               {self.P_imp}  $ Void below model\n' \
                              f'10002  0   192399 -192301 132201 132202 132203  {self.P_imp}  $ Void around model\n' \
                              f'10003  0   192301                               {self.P_imp}  $ Void above model\n'
