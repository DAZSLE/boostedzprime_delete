import os
import subprocess
import json
from collections import OrderedDict

#from common.cmslpc import eos_rec_search
from common.samples import samples, subsamples, subsample_lfns

def eos_rec_search(startdir, suffix, skiplist, dirs):
    donedirs = []
    dirlook = subprocess.check_output(f"eos {eosbase} ls {startdir}", shell=True).decode('utf-8').split("\n")[:-1]
    for d in dirlook:
        if d.endswith(suffix):
            donedirs.append(startdir+"/"+d)
        elif any(skip in d for skip in skiplist):
            print("Skipping %s"%d)
            continue
        else:
            print("Searching %s"%d)
            donedirs = donedirs + eos_rec_search(startdir+"/"+d,suffix,skiplist,dirs+donedirs)
    return dirs+donedirs

if __name__ == "__main__":
    eosbase = "root://cmseos.fnal.gov/"
    eosdir = "/store/group/lpcbacon/pancakes/02/"
    dirlist = [
        ["2017/UL/", "2017UL",["Run20","hww_2017mc","hadd","tmp"]],
        ["2017/", "2017",["Run20","hadd","UL","tmp"]],
        ["2018/UL", "2018UL",["200211_180642"]],
    ]
    for year in ["2017"]:
        output_dict = OrderedDict()
        for sample in samples[year]:
            for subsample in subsamples[year][sample]:
                for lfn in subsample_lfns[subsample]:
                    dirlist = subprocess.check_output(f"eos {eosbase} ls {lfn}", shell=True).decode('utf-8').split("\n")
                    output_dict[subsample] = [x for x in dirlist in x[-5:] == ".root"]
        with open(os.path.expandvars(f"$ANALYSISBASE/boostedzprime/data/filesets/fileset_{year}.json"), 'w') as outfile:
            json.dump(jdict, outfile, indent=4, sort_keys=True)
