# boostedzprime

## coffea+tensorflow capability (standalone, transportable conda environment)
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p miniconda/
source miniconda/bin/activate
conda create -n tf tensorflow
conda activate tf
pip install coffea
conda install -c conda-forge xrootd


git clone git@github.com:DAZSLE/boostedzprime.git
cd boostedzprime
pip install --user --editable .

# To make the environment transportable
conda install -c conda-forge conda-pack
conda-pack
```

Disclaimer: sporked from `boostedhiggs` for github searchability.


