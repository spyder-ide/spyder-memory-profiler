#!/bin/bash

export COVERALLS_REPO_TOKEN="fLwtNlVk87LZhqdP0t9RDj49PnOWK1TmX"
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

coveralls
