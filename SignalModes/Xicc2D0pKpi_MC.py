# -*- coding: utf-8 -*-

# DaVinci script to apply Stripping 21 cuts with PID requirements to MC
# The decays of Xicc+ -> (D0 -> pi+ K-) p K- pi+ are generated by GenXicc package 

__author__  = 'Murdo Traill'
__date__    =  '23/12/2016'

########## IMPORT BASIC CLASSES ###################

import GaudiKernel.SystemOfUnits as Units

from Gaudi.Configuration import *
from PhysSelPython.Wrappers import AutomaticData, Selection, DataOnDemand, SelectionSequence

########## CANDIDATE LOCATION ####################

line = 'XiccXiccPlusToD0PKPi'                     # The stripping line of choice 
location = '/Event/Charm/Phys/'+line+'/Particles' # For debugging purposes later

######## BUILD THE D0 DECAY ###################

from Configurables import CombineParticles

# Define Algorithm '_D02PiK' with the following cuts to constrain the Dplus candidates.

_D02KPi = CombineParticles("_D02KPi",                       
				    DecayDescriptor = "[D0 -> K- pi+]cc",
		        DaughtersCuts = {'K+' : '(P > 2*GeV)', 'pi+' : '(P > 2*GeV)'},
            CombinationCut = "(((APT>1*GeV) | (ASUM(PT)>1.2*GeV)) & (ADAMASS('D0')<110*MeV) & (ADOCA(1,2)<0.5*mm) & (ADOCACHI2CUT(15,'')))",
            MotherCut = "((VFASPF(VCHI2)<10) & (ADMASS('D0')<100*MeV) & (BPVVDCHI2>36))")

# Locate protoparticles from TES for kaons and pions. 

from CommonParticles import StdAllNoPIDsKaons, StdAllNoPIDsPions, StdAllNoPIDsProtons

Kaons  = DataOnDemand(Location = 'Phys/StdNoPIDsKaons/Particles')
Pions = DataOnDemand(Location = 'Phys/StdNoPIDsPions/Particles')

# Make a selection object for the D0 candidates using the algorithm defined above, feeding in the protoparticles. 

Sel_LooseD02KPi = Selection("Sel_LooseD02KPi", 
                              Algorithm = _D02KPi,
                              RequiredSelections = [Kaons, Pions])

# Define next the algorithm '_D0filter' which will place further cuts on the Dplus candidates.

from Configurables import FilterDesktop 
                   
_D0filter = FilterDesktop("_D0filter",
                       Code = "(ADMASS('D0')<75.0) & (BPVVDCHI2>64.0)")

# Make another Selection object for filtered Dplus candidates using '_dplusfilter' algorithm.
                 
Sel_D02KPi = Selection("Sel_D02KPi",
                      Algorithm = _D0filter,
                      RequiredSelections = [Sel_LooseD02KPi])
                      
############# BUILD THE XICC DECAY #######################

# Locate the protoparticles from TES for the soft protons. 

AllKaons  = DataOnDemand(Location = 'Phys/StdAllNoPIDsKaons/Particles')
AllPions = DataOnDemand(Location = 'Phys/StdAllNoPIDsPions/Particles')
AllProtons = DataOnDemand(Location = 'Phys/StdAllNoPIDsProtons/Particles')

# Define the algorithm '_pfilter' with cuts for the protons. 

_Pfilter = FilterDesktop("_Pfilter",
	              Code = "(TRCHI2DOF<5.0) & (P>2000.0) & (PT>250.0) & (MIPCHI2DV(PRIMARY)>-1.0)")

# Make a selection object for the filtered protons, feeding in the protoparticles. 

Sel_FilteredProtons = Selection("Sel_FilteredProtons", 
                          Algorithm = _Pfilter,
                          RequiredSelections = [AllProtons])

# Define the algorithm '_Kfilter' with cuts for the soft kaons. 

_Kfilter = FilterDesktop("_Kfilter",
	              Code = "(TRCHI2DOF<5.0)& (P>2000.0)& (PT>250.0) & (MIPCHI2DV(PRIMARY)>-1.0)")

# Make a selection object for the filtered kaons, feeding in the protoparticles. 

Sel_FilteredKaons = Selection("Sel_FilteredKaons", 
                          Algorithm = _Kfilter,
                          RequiredSelections = [AllKaons])

# Define the algorithm '_Pifilter' with cuts for the soft pions. 

_Pifilter = FilterDesktop("_Pifilter",
                Code = "(TRCHI2DOF<5.0)& (P>2000.0)& (PT>250.0) & (MIPCHI2DV(PRIMARY)>-1.0)")

# Make a selection object for the filtered pions, feeding in the protoparticles. 

Sel_FilteredPions = Selection("Sel_FilteredPions", 
                          Algorithm = _Pifilter,
                          RequiredSelections = [AllPions])
    
# Define the TisTosParticle Tagger Algorithm '_XiccD0TisTos" for determining if D0 Candidate are TIS or TOS.                           
                          
from Configurables import TisTosParticleTagger

_XiccD0TisTos = TisTosParticleTagger("XiccD0TisTos", TisTosSpecs = { 'Hlt2.*CharmHadD02.*Decision%TOS' : 0 })

# Make a selection object for the TISTOS result of the filtered D0 candidates. 

Sel_XiccD0TisTos = Selection("Sel_XiccD0TisTos", 
							Algorithm = _XiccD0TisTos, 
							RequiredSelections = [Sel_D02KPi])
							
# Define the algorithm '_Xiccplus2D0Kpi' with the following cut to constrain the Xicc candidates. 

_Xiccplus2D0Kpi = CombineParticles("_Xiccplus2D0Kpi",
							DecayDescriptor = "[Xi_cc+ -> D0 p+ K- pi+]cc",
							DaughtersCuts = { '' : 'ALL' , 'D0' : 'ALL' , 'D~0' : 'ALL' , 'K+' : 'ALL' , 'K-' : 'ALL' , 'p+' : 'ALL' , 'p~-' : 'ALL', 'pi+' : 'ALL' , 'pi-' : 'ALL' },
							CombinationCut = "(AM<4000.0)& (APT>2000.0)& (ADOCAMAX('')<0.5)",
							MotherCut = "(VFASPF(VCHI2)<60.0)&(CHILD(VFASPF(VZ),1) - VFASPF(VZ) > 0.01)& (BPVVDCHI2 > -1.0)& (BPVDIRA > 0.0)")
	
# Make a selection object for the final Xicc candidates with the above algorithm. 				

Sel_Xicc = Selection("Xicc+_Sel", Algorithm = _Xiccplus2D0Kpi, RequiredSelections = [Sel_XiccD0TisTos, Sel_FilteredProtons, Sel_FilteredKaons, Sel_FilteredPions]) 

# Configure the order of selections to be carried out in sequentially with the last selection at the top. 

Seq_Xicc2D0pKpi = SelectionSequence("Seq_Xicc2D0pKpi" , TopSelection = Sel_Xicc)

###################### CONFIGURE DECAY TREE TUPLE ###########################

# Using DecayTreeTuple to give reconstructed information in our final ntuple 

from Configurables import DecayTreeTuple, TupleToolTrigger, TupleToolDecay, TupleToolTISTOS
from DecayTreeTuple.Configuration import *

simulation = True

tuple = DecayTreeTuple() 
tuple.Decay = "[Xi_cc+ -> ^(D0-> ^K- ^pi+) ^p+ ^K- ^pi+]CC"

# Input is the resulting of the stripping the candidates
tuple.Inputs = [Seq_Xicc2D0pKpi.outputLocation()] 

tuple.ToolList +=  [
      "TupleToolGeometry"
    , "TupleToolKinematic"
    , "TupleToolEventInfo"
    , "TupleToolTrackInfo"  
    , "TupleToolPrimaries"
    , "TupleToolTISTOS"
    , "TupleToolAngles"
    , "TupleToolPid"
    , "TupleToolPropertime"]

if (simulation):
  tuple.addTupleTool("TupleToolMCTruth")
  tuple.addTupleTool("TupleToolMCBackgroundInfo")

# Change the configuration of the TupleToolTISTOS tool
tuple.addTool(TupleToolTISTOS())
tuple.TupleToolTISTOS.TriggerList = ["Hlt1TrackAllL0Decision",
                                     "Hlt1GlobalDecision",
                                     'Hlt2CharmHadD02HH_D02PiPiDecision',
                                     'Hlt2CharmHadD02HH_D02PiPiWideMassDecision',
                                     'Hlt2CharmHadD02HHKsLLDecision',
                                     'Hlt2CharmHadD02HHKsDDDecision',
                                     'Hlt2CharmHadD02HH_D02KPiDecision', 
                                     'Hlt2CharmHadD02HH_D02KPiWideMassDecision',
                                     'Hlt2CharmHadD02HH_D02KKDecision', 
                                     'Hlt2CharmHadD02HH_D02KKWideMassDecision']

tuple.TupleToolTISTOS.VerboseHlt1 = True
tuple.TupleToolTISTOS.VerboseHlt2 = True

# Personalise particle branch head names
tuple.addBranches({'Xicc'   : '[Xi_cc+ -> (D0-> K- pi+) p+ K- pi+]CC',
                   'D0'     : '[Xi_cc+ -> ^(D0-> K- pi+) p+ K- pi+]CC',
                   'Kminus' : '[Xi_cc+ -> (D0-> ^K- pi+) p+ K- pi+]CC',
                   'piplus' : '[Xi_cc+ -> (D0-> K- ^pi+) p+ K- pi+]CC',
                   'pplus'  : '[Xi_cc+ -> (D0-> K- pi+) ^p+ K- pi+]CC',
                   'Ksoft'  : '[Xi_cc+ -> (D0-> K- pi+) p+ ^K- pi+]CC',
                   'pisoft' : '[Xi_cc+ -> (D0-> K- pi+) p+ K- ^pi+]CC'})

# Configure DecayTreeFitter with a constraint on the D0 mass
const_tool1 = tuple.Xicc.addTupleTool('TupleToolDecayTreeFitter/ConsD0Mass')
const_tool1.daughtersToConstrain = ['D0']
const_tool1.Verbose = True 

const_tool2 = tuple.Xicc.addTupleTool('TupleToolDecayTreeFitter/ConsPV')
const_tool2.constrainToOriginVertex = True
const_tool2.Verbose = True

#Configure LoKi__Hybrid__TupleTool
from Configurables import LoKi__Hybrid__TupleTool

preamble = ['DZ = VFASPF(VZ) - BPV(VZ)',
            'TRACK_MAX_PT = MAXTREE(ISBASIC & HASTRACK, PT, -1)']

variables1 = {'MAXDOCA'     :  "DOCAMAX",
              'DIRA'        :  "BPVDIRA",
              'DecayAngle'  :  "LV01",
              'P'           :  "P",
              'TRACK_Eta'   :  "ETA",
              'DZ'          :  "DZ",
              'MAX_PT'      :  "TRACK_MAX_PT",
              'VTX_CHI2'    :  "VFASPF(VCHI2)",
              'VTX_VZ'      :  "VFASPF(VZ)",
              'MIPCHI2DV'   :  "MIPCHI2DV(PRIMARY)"}

variables2 = { 'P'           :  "P",
               'TRACK_Eta'   :  "ETA"}

XiccTool = tuple.Xicc.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
XiccTool.Preambulo = preamble
XiccTool.Variables = variables1

D0Tool = tuple.D0.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
D0Tool.Preambulo = preamble
D0Tool.Variables = variables1

KmTool = tuple.Kminus.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
KmTool.Preambulo = preamble
KmTool.Variables = variables2

PipTool = tuple.piplus.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
PipTool.Preambulo = preamble
PipTool.Variables = variables2

psoftTool = tuple.pplus.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
psoftTool.Preambulo = preamble
psoftTool.Variables = variables2

KmsoftTool = tuple.Ksoft.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
KmsoftTool.Preambulo = preamble
KmsoftTool.Variables = variables2

PipsoftTool = tuple.pisoft.addTupleTool('LoKi::Hybrid::TupleTool/XiccLoKiTuple')
PipsoftTool.Preambulo = preamble
PipsoftTool.Variables = variables2

################### CONFIGURE MCDECAY TREE TUPLE ###############################

mctuple = MCDecayTreeTuple()

mctuple.ToolList +=  [ 
      "MCTupleToolKinematic"
    , "MCTupleToolAngles"
    , "MCTupleToolEventType"
    , "MCTupleToolDecayType"  
    , "MCTupleToolPID"
    , "MCTupleToolPrimaries"
    , "MCTupleToolPrompt"
    , "MCTupleToolInteractions"
    , "MCTupleToolReconstructed"
    , "MCTupleToolHierarchy"]

mctuple.Decay = "[Xi_cc+ => ^(D0 => ^K- ^pi+) ^p+ ^K- ^pi+]CC" 

# Personalise particle branch head names
mctuple.addBranches({'Xicc'   : '[Xi_cc+ => (D0 => K- pi+) p+ K- pi+]CC',
                     'D0'     : '[Xi_cc+ => ^(D0 => K- pi+) p+ K- pi+]CC',
                     'Kminus' : '[Xi_cc+ => (D0 => ^K- pi+) p+ K- pi+]CC',
                     'piplus' : '[Xi_cc+ => (D0 => K- ^pi+) p+ K- pi+]CC',
                     'pplus'  : '[Xi_cc+ => (D0 => K- pi+) ^p+ K- pi+]CC',
                     'Ksoft'  : '[Xi_cc+ => (D0 => K- pi+) p+ ^K- pi+]CC',
                     'pisoft' : '[Xi_cc+ => (D0 => K- pi+) p+ K- ^pi+]CC'})

####################### CONFIGURE DAVINCI  ###########################

from Configurables import DaVinci

dv = DaVinci()
dv.UserAlgorithms += [Seq_Xicc2D0pKpi.sequence(), tuple, mctuple]

dv.DataType = '2012'
dv.InputType = 'DST'
dv.PrintFreq = 1000
dv.EvtMax =  -1          

# DDDB = Detector Description Database and CondDB = Conditions Database.

dv.DDDBtag = "dddb-20150928"
dv.CondDBtag = "sim-20160321-2-vc-md100"
#dv.CondDBtag = "sim-20160321-2-vc-mu100"

#dv.HistogramFile = "26165059_MagDown_histos.root"   
dv.TupleFile     = "Xicc2D0pKpi_MagDown_tuple.root"
dv.Simulation = True
dv.Lumi = not dv.Simulation 

################# DEBUGGING #########################

from Configurables import GaudiSequencer
from Configurables import LoKi__HDRFilter, PrintDecayTree 

MySequencer = GaudiSequencer('Sequence')

pt = PrintDecayTree(Inputs = [ location ])
sf = LoKi__HDRFilter( 'StripPassFilter', Code="HLT_PASS('Stripping"+line+"Decision')", Location="/Event/Strip/Phys/DecReports" )

MySequencer.Members = [ sf ]

dv.appendToMainSequence([ MySequencer ])

MessageSvc().Format = "% F%60W%S%7W%R%T %0W%M"  # useful bit of coding to increase error message output

#####################################################

#from GaudiConf import IOHelper

#IOHelper().inputFiles([
#        '/afs/cern.ch/work/m/mutraill/Data/MonteCarlo/Xicc+2D0pK-pi+/MagDown_00053952_00000001_2.AllStreams.dst'
#         ], clear=True)
