import pandas as pd
import networkx as nx
import random
import matplotlib.pyplot as plt
import math
import numpy as np


class Environment:
    def __init__(self, nodes_amount: int, rounds_amount: int) -> None:
        self.nodes_amount = nodes_amount
        self.rounds_amount = rounds_amount
        self.graph = nx.Graph()
        self.graph_df = self.generate_df()
        self.dead = []
        self.energy = []

    def generate_df(self):
        """
        method that generate DataFramee which contains network data
        """
        data = []
        for i in range(self.nodes_amount):
            node = f"nodes_{i}"
            pos_x = random.randint(0, self.nodes_amount)
            pos_y = random.randint(0, self.nodes_amount - 10)
            pos = (pos_x, pos_y)
            energy = float(random.randint(300, 1000))
            is_ch = False
            color = "Green"
            is_dead = False
            is_taken = False
            ch = ""
            data.append(
                [node, pos, energy, is_ch, color, is_dead, is_taken, ch]
            )
        data.append(
            ["antenna", (self.nodes_amount/2, self.nodes_amount), float(300000), None, "Black", None, None, ""]
        )
        df = pd.DataFrame(
            data=data, columns=["node", "pos", "energy", "is_ch", "color", 'is_dead', 'is_taken' ,'ch'],
            index=[i for i in range(len(data))]
        )
        print("generated dataframe")
        return df
    
    def add_nodes(self):
        for i in range(self.nodes_amount+1):
            self.graph.add_node(self.graph_df.node[i], pos=self.graph_df.pos[i])
        
        print('added_nodes')
    
    def cluster_head_selection(self):
        def randomOddNumber(a,b):
                a = a // 2
                b = b // 2 - 1
                number = random.randint(a,b)
                number = (number * 2) + 1
                return number

        alive_nodes = self.graph_df.loc[(self.graph_df['is_dead'] == False)]
        random_amount = randomOddNumber(1, 9)
        while random_amount > len(alive_nodes.index.to_list()) and len(alive_nodes.index.to_list()) != 0:
            random_amount = randomOddNumber(1, 9)
        sample = random.sample(alive_nodes.index.to_list(), random_amount)

        
        for el in sample:
            alive_nodes.loc[el, ['is_ch']] = True
            alive_nodes.loc[el, ['color']] = "Red"
        
        self.graph_df.loc[(self.graph_df['is_dead'] == False)] = alive_nodes
        print('selected cluster heads')

    def antenna_edges(self):
        chs = self.graph_df.loc[self.graph_df['is_ch'] == True] #cluster heads
        antenna_pos = self.graph_df.loc[self.graph_df['node'] == "antenna"].pos.values[0] #antenna x, y cords
        antenna_name = "antenna"
        distances = []
        nodes = chs.node.values
        pos = chs.pos.values

        for i in range(len(nodes)):
            distance = math.sqrt(
                (pos[i][0]-antenna_pos[0])**2 + (pos[i][1]-antenna_pos[1])**2
                )
            distances.append([nodes[i], distance])
        distances = sorted(distances, key= lambda x:x[1])
        
        for i, distance in enumerate(distances):
            self.graph.add_edge(distance[0], antenna_name)
            antenna_name = distance[0]
        print('created edges to ant')

    def clustering(self):
        chs = self.graph_df.loc[self.graph_df['is_ch'] == True]
        for ch_node, ch_pos in zip(chs.node.values, chs.pos.values):
            random_cluster_child = random.randint(1,6)
            not_chs = self.graph_df.loc[(self.graph_df['is_ch'] == False) 
            & (self.graph_df['is_taken'] == False) & (self.graph_df['is_dead'] == False)]
            distances = []
            for node, pos in zip(not_chs.node.values, not_chs.pos.values):
                distance = math.sqrt(
                    (pos[0]-ch_pos[0])**2 + (pos[1] - ch_pos[1])**2
                )
                distances.append([node, distance])
            distances = sorted(distances, key= lambda x:x[1])
            
            for top in distances[0:random_cluster_child]:
                self.graph.add_edge(top[0], ch_node)
                index = not_chs.index[not_chs['node'] == top[0]].tolist()[0]
                not_chs.loc[index, 'is_taken'] = True
                not_chs.loc[index, 'ch'] = ch_node
            self.graph_df.loc[(self.graph_df['is_ch'] == False) & (self.graph_df['is_taken'] == False) & (self.graph_df['is_dead'] == False)] = not_chs
        print('clustered')

    
    def energy_consumption(self):
        ch = self.graph_df.loc[self.graph_df['is_ch'] == True]
        antennna_pos = self.graph_df.loc[self.graph_df['node'] == 'antenna'].pos.values[0]
        for ch_node, ch_pos in zip(ch.node.values, ch.pos.values):
            cluster_children = self.graph_df.loc[self.graph_df['ch'] == ch_node]
            #Cluster head power consumption
            distance_ant = math.sqrt(
                    (ch_pos[0]-antennna_pos[0])**2 + (ch_pos[1] - antennna_pos[1])**2
                )
            ch_power_consum = len(cluster_children)*distance_ant + distance_ant
            index = self.graph_df.index[self.graph_df['node'] == ch_node].tolist()[0]
            self.graph_df.loc[index, ['energy']] = self.graph_df.loc[index, ['energy']] - ch_power_consum

            #Cluster children power consumption
            
            nodes_power_consum = []
            for node, pos in zip(cluster_children.node.values, cluster_children.pos.values):
                distance = math.sqrt(
                    (pos[0]-ch_pos[0])**2 + (pos[1] - ch_pos[1])**2
                )
                nodes_power_consum.append([node, round(distance)])
            
            for node, power_consum in nodes_power_consum:
                index = self.graph_df.index[self.graph_df['node'] == node].tolist()[0]
                self.graph_df.loc[index, ['energy']] = self.graph_df.loc[index, ['energy']] - power_consum
        print('energy consume calculated')

    def dead_update(self):
        indexes = self.graph_df.index[
            (self.graph_df['energy'] <= 0.0) & (self.graph_df['is_dead']==False)
            ].tolist()

        for index in indexes:
            self.graph_df.loc[index, ['is_dead']] = True
            print("dead: update info")
            self.graph_df.loc[index, ['color']] = "Blue"
            print("dead: update color")
            self.graph_df.loc[index, ['is_ch']] = False
            print("dead: update isch")
            self.graph_df.loc[index, ['ch']] = ''
            self.graph_df.loc[index, ['energy']] = 0.0
            print("dead: update ch")
            self.graph_df.loc[index, ['is_taken']] = False
        print('dead updated')

    def new_state(self):
        indexes = self.graph_df.index[
            ((self.graph_df['is_ch'] == True) | (self.graph_df['ch'] != ""))
            & (self.graph_df['is_dead'] == False)
        ].tolist()

        for index in indexes:
            self.graph_df.loc[index, 'color'] = "Green"
            self.graph_df.loc[index, 'is_ch'] = False
            self.graph_df.loc[index, 'is_taken'] = False
            self.graph_df.loc[index, 'ch'] = ''
        print('clean_state')
    
    def not_all_dead(self):
        not_dead = self.graph_df.loc[self.graph_df['is_dead'] == False]
        if len(not_dead) != 0:
            return True
        else:
            return False
    
    def get_sum_of_dead_nodes(self):
        dead = len(self.graph_df.loc[self.graph_df['is_dead'] == True])
        self.dead.append(dead)
    
    def get_sum_of_energy(self):
        energy = self.graph_df['energy'].sum()
        self.energy.append(energy-300000.0)
    
    def draw_tests_plot(self):
        fig, axs = plt.subplots(2)
        x = np.linspace(0, self.rounds_amount, self.rounds_amount)
        print(x)
        y_dead = self.dead
        print(y_dead)
        y_energy = self.energy
        print(y_energy)
        axs[0].set_title('amount of dead nodes per round')
        axs[0].set_xlabel("amount of rounds")
        axs[0].set_ylabel("amount of dead nodes")
        axs[0].plot(x, y_dead)

        axs[1].set_title('amount of total energy per round')
        axs[1].set_xlabel("amount of rounds")
        axs[1].set_ylabel("amount of total energy")
        axs[1].plot(x, y_energy)

        fig.tight_layout()
        return fig

    def draw_graph(self):
        self.graph = nx.Graph()
        self.dead_update()
        self.get_sum_of_dead_nodes()
        self.get_sum_of_energy()
        self.new_state()
        self.add_nodes()
        if self.not_all_dead():
            self.cluster_head_selection()
            self.antenna_edges()
            self.clustering()
            self.energy_consumption()
        
        pos = nx.get_node_attributes(self.graph, 'pos')

        color = self.graph_df.color.tolist()
        return nx.draw(self.graph, pos=pos, node_color=color, node_size=50)
            



    