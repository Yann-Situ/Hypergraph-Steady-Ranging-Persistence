# Steady and Ranging Persistence for Hypergraphs
Small piece of code in python to compute steady and ranging persistence of features of a hypergraph filtration.

Part of the code (mostly the file `persistence.py`) is borrowed from the following [Generalized Persistence Analysis](https://github.com/LimenResearch/gpa) tool.

## Dependencies
The code uses the following python module:
- sys, matplotlib, numpy, math, collections, colorsys;
- [HyperNetX](https://github.com/pnnl/HyperNetX) for hypergraph handling and visualization;
- [tqdm](https://github.com/tqdm/tqdm) for progress bar (optional).

## Usage
In this repository, the tests are made with data derived from William Shakespeare’s plays. The data files are stored in the `data/` folder and were taken from the [Hyperbard](https://hyperbard.net/) dataset.
Here is a [great link](https://www.cs.cornell.edu/~arb/data/) for plenty of other hypergraph datasets.

To perform the test, go to the repository and call:
```
python3 test_hyperbard.py filename
```
with filename being a hyperbard `edges.csv` file, for instance:
```
python3 test_hyperbard.py data/king-lear_hg-scene-mw.edges.csv
```

First, the script will open the hyperbard file to build two hypergraph 
filtrations: the scene-hypergraph and the character-hypergraph filtrations of the play.
The script will plot a sample of this two filtrations (for t=3,5,7,9).

Second, the script will compute four persistence diagrams for each filtrations:
- the steady persistence for the hyperhub feature;
- the ranging persistence for the hyperhub feature;
- the steady(=ranging) persistence for the exclusivity feature;
- the steady(=ranging) persistence for the max originality feature.

## Example
Example of steady and ranging persistence for the scene-hypergraph filtration of *King Lear*:
![sample-steady-ranging-persistence](https://github.com/user-attachments/assets/245e1daf-f7e5-4dff-af91-f9c44a93d8b1)
