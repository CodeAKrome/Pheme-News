from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt


# pip install py2neo networkx matplotlib


class CypherGraphVisualizer:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))
        self.G = nx.DiGraph()

    def run_query(self, cypher_query):
        results = self.graph.run(cypher_query)
        for record in results:
            n = record['n']
            m = record['m']
            r = record['r']
            self.G.add_node(n.identity, label=n['name'])
            self.G.add_node(m.identity, label=m['name'])
            self.G.add_edge(n.identity, m.identity, label=r.__class__.__name__)

    def visualize(self, save_path=None):
        pos = nx.spring_layout(self.G)
        nx.draw(self.G, pos, with_labels=True, labels=nx.get_node_attributes(self.G, 'label'),
                node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, 'label'))

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

# Usage
if __name__ == "__main__":
    visualizer = CypherGraphVisualizer("bolt://localhost:7687", "neo4j", "password")
    cypher_query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    visualizer.run_query(cypher_query)
    visualizer.visualize("graph.png")  # Save to file
    # visualizer.visualize()  # To display without saving