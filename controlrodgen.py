import codesnippets
import genfuncs

class controlRodGen():
    def __init__(self, safeHeight=0,
                       shimHeight=0,
                       regHeight=0,
                       h2o_temp_K=294,
                       h2o_temp_mev=2.533494e-08,
                       h2o_density=None,
                       h2o_void_percent=0,
                       P_imp=None,
                       bank=False,
                       coreOnly = True):

        if bank == True:
            self.safeHeight = self.shimHeight = self.regHeight = max(safeHeight,shimHeight,regHeight)
        else:
            self.safeHeight = safeHeight
            self.shimHeight = shimHeight
            self.regHeight = regHeight

        self.voidPercent = h2o_void_percent
        self.h2o_temp_K = h2o_temp_K
        self.H2ODensity = (1-0.01*self.voidPercent) * h2o_density if h2o_density else (1-0.01*self.voidPercent) * genfuncs.find_h2o_temp_K_density(self.h2o_temp_K)

        self.P_imp = f'imp:{",".join(P_imp)}=1' if P_imp else 'imp:n=1'         # Read in the imput card used for particle transport, if no particles inputted then it is set to 'n'

        self.coreOnly = coreOnly

        self.safeMovement = 0.38 * self.safeHeight
        self.shimMovement = 0.38 * self.shimHeight   #38 inches of total movement so 0.38cm/%
        self.regMovement = 0.38 * self.regHeight

        self.safeSurfaces = f'c\nc Safe Rod ({self.safeHeight}% withdrawn)\nc\n' + codesnippets.safeRodcz
        self.shimSurfaces = f'c\nc Shim Rod ({self.shimHeight}% withdrawn)\nc\n' + codesnippets.shimRodcz
        self.regSurfaces = f'c\nc Reg Rod ({self.regHeight}% withdrawn)\nc\n' + codesnippets.regRodcz

        self.safeCellCard = ''
        self.shimCellCard = ''
        self.regCellCard = ''

        self.alDensity = 2.70
        self.graphiteDensity = 1.698
        self.boronCarbideDensity = 1.80772
        self.tmp = h2o_temp_mev

        self.safePZ()
        self.shimPZ()
        self.regPZ()

        self.safeCell()
        self.shimCell()
        self.regCell()


    def safePZ(self):
        self.safeSurfaces += 'c pz surfaces\n' \
                             'c\n' \
                            f'812301   pz   {"{:.4f}".format(62.8153 + self.safeMovement)}   $ top of control rod\n' \
                            f'812302   pz   {"{:.4f}".format(62.0533 + self.safeMovement)}   $ top of main section\n' \
                            f'812303   pz   {"{:.4f}".format(61.4183 + self.safeMovement)}   $ top of poison portion\n' \
                            f'812304   pz   {"{:.4f}".format(15.4327 + self.safeMovement)}   $ bottom of poison portion\n' \
                            f'812305   pz   {"{:.4f}".format(14.7077 + self.safeMovement)}   $ bottom of main section\n' \
                            f'812306   pz   {"{:.4f}".format(14.3013 + self.safeMovement)}   $ bottom of outer lower cone\n' \
                            f'812307   pz   {"{:.4f}".format(13.7425 + self.safeMovement)}   $ bottom of control rod \n' \
                             'c\n' \
                             'c\n' \
                             'c k/z surfaces\n' \
                             'c\n' \
                            f'813301   k/z   6.91134   -3.99034   {"{:.4f}".format(69.51676 + self.safeMovement)}   0.1877777777   $ upper beveling\n' \
                            f'813302   k/z   6.91134   -3.99034   {"{:.4f}".format(16.55385 + self.safeMovement)}   0.66015625     $ lower outer beveling\n' \
                            f'813303   k/z   6.91134   -3.99034   {"{:.4f}".format(17.5425 + self.safeMovement)}   5.0625         $ lower inner beveling\n' \
                             'c\n' \
                             'c\n' \
                             'c End of Safe Rod'
        
    def shimPZ(self):
        self.shimSurfaces += 'c pz surfaces\n' \
                             'c\n' \
                            f'822301   pz   {"{:.4f}".format(62.8153 + self.shimMovement)}   $ top of control rod\n' \
                            f'822302   pz   {"{:.4f}".format(62.0533 + self.shimMovement)}   $ top of main section\n' \
                            f'822303   pz   {"{:.4f}".format(61.4183 + self.shimMovement)}   $ top of poison portion\n' \
                            f'822304   pz   {"{:.4f}".format(15.4327 + self.shimMovement)}   $ bottom of poison portion\n' \
                            f'822305   pz   {"{:.4f}".format(14.7077 + self.shimMovement)}   $ bottom of main section\n' \
                            f'822306   pz   {"{:.4f}".format(14.3013 + self.shimMovement)}   $ bottom of outer lower cone\n' \
                            f'822307   pz   {"{:.4f}".format(13.7425 + self.shimMovement)}   $ bottom of control rod \n' \
                             'c\n' \
                             'c\n' \
                             'c k/z surfaces\n' \
                             'c\n' \
                            f'823301   k/z   -6.91134   -3.99034   {"{:.4f}".format(69.51676 + self.safeMovement)}   0.1877777777   $ upper beveling\n' \
                            f'823302   k/z   -6.91134   -3.99034   {"{:.4f}".format(16.55385 + self.safeMovement)}   0.66015625     $ lower outer beveling\n' \
                            f'823303   k/z   -6.91134   -3.99034   {"{:.4f}".format(17.5425 + self.safeMovement)}   5.0625         $ lower inner beveling\n' \
                             'c\n' \
                             'c\n' \
                             'c End of Shim Rod'
    
    def regPZ(self):
        self.regSurfaces += 'c pz surfaces\n' \
                            'c\n' \
                           f'832301   pz   {"{:.4f}".format(62.8153 + self.regMovement)}   $ top of control rod\n' \
                           f'832302   pz   {"{:.4f}".format(62.0533 + self.regMovement)}   $ top of main section\n' \
                           f'832303   pz   {"{:.4f}".format(61.4183 + self.regMovement)}   $ top of poison portion\n' \
                           f'832304   pz   {"{:.4f}".format(15.4327 + self.regMovement)}   $ bottom of poison portion\n' \
                           f'832305   pz   {"{:.4f}".format(14.7077 + self.regMovement)}   $ bottom of main section\n' \
                           f'832306   pz   {"{:.4f}".format(14.3013 + self.regMovement)}   $ bottom of outer lower cone\n' \
                           f'832307   pz   {"{:.4f}".format(13.7425 + self.regMovement)}   $ bottom of control rod \n' \
                            'c\n' \
                            'c\n' \
                            'c k/z surfaces\n' \
                            'c\n' \
                           f'833301   k/z   -6.91134   -3.99034   {"{:.4f}".format(69.51676 + self.safeMovement)}   0.1877777777   $ upper beveling\n' \
                           f'833302   k/z   -6.91134   -3.99034   {"{:.4f}".format(16.55385 + self.safeMovement)}   0.66015625     $ lower outer beveling\n' \
                           f'833303   k/z   -6.91134   -3.99034   {"{:.4f}".format(17.5425 + self.safeMovement)}   5.0625         $ lower inner beveling\n' \
                            'c\n' \
                            'c\n' \
                            'c End of Reg Rod'

    def safeCell(self):
        self.safeCellCard += 'c --- Safe Rod ---\n' \
                             'c\n' \
                            f'30501   103  -{"{:.2f}".format(self.alDensity)}       -192301  812301 -811301                  {self.P_imp}                    $ control rod connecting rod\n' \
                            f'30502   102  -{self.H2ODensity}   {"-192301" if self.coreOnly else "-130002"}  812301 -811304  811301          {self.P_imp}   tmp={self.tmp} $ water ring above control rod\n' \
                            f'30503   102  -{self.H2ODensity}    812302 -812301 -811304  811302  813301  {self.P_imp}   tmp={self.tmp} $ water above upper bevel\n' \
                            f'30504   103  -{"{:.2f}".format(self.alDensity)}        812302 -812301 -811304  811302 -813301  {self.P_imp}                    $ control rod upper bevel\n' \
                            f'30505   103  -{"{:.2f}".format(self.alDensity)}       -812301  812302 -811302                  {self.P_imp}                    $ top control rod inactive region\n' \
                            f'30506   103  -{"{:.2f}".format(self.alDensity)}       -812302  812303 -811304                  {self.P_imp}                    $ upper control rod inactive region\n' \
                             'c\n' \
                            f'30507   107  -{"{:.5f}".format(self.boronCarbideDensity)}    -811303 -812303  812304                  {self.P_imp}                    $ control rod poison section\n' \
                            f'30523   106  -{"{:.3f}".format(self.graphiteDensity)}       811303 -811305 -812303  812304          {self.P_imp}                    $ control rod poison burnup (graphite)\n' \
                            f'30508   103  -{"{:.2f}".format(self.alDensity)}        812305 -812303  811305 -811304          {self.P_imp}                    $ control rod cladding\n' \
                             'c\n' \
                            f'30509   103  -{"{:.2f}".format(self.alDensity)}       -812304  812305 -811305                  {self.P_imp}                    $ lower control rod inactive section\n' \
                            f'30510   103  -{"{:.2f}".format(self.alDensity)}       -812305  812306 -811302                  {self.P_imp}                    $ bottom control rod inactive section\n' \
                            f'30511   103  -{"{:.2f}".format(self.alDensity)}        811302 -811304 -812305  812306 -813302  {self.P_imp}                    $ Outer lower bevel\n' \
                            f'30512   103  -{"{:.2f}".format(self.alDensity)}       -811302 -812306  812307 -813303          {self.P_imp}                    $ inner lower bevel\n' \
                            f'30513   102  -{self.H2ODensity}    811302 -811304 -812305  812306  813302  {self.P_imp}   tmp={self.tmp} $ water around outer lower bevel\n' \
                            f'30514   102  -{self.H2ODensity}   -811302 -812306  812307  813303          {self.P_imp}   tmp={self.tmp} $ water around inner lower bevel\n' \
                            f'30515   102  -{self.H2ODensity}    811302 -811304  812307 -812306          {self.P_imp}   tmp={self.tmp} $ water under control rod bevels\n' \
                             'c\n' \
                            f'30516   102  -{self.H2ODensity}   -812307  902301 -811304                  {self.P_imp}   tmp={self.tmp} $ water under control rod\n' \
                             'c\n' \
                            f'30517   102  -{self.H2ODensity}    811304 -903057  902303 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water between safe rod and gride tube\n' \
                            f'30518   103  -{"{:.2f}".format(self.alDensity)}        903057 -903058  902303 -902399          {self.P_imp}                    $ control rod guide tube main section\n' \
                            f'30519   102  -{self.H2ODensity}    903057 -903058  902399 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water above guide tube\n' \
                            f'30520   102  -{self.H2ODensity}    903058 -903059  10     {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water around guide tube\n' \
                            f'30521   103  -{"{:.2f}".format(self.alDensity)}        811304 -903058  902301 -902303          {self.P_imp}                    $ guide tube thick section\n' \
                            f'30522   103  -{"{:.2f}".format(self.alDensity)}       -903058  10     -902301                  {self.P_imp}                    $ guide tube grid plate adapter\n'

    def shimCell(self):
        self.shimCellCard += 'c --- Shim Rod ---\n' \
                             'c\n' \
                            f'30901   103  -{"{:.2f}".format(self.alDensity)}       -192301  822301 -821301                  {self.P_imp}                    $ control rod connecting rod\n' \
                            f'30902   102  -{self.H2ODensity}   {"-192301" if self.coreOnly else "-130002"}  822301 -821304  821301          {self.P_imp}   tmp={self.tmp} $ water ring above control rod\n' \
                            f'30903   102  -{self.H2ODensity}    822302 -822301 -821304  821302  823301  {self.P_imp}   tmp={self.tmp} $ water above upper bevel\n' \
                            f'30904   103  -{"{:.2f}".format(self.alDensity)}        822302 -822301 -821304  821302 -823301  {self.P_imp}                    $ control rod upper bevel\n' \
                            f'30905   103  -{"{:.2f}".format(self.alDensity)}       -822301  822302 -821302                  {self.P_imp}                    $ top control rod inactive region\n' \
                            f'30906   103  -{"{:.2f}".format(self.alDensity)}       -822302  822303 -821304                  {self.P_imp}                    $ upper control rod inactive region\n' \
                             'c\n' \
                            f'30907   107  -{"{:.5f}".format(self.boronCarbideDensity)}    -821303 -822303  822304                  {self.P_imp}                    $ control rod poison section\n' \
                            f'30923   106  -{"{:.3f}".format(self.graphiteDensity)}       821303 -821305 -822303  822304          {self.P_imp}                    $ control rod poison burnup (graphite)\n' \
                            f'30908   103  -{"{:.2f}".format(self.alDensity)}        822305 -822303  821305 -821304          {self.P_imp}                    $ control rod cladding\n' \
                             'c\n' \
                            f'30909   103  -{"{:.2f}".format(self.alDensity)}       -822304  822305 -821305                  {self.P_imp}                    $ lower control rod inactive section\n' \
                            f'30910   103  -{"{:.2f}".format(self.alDensity)}       -822305  822306 -821302                  {self.P_imp}                    $ bottom control rod inactive section\n' \
                            f'30911   103  -{"{:.2f}".format(self.alDensity)}        821302 -821304 -822305  822306 -823302  {self.P_imp}                    $ Outer lower bevel\n' \
                            f'30912   103  -{"{:.2f}".format(self.alDensity)}       -821302 -822306  822307 -823303          {self.P_imp}                    $ inner lower bevel\n' \
                            f'30913   102  -{self.H2ODensity}    821302 -821304 -822305  822306  823302  {self.P_imp}   tmp={self.tmp} $ water around outer lower bevel\n' \
                            f'30914   102  -{self.H2ODensity}   -821302 -822306  822307  823303          {self.P_imp}   tmp={self.tmp} $ water around inner lower bevel\n' \
                            f'30915   102  -{self.H2ODensity}    821302 -821304  822307 -822306          {self.P_imp}   tmp={self.tmp} $ water under control rod bevels\n' \
                             'c\n' \
                            f'30916   102  -{self.H2ODensity}   -822307  902301 -821304                  {self.P_imp}   tmp={self.tmp} $ water under control rod\n' \
                             'c\n' \
                            f'30917   102  -{self.H2ODensity}    821304 -903097  902303 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water between safe rod and gride tube\n' \
                            f'30918   103  -{"{:.2f}".format(self.alDensity)}        903097 -903098  902303 -902399          {self.P_imp}                    $ control rod guide tube main section\n' \
                            f'30919   102  -{self.H2ODensity}    903097 -903098  902399 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water above guide tube\n' \
                            f'30920   102  -{self.H2ODensity}    903098 -903099  10     {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water around guide tube\n' \
                            f'30921   103  -{"{:.2f}".format(self.alDensity)}        821304 -903098  902301 -902303          {self.P_imp}                    $ guide tube thick section\n' \
                            f'30922   103  -{"{:.2f}".format(self.alDensity)}       -903098  10     -902301                  {self.P_imp}                    $ guide tube grid plate adapter\n'

    def regCell(self):
        self.regCellCard += 'c --- Reg Rod ---\n' \
                            'c\n' \
                           f'50101   103  -{"{:.2f}".format(self.alDensity)}       -192301  832301 -831301                  {self.P_imp}                    $ control rod connecting rod\n' \
                           f'50102   102  -{self.H2ODensity}   {"-192301" if self.coreOnly else "-130002"}  832301 -831304  831301          {self.P_imp}   tmp={self.tmp} $ water ring above control rod\n' \
                           f'50103   102  -{self.H2ODensity}    832302 -832301 -831304  831302  833301  {self.P_imp}   tmp={self.tmp} $ water above upper bevel\n' \
                           f'50104   103  -{"{:.2f}".format(self.alDensity)}        832302 -832301 -831304  831302 -833301  {self.P_imp}                    $ control rod upper bevel\n' \
                           f'50105   103  -{"{:.2f}".format(self.alDensity)}       -832301  832302 -831302                  {self.P_imp}                    $ top control rod inactive region\n' \
                           f'50106   103  -{"{:.2f}".format(self.alDensity)}       -832302  832303 -831304                  {self.P_imp}                    $ upper control rod inactive region\n' \
                            'c\n' \
                           f'50107   107  -{"{:.5f}".format(self.boronCarbideDensity)}    -831303 -832303  832304                  {self.P_imp}                    $ control rod poison section\n' \
                           f'50123   106  -{"{:.3f}".format(self.graphiteDensity)}       831303 -831305 -832303  832304          {self.P_imp}                    $ control rod poison burnup (graphite)\n' \
                           f'50108   103  -{"{:.2f}".format(self.alDensity)}        832305 -832303  831305 -831304          {self.P_imp}                    $ control rod cladding\n' \
                            'c\n' \
                           f'50109   103  -{"{:.2f}".format(self.alDensity)}       -832304  832305 -831305                  {self.P_imp}                    $ lower control rod inactive section\n' \
                           f'50110   103  -{"{:.2f}".format(self.alDensity)}       -832305  832306 -831302                  {self.P_imp}                    $ bottom control rod inactive section\n' \
                           f'50111   103  -{"{:.2f}".format(self.alDensity)}        831302 -831304 -832305  832306 -833302  {self.P_imp}                    $ Outer lower bevel\n' \
                           f'50112   103  -{"{:.2f}".format(self.alDensity)}       -831302 -832306  832307 -833303          {self.P_imp}                    $ inner lower bevel\n' \
                           f'50113   102  -{self.H2ODensity}    831302 -831304 -832305  832306  833302  {self.P_imp}   tmp={self.tmp} $ water around outer lower bevel\n' \
                           f'50114   102  -{self.H2ODensity}   -831302 -832306  832307  833303          {self.P_imp}   tmp={self.tmp} $ water around inner lower bevel\n' \
                           f'50115   102  -{self.H2ODensity}    831302 -831304  832307 -832306          {self.P_imp}   tmp={self.tmp} $ water under control rod bevels\n' \
                            'c\n' \
                           f'50116   102  -{self.H2ODensity}   -832307  902301 -831304                  {self.P_imp}   tmp={self.tmp} $ water under control rod\n' \
                            'c\n' \
                           f'50117   102  -{self.H2ODensity}    831304 -905017  902303 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water between safe rod and gride tube\n' \
                           f'50118   103  -{"{:.2f}".format(self.alDensity)}        905017 -905018  902303 -902399          {self.P_imp}                    $ control rod guide tube main section\n' \
                           f'50119   102  -{self.H2ODensity}    905017 -905018  902399 {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water above guide tube\n' \
                           f'50120   102  -{self.H2ODensity}    905018 -905019  10     {"-192301" if self.coreOnly else "-130002"}          {self.P_imp}   tmp={self.tmp} $ water around guide tube\n' \
                           f'50121   103  -{"{:.2f}".format(self.alDensity)}        831304 -905018  902301 -902303          {self.P_imp}                    $ guide tube thick section\n' \
                           f'50122   103  -{"{:.2f}".format(self.alDensity)}       -905018  10     -902301                  {self.P_imp}                    $ guide tube grid plate adapter    FIXME (probably not actually broken, just the last cell)\n'