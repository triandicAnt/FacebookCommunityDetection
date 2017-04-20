# Market-Segmentation
Find market segments in social network data of Facebook users.

## Objective:
* Data consisted of users as nodes and their relationship between friends as their edges. 
* The algorithm detected communities in attributed graph data based on the structural, demographic (age, sex, ethnicity, education) and attribute similarities using Python's iGraph module. 
* The found segments were evaluated via influence propagation. 
* In influence propagation an entity in the segment is influenced and how fast the influence propagates over the entire network is evaluated. 
* The faster the influence propagates, the better is the segment.

## Data sets:
http://masonporter.blogspot.in/2011/02/facebook100-data-set.html

## Requirements:
* igraph : http://igraph.org/
* scipy

## Steps to Run:
* Load Facebook data and find market segments:
```python
python marketSegment.py
```
* Evaluate the results:
```R
evaluation.R
```
