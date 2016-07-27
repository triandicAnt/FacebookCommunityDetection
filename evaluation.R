library(igraph)
#install.packages("akmeans")
library("akmeans")

## Influence Propagation
# Arguments:
# Graph = Structural Graph, Igraph Instance
# Comm  = Communiity/Clusters
# Beta = Influence Propagation Rate

influence_propagation <- function(graph, comm, beta=0.75){
  output = c()
  v = vcount(graph)
  nodes <- data.frame(1:v)
  colnames(nodes) <- c("Id")
  nodes$comm = comm
  nodes$color = "green"
  
  influencers = c()
  for(k in unique(comm)){
    influencer = sample(nodes[which(nodes$comm %in% k), c("Id")],1)
    influencers = append(influencers, influencer)           
  }
  
  nodes[nodes$Id %in% influencers, c("color")] <- "red"
  new_influencers = influencers
  total_influencers = length(influencers)
  
  timestep = 1
  old_influencers = 0
  ratio = total_influencers/v
  
  cat("Time Step = " , timestep,", Total Influencers = ", total_influencers, ", Network Coverage = " , ratio ,"\n")
  output = data.frame(timestep, total_influencers)
  
  timestep = timestep + 1
  alpha = 0.7
  
  #while(total_influencers - old_influencers > 0 && ratio < 1){
  for(i in 1:15){
    old_influencers = total_influencers
    influencers = new_influencers
    for(i in influencers){
      nbs = neighbors(graph, i)
      ## Selection if the propagation is inside community or outside
      flag = "inside"
      if(sample(1:100, 1) <= alpha*100){
        
        candidates = nodes[nodes$comm == nodes[i, c("comm")] & nodes$color == "green", c("Id")]
        candidates = intersect(candidates, nbs)
        ids <- c()
        for(j in candidates){
          if(j %in% nbs && sample(1:100, 1) <= beta * 100){     # Stochastically determining if node will get infected, using beta transmission probability
            ids <- append(ids, j)
          }  
        }    
      }else{
        candidates = nodes[nodes$comm != nodes[i, c("comm")] & nodes$color == "green", c("Id")]
        candidates = intersect(candidates, nbs)
        ids <- c()
        for(j in candidates){
          if(sample(1:100, 1) <= beta * 100){     # Stochastically determining if node will get infected, using beta transmission probability
            ids <- append(ids, j)
          }  
        }
      }
      nodes[which(nodes$Id %in% ids), c("color")] <- "red" 
      total_influencers = nrow(nodes[nodes$color == "red",])
      new_influencers = append(new_influencers, unique(ids))
    }  
    ratio = nrow(nodes[nodes$color == "red",])/v
    cat("Time Step = " ,timestep,", Total Influencers = ", total_influencers, ", Network Coverage = ", ratio ,"\n")
    output = rbind(output, data.frame(timestep, total_influencers))
    timestep = timestep + 1
  }
  output
}

## Influence Propagation Example

# ===== Reading the graph ====== #
g <- read.graph(file="data/fb_caltech_small_edgelist.txt", format = c("edgelist"))

# ===== Read communities file ==== #
comm = integer(vcount(g))

conn <- file("communities.txt", open="r")
lines <-readLines(conn)
for (i in 1:length(lines)){
    verts = unlist(strsplit(lines[i], ","))
    verts = as.integer(verts) + 1   # R indexes start at 1
    comm[verts] = i
}
close(conn)


# ===== Clusters From Adaptive K-means ===== #
attrData <- read.csv("data/fb_caltech_small_attrlist.csv")
akm = akmeans(attrData, d.metric=2, ths3=.4, mode=3, 
              min.k=length(unique(comm)), max.k=length(unique(comm))) ## cosine distance based

# ===== Influence Propagation Using adaptive k-means clusters ===== #
op1 = influence_propagation(graph=g, comm = akm$cluster)

# ===== Influence Propagation Using SAC-1 communities  ===== #
op2 = influence_propagation(graph=g, comm = comm)

print("here")


## Plot for the timestep comparison 
tsteps = as.vector(op1$timestep)
tsteps = append(tsteps, as.vector(op2$timestep))
plot(op1, type="b", col=2, pch=20, ylim = c(0, vcount(g)), xlim = c(1, max(tsteps)), main = "Influence Propagation")
points(op2, type="b", col=3, pch=20)
legend("bottomright",  c("Adaptive-Kmeans","SAC-1"), col=2:3, pch=c(20,20))
