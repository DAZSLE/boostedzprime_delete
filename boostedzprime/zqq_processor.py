import logging
from functools import partial
import numpy as np
from coffea import processor, hist
from boostedzprime.twoProngGRU import *
from coffea.nanoaod.methods import collection_methods, Candidate
#collection_methods["FatJetPFCands"] = Candidate

from boostedzprime.corrections import (
    corrected_msoftdrop,
    gruddt_shift,
    n2ddt_shift,
    shift,
    add_pileup_weight,
    add_jetTriggerWeight,
    add_VJets_NLOkFactor,
)
from boostedzprime.common import (
    getBosons,
)

def genmatch(events):
    zprime = events.GenPart[((events.GenPart.pdgId==55) | (events.GenPart.pdgId==23) | (abs(events.GenPart.pdgId)==24)) & events.GenPart.hasFlags(["isLastCopy"])].flatten()
    q0 = zprime.children[:, 0]
    q1 = zprime.children[:, 1]
    return (events.FatJet.delta_r2(q0) < 0.6*0.6) & (events.FatJet.delta_r2(q1) < 0.6*0.6)

    
class ZQQProcessor(processor.ProcessorABC):
    def __init__(self, year='2017'):
        self._year = year
        self._triggers = {
            '2017': [
                'PFHT1050',
                'AK8PFJet400_TrimMass30',
                'AK8PFJet420_TrimMass30',
                'AK8PFHT800_TrimMass50',
                'PFJet500',
                'AK8PFJet500',
                'AK8PFJet550',
                'CaloJet500_NoJetID',
                'CaloJet550_NoJetID', 
                 ]
        }
        self._muontriggers = {
            '2017': [
                'Mu50', 
                #'TkMu50',
                 ]
        }
        self._accumulator = processor.dict_accumulator({
            'sumw': processor.defaultdict_accumulator(float),
            'templates': hist.Hist(
                'Events',
                hist.Cat('dataset', 'Dataset'),
                hist.Cat('region', 'Region'),
                #hist.Cat('systematic', 'Systematic'),
                hist.Bin('pt', r'Jet $p_{T}$ [GeV]', 25,500,1000),#[525,575,625,700,800,1500]),#np.arange(525,2000,50)),
                hist.Bin('msd', r'Jet $m_{sd}$', 23, 40, 300),
                #hist.Bin('gru', 'GRU value',20,0.,1.),
                #hist.Bin('gruddt', 'GRU$^{DDT}$ value',[-1,0,1]),
                #hist.Bin('rho', 'jet rho', 20,-5.5,-2.),#[-5.5,-5.,-4.5,-4.,-3.5,-3.,-2.5,-2.]),
                #hist.Bin('n2', 'N$_2$ value', 20, 0., 0.5),
                #hist.Bin('n2ddt', 'N$_2^{DDT}$ value', 21, -0.3, 0.3),
                #hist.Bin('Vmatch', 'Matched to V', [-1,0,1]),
                hist.Bin('in_v3_ddt', 'IN$^{DDT}$  value', 20, -1, 0.5),
                hist.Bin('mu_pt', 'Leading muon p_{T}', 20,50., 700.),
                hist.Bin('mu_pfRelIso04_all', 'Muon pfRelIso04 isolation', 20,0.,1.),
                #hist.Bin('nPFConstituents', 'Number of PF candidates',41,20,60),
                #hist.Bin('nJet', 'Number of fat jets', 10,0,9), 
            ),
            #'gruddt' : hist.Hist(
            #    hist.Cat('dataset', 'Dataset'),
            #    hist.Cat('region', 'Region'),
            #'cutflow': hist.Hist(
            #    'Events',
            #    hist.Cat('dataset', 'Dataset'),
            #    hist.Cat('region', 'Region'),
            #    hist.Bin('cut', 'Cut index', 11, 0, 11),
            #),
            'cutflow_signal' : processor.defaultdict_accumulator(partial(processor.defaultdict_accumulator, float)),
            'cutflow_ttbar_muoncontrol' : processor.defaultdict_accumulator(partial(processor.defaultdict_accumulator, float)),

        })
    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        #assert(len(np.unique(events.event)) == len((events.event)))
        dataset = events.metadata['dataset']
        print('process dataset', dataset)
        isRealData = 'genWeight' not in events.columns
        selection = processor.PackedSelection()
        weights = processor.Weights(len(events))
        output = self.accumulator.identity()
        if(len(events) == 0): return output
        if not isRealData:
            output['sumw'][dataset] += events.genWeight.sum()

       


        # trigger paths
        if isRealData:
            trigger_fatjet = np.zeros(events.size, dtype='bool')
            for t in self._triggers[self._year]:
                try:
                    trigger_fatjet = trigger_fatjet | events.HLT[t]
                except:
                    print('trigger %s not available'%t)
                    continue

            trigger_muon = np.zeros(events.size, dtype='bool')
            for t in self._muontriggers[self._year]:
                trigger_muon = trigger_muon | events.HLT[t]
 
        else:
            trigger_fatjet = np.ones(events.size, dtype='bool')
            trigger_muon = np.ones(events.size, dtype='bool')

        selection.add('fatjet_trigger', trigger_fatjet)
        selection.add('muon_trigger', trigger_muon) 

        # run model on PFCands associated to FatJet (FatJetPFCands)
        #events.FatJet.array.content["PFCands"] = type(events.FatJetPFCands.array).fromcounts(events.FatJet.nPFConstituents.flatten(), events.FatJetPFCands.flatten())
        #events.FatJet.array.content["twoProngGru"] = run_model(events.FatJet.flatten())
   
        #else:
        #  events.FatJet["genMatchFull"] = np.ones(len(events))
        fatjets = events.FatJet
        gru = events.GRU
        IN  = events.IN
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets)
        fatjets['rhocorr'] = 2*np.log(fatjets.msdcorr/fatjets.pt)
        fatjets['gruddt'] = gru.v25 - shift(fatjets,algo='gruddt',year=self._year)
        fatjets['in_v3_ddt'] = IN.v3 - shift(fatjets,algo='inddt',year=self._year)
        fatjets['n2ddt'] = fatjets.n2b1 - n2ddt_shift(fatjets,year=self._year)
        #fatjets['count'] = fatjets.count
        if 'WJetsToQQ' in dataset or 'ZJetsToQQ' in dataset: fatjets["genMatchFull"] = genmatch(events)
        else: fatjets["genMatchFull"] = fatjets.pt.zeros_like() #np.zeros(events.size, dtype='bool') 

        candidatejet = fatjets[
            (fatjets.pt > 200)
            & (abs(fatjets.eta) < 2.5)
        ][:, 0:1]

        # basic jet selection
        selection.add('minjetkin', ( 
            (candidatejet.pt >= 450)
            #& (candidatejet.msdcorr >= 40.)
            & (abs(candidatejet.eta) < 2.5)
            & (candidatejet.rhocorr >= -5.5)
            & (candidatejet.rhocorr <= -2)
        ).any())
        selection.add('signal_pt', (
            (candidatejet.pt >= 525)
        ).any())

        selection.add('mass', (candidatejet.msdcorr >= 40.).any())
        selection.add('v_selection_jetkin', ( 
            (candidatejet.pt >= 200)
            & (candidatejet.rhocorr >= -5.5)
            & (candidatejet.rhocorr <= -2)
        ).any())
        selection.add('genmatch', candidatejet.genMatchFull.pad(1).fillna(0).flatten() if ('WJetsToQQ' in dataset or 'ZJetsToQQ' in dataset) else candidatejet.pt.pad(1).fillna(0).flatten().astype(bool))
        #if isRealData:
        #   selection.add('blinding', (
        #      (events.event %10 == 0)
        #   ))
        selection.add('n2ddt', (candidatejet.n2ddt < 0.).any())
        selection.add('jetid', candidatejet.isTight.any())
        selection.add('met', events.MET.pt > 40.) 

        goodmuon = (
            (events.Muon.pt > 10)
            & (abs(events.Muon.eta) < 2.1)
            #& (events.Muon.pfRelIso04_all < 0.4)
            #& (events.Muon.looseId).astype(bool)
        )
        nmuons=goodmuon.sum()
        leadingmuon = events.Muon[goodmuon 
        #& (events.Muon.pt > 55)
        ][:, 0:1]
        muon_ak8_pair = leadingmuon.cross(candidatejet, nested=True)
 
        ngoodmuons = goodmuon[events.Muon.pt > 55].sum()

        selection.add('muonDphiAK8', (
            abs(muon_ak8_pair.i0.delta_phi(muon_ak8_pair.i1)) > 2*np.pi/3
        ).all().all())

        

        selection.add('muonkin', (
            (leadingmuon.pt > 55.)
            & (abs(leadingmuon.eta) < 2.1)
            #& (leadingmuon.looseId).astype(bool)
        ).all())

        #ak4 puppi jet for CR
        jets = events.Jet[
            (events.Jet.pt > 50.)
            & (abs(events.Jet.eta) < 3)
            & (events.Jet.isTight).astype(bool)
        ]

        # only consider first 4 jets to be consistent with old framework
        jets = jets[:, :4]
        ak4_ak8_pair = jets.cross(candidatejet, nested=True)
        dr = abs(ak4_ak8_pair.i0.delta_r(ak4_ak8_pair.i1))
        ak4_away = jets[(dr > 0.8).all()]
        #selection.add('ak4btagMedium08', ak4_away.btagDeepB.max() > 0.4941)
        selection.add('ak4btagMedium08', ak4_away.btagCSVV2.max() > 0.8838)

        #generic lep veto

        nelectrons = (
            (events.Electron.pt > 10.)
            & (abs(events.Electron.eta) < 2.5)
            & (events.Electron.cutBased >= events.Electron.LOOSE)
        ).sum()

        ntaus = (
            (events.Tau.pt > 20.)
            & (events.Tau.idDecayMode).astype(bool)
            # bacon iso looser than Nano selection
        ).sum()
        selection.add('onemuon', (ngoodmuons==1)& (nelectrons == 0) & (ntaus == 0))
        selection.add('noleptons', (nmuons == 0) & (nelectrons == 0) & (ntaus == 0))
        selection.add('noelectron_notau', (nelectrons == 0) & (ntaus == 0))
     
        if not isRealData: 
            weights.add('genweight', events.genWeight)
            #add_pileup_weight(weights, events.Pileup.nPU, self._year, dataset)
            #add_jetTriggerWeight(weights, candidatejet.msdcorr, candidatejet.pt, self._year) signal region only
            bosons = getBosons(events)
            genBosonPt = bosons.pt.pad(1, clip=True).fillna(0)
            add_VJets_NLOkFactor(weights, genBosonPt, self._year, dataset)  
            #b-tag weights
        regions = {
           'signal'                 : ['fatjet_trigger','minjetkin','signal_pt','mass','noleptons','jetid','genmatch'],
           'ttbar_muoncontrol'      : ['muon_trigger', 'minjetkin','jetid', 'mass', 'muonDphiAK8','muonkin','ak4btagMedium08','onemuon',],
           'noselection' : [],#'vselection_muoncontrol' : ['muon_trigger', 'v_selection_jetkin', 'genmatch', 'jetid', 'ak4btagMedium08', 'muonkin','met'],
        }
        #if isRealData and 'SingleMuon' not in dataset:
        #    regions['signal'].append('blinding')
        '''for region, cuts in regions.items():
            allcuts = set() 
            print ('weights', weights.weight().shape)
            print( len(events)) 
            output['cutflow'].fill(dataset=dataset, region=region, cut=0)#,weight=weights.weight())
            
            for i, cut in enumerate(cuts):
                 
                allcuts.add(cut)
                cut = selection.all(*allcuts)
                output['cutflow'].fill(dataset=dataset, region=region, cut=i + 1)# weight=weights.weight()[cut])
        '''
        allcuts_signal = set()
        output['cutflow_signal'][dataset]['none']+= float(weights.weight().sum())
        allcuts_ttbar_muoncontrol = set()
        output['cutflow_ttbar_muoncontrol'][dataset]['none']+= float(weights.weight().sum())
  
        for cut in regions['signal']:
            allcuts_signal.add(cut)
            output['cutflow_signal'][dataset][cut] += float(weights.weight()[selection.all(*allcuts_signal)].sum())

        for cut in regions['ttbar_muoncontrol']:
            allcuts_ttbar_muoncontrol.add(cut)
            output['cutflow_ttbar_muoncontrol'][dataset][cut] += float(weights.weight()[selection.all(*allcuts_ttbar_muoncontrol)].sum())

        def normalize(val, cut):
            return val[cut].pad(1, clip=True).fillna(0).flatten()

        def fill(region, systematic=None, wmod=None):
            selections = regions[region]
            cut = selection.all(*selections)
            sname = 'nominal' if systematic is None else systematic
            weight = weights.weight()[cut]
            output['templates'].fill(
                dataset=dataset,
                region=region,
                pt=normalize(candidatejet.pt, cut),
                msd=normalize(candidatejet.msdcorr, cut),
                #gruddt=normalize(candidatejet.gruddt, cut),
                #n2=normalize(candidatejet.n2b1, cut),
                #gru=normalize(candidatejet.twoProngGru, cut),
                #rho=normalize(candidatejet.rhocorr, cut),
                in_v3_ddt=normalize(candidatejet.in_v3_ddt, cut),
                #nPFConstituents=normalize(candidatejet.nPFConstituents, cut),
                #nJet=candidatejet.counts[cut],
                #Vmatch=normalize(candidatejet.genMatchFull, cut),
                mu_pt=normalize(leadingmuon.pt, cut),
                mu_pfRelIso04_all=normalize(leadingmuon.pfRelIso04_all, cut),
                weight=weight,
            )

        for region in regions:
            fill(region)

        return output

    def postprocess(self, accumulator):
        return accumulator

