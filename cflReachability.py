import matplotlib.pyplot as plt
from collections import deque
import networkx as nx
import pandas as pd
import json

class Read:
    def __init__(self, csvGraphFileName="graph.json", csvCFGFile="CFG.json"):
        self.graphFile = csvGraphFileName
        self.cfgFile = csvCFGFile

    def graph(self):
        with open(self.graphFile, 'r') as fh:
            graph_data = json.load(fh)
            self.vertices = graph_data["Vertices"]
            self.edges = []
            for edge in graph_data["Edges"]:
                self.edges.append(edge.split(","))
            
            # plot graph
            self.G = nx.DiGraph()
            for edge in self.edges:
                self.G.add_edge(edge[0], edge[1], label=edge[2])
            return self.vertices, self.edges
    
    def cfg(self):
        with open(self.cfgFile, "r") as fh:
            data = json.load(fh)
        self.start_symbol = data['start_symbol']
        self.terminals = data['terminals']
        self.non_terminals = data["non_terminals"]
        self.productions = data["productions"]
        return self.terminals, self.non_terminals, self.productions, self.start_symbol



class FindPathFromSource(Read):
    def __init__(self, start_node):
        super().__init__()
        super().graph()
        super().cfg()
        # start_node
        self.start_node = start_node
        # start_symbol
        self.start_symbol = self.cfg()[-1]
        # productions
        self.productions = self.cfg()[-2]
        # W
        self.W = deque()
        for edge in self.edges: self.W.append(edge) 
        # E
        self.E = deque()
        for edge in self.edges: self.E.append(edge)
        # R
        self.R = set()

    def plot_graph(self):
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(self.G)
        nx.draw(self.G, pos, with_labels=True, node_color="skyblue", node_size=2000, font_size=16, font_weight="bold", arrows=True)
        edge_labels = nx.get_edge_attributes(self.G, "label") 
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
        plt.title("Graph with Labeled Edges")
        plt.show()

    def ApplyRules(self):
        for left, right in self.productions.items():
            if right == "epsilon":
                for v in self.vertices:
                    self.E.append([v,v,left])
                    self.W.append([v,v,left])

        while len(self.W) != 0:
            poped_edge = self.W.popleft()
            edge_label = poped_edge[2]
            for left, right in self.productions.items():
                #  Rule form of X --> d(d is terminal)
                if len(right) == 1:
                    if right == edge_label:
                        self.E.append([poped_edge[0],poped_edge[1],left])
                        self.W.append([poped_edge[0],poped_edge[1],left])
                        if (poped_edge[0] == self.start_node) and (left == self.start_symbol):
                            self.R.add(poped_edge[1])
                #  Rule form of X --> YZ
                if len(right) == 2:
                    symbols = []
                    for symbol in right:
                        symbols.append(symbol)
                    # YZ
                    for edge in list(self.E):
                        if edge[0] == poped_edge[1] and edge[2] == symbols[1]:
                            if [poped_edge[0],edge[1],left] not in self.E:
                                self.W.append([poped_edge[0],edge[1],left])
                                self.E.append([poped_edge[0],edge[1],left])
                                if poped_edge[0] == self.start_node and left == self.start_symbol:
                                    self.R.add(edge[1])
                    # ZY
                    for edge in list(self.E):
                        if edge[1] == poped_edge[0] and edge[2] == symbols[1]:
                            if [edge[0],poped_edge[1],left] not in self.E:
                                self.W.append([edge[0],poped_edge[1],left])
                                self.E.append([edge[0],poped_edge[1],left])
                                if poped_edge[0] == self.start_node and left == self.start_symbol:
                                    self.R.add(poped_edge[1])
        return self.R


if __name__ == '__main__':
    source_vertex = "A"
    a = FindPathFromSource(source_vertex).ApplyRules()
    print(a)
    FindPathFromSource(source_vertex).plot_graph()  