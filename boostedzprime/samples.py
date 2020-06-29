import os
import subprocess
import json

# Samples (short names, appear on final histograms)
samples = ["qcd", "zqq", "wqq", "hbb", "diboson", "ttbar", "singletop", "wlnu", "zll"]
zprime_masses = [50, 75, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500]
for mass in zprime_masses:
    samples.append(f"VectorZPrimeToQQ_M{mass}")
samples.append("VectorZPrimeGammaToQQGamma_flat")

# Subsample map (maps short names onto dataset names)
# - Subprocess name only; remove generation details
subsamples = {
    "2017": {
        "qcd": [
            "QCD_HT1000to1500",
            "QCD_HT100to200",
            "QCD_HT1500to2000",
            "QCD_HT2000toInf",
            "QCD_HT300to500",
            "QCD_HT500to700",
            "QCD_HT50to100",
            "QCD_HT700to1000",
        ],
        "zqq": [
            "ZJetsToQQ_HT800toInf",
            "ZJetsToQQ_HT400to600",
            "ZJetsToQQ_HT600to800",
        ], 
        "wqq": [
            "WJetsToQQ_HT800toInf",
            "WJetsToQQ_HT400to600",
            "WJetsToQQ_HT600to800",
        ],
        "ttbar": [
            "TTTo2L2Nu",
            "TTToHadronic",
            "TTToSemiLeptonic",
        ]
        "hbb": [

        ], 
        "singletop": [
            "ST_s-channel_4f_hadronicDecays", 
            "ST_s-channel_4f_leptonDecays", 
            "ST_t-channel_antitop_4f_InclusiveDecays", 
            "ST_t-channel_top_4f_InclusiveDecays", 
            "ST_tW_antitop_5f_inclusiveDecays", 
            "ST_tW_top_5f_inclusiveDecays", 
        ], 
        "diboson": ["WW", "WZ", "ZZ"],
        "wlnu": [
            "WJetsToLNu_HT100To200",
            "WJetsToLNu_HT1200To2500",
            "WJetsToLNu_HT200To400",
            "WJetsToLNu_HT2500ToInf",
            "WJetsToLNu_HT400To600",
            "WJetsToLNu_HT600To800",
            "WJetsToLNu_HT70To100",
            "WJetsToLNu_HT800To1200",
        ], 
        "zll": [
            "DYJetsToLL_M-50_HT-100to200",
            "DYJetsToLL_M-50_HT-1200to2500",
            "DYJetsToLL_M-50_HT-200to400",
            "DYJetsToLL_M-50_HT-2500toInf",
            "DYJetsToLL_M-50_HT-400to600",
            "DYJetsToLL_M-50_HT-600to800",
            "DYJetsToLL_M-50_HT-800to1200",
        ]
    }
}
for mass in zprime_masses:
    subsamples["2017"][f"VectorZPrimeToQQ_M{mass}"] = f"VectorZPrimeToQQ_M{mass}"
# For 2016 and 2018, start by copying 2017, and then replace where needed

# Physical locations of samples
#eosbase = "root://cmseos.fnal.gov/"
topdir_2017 = f"/store/group/lpcbacon/pancakes/02/2017/"
topdir_2017hadd = f"/store/group/lpcbacon/pancakes/02/2017/"
topdir_2017UL = f"/store/group/lpcbacon/pancakes/02/2017/UL/"
topdir_2017ULhadd = f"/store/group/lpcbacon/pancakes/02/2017/UL/hadd"
subsample_lfns = {
    "2017": {
        "QCD_HT1000to1500": [f"{topdir_2017ULhadd}/QCD_HT1000to1500_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT100to200": [f"{topdir_2017ULhadd}/QCD_HT100to200_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT1500to2000": [f"{topdir_2017ULhadd}/QCD_HT1500to2000_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT2000toInf": [f"{topdir_2017ULhadd}/QCD_HT2000toInf_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT300to500": [f"{topdir_2017ULhadd}/QCD_HT300to500_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT500to700": [f"{topdir_2017ULhadd}/QCD_HT500to700_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT50to100": [f"{topdir_2017ULhadd}/QCD_HT50to100_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "QCD_HT700to1000": [f"{topdir_2017ULhadd}/QCD_HT700to1000_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8-hadd/"],
        "ZJetsToQQ_HT800toInf": [f"{topdir_2017hadd}/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "ZJetsToQQ_HT400to600": [f"{topdir_2017hadd}/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "ZJetsToQQ_HT600to800": [f"{topdir_2017hadd}/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToQQ_HT800toInf": [f"{topdir_2017hadd}/WJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToQQ_HT400to600": [f"{topdir_2017hadd}/WJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToQQ_HT600to800": [f"{topdir_2017hadd}/WJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "TTTo2L2Nu": [f"{topdir_2017ULhadd}/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8-hadd/"],
        "TTToHadronic": [f"{topdir_2017ULhadd}/TTToHadronic_TuneCP5_13TeV-powheg-pythia8-hadd/"],
        "TTToSemiLeptonic": [f"{topdir_2017ULhadd}/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8-hadd/"],
        "ST_s-channel_4f_hadronicDecays": [f"{topdir_2017hadd}/ST_s-channel_4f_hadronicDecays_TuneCP5_13TeV-amcatnlo-pythia8-hadd/"],
        "ST_s-channel_4f_leptonDecays": [f"{topdir_2017hadd}/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8-hadd/"],
        "ST_t-channel_antitop_4f_InclusiveDecays": [f"{topdir_2017hadd}/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8-hadd/"],
        "ST_t-channel_top_4f_InclusiveDecays": [f"{topdir_2017hadd}/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8-hadd/"],
        "ST_tW_antitop_5f_inclusiveDecays": [f"{topdir_2017hadd}/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8-hadd/"],
        "ST_tW_top_5f_inclusiveDecays": [f"{topdir_2017hadd}/ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8-hadd/"],
        "WW": [f"{topdir_2017ULhadd}/WW_TuneCP5_13TeV-pythia8-hadd/"],
        "WZ": [f"{topdir_2017ULhadd}/WZ_TuneCP5_13TeV-pythia8-hadd/"],
        "ZZ": [f"{topdir_2017ULhadd}/ZZ_TuneCP5_13TeV-pythia8-hadd/"],
        "WJetsToLNu_HT100To200": [f"{topdir_2017hadd}/WJetsToLNu_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT1200To2500": [f"{topdir_2017hadd}/WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT200To400": [f"{topdir_2017hadd}/WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT2500ToInf": [f"{topdir_2017hadd}/WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT400To600": [f"{topdir_2017hadd}/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT600To800": [f"{topdir_2017hadd}/WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT70To100": [f"{topdir_2017hadd}/WJetsToLNu_HT-70To100_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "WJetsToLNu_HT800To1200": [f"{topdir_2017hadd}/WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"],
        "DYJetsToLL_M-50_HT-100to200": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-1200to2500": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-200to400": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-2500toInf": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-400to600": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-600to800": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
        "DYJetsToLL_M-50_HT-800to1200": [f"{topdir_2017hadd}/DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8-hadd/"], 
    }
}
for mass in zprime_masses:
    sampledirs["2017"][f"VectorZPrimeToQQ_M{mass}"] = f"{topdir_2017hadd}/VectorZPrimeToQQ_M{mass}_pT300_TuneCP5_madgraph_pythia8_13TeV"
