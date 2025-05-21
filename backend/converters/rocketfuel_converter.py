import re
import networkx as nx
import os

def parse_cch(file_path):
    nodes = {}
    total_links = 0
    ambiguous_nodes = 0
    disconnected_nodes = 0

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('-'):
                # Skip lines that start with '-euid =externaladdress rn'
                continue

            parts = line.strip().split()
            uid = parts[0]
            loc = parts[1]
            derived_from_dns = '+' in parts
            is_backbone = 'bb' in parts

            num_neigh_match = re.search(r'\((\d+)\)', line)
            num_neigh = int(num_neigh_match.group(1)) if num_neigh_match else 0

            ext_conns_match = re.search(r'&(\d+)', line)
            ext_conns = int(ext_conns_match.group(1)) if ext_conns_match else 0

            neighbors = re.findall(r'<(\d+)>', line)
            ext_neighbors = re.findall(r'{(\d+)}', line)

            name_match = re.search(r'=(\S+)', line)
            name = name_match.group(1) if name_match else ""

            not_responded = '!' in line

            rn_match = re.search(r'r(\d+)', line)
            rn = int(rn_match.group(1)) if rn_match else 0

            nodes[uid] = {
                'loc': loc,
                'derived_from_dns': derived_from_dns,
                'is_backbone': is_backbone,
                'num_neigh': num_neigh,
                'ext_conns': ext_conns,
                'name': name,
                'not_responded': not_responded,
                'rn': rn,
                'neighbors': neighbors,
                'ext_neighbors': ext_neighbors,
            }

            if loc == 'T':
                ambiguous_nodes += 1
            if num_neigh == 0:
                disconnected_nodes += 1

            total_links += num_neigh

    return nodes

def build_graph_from_cch(nodes):
    G = nx.MultiGraph()
    for uid, data in nodes.items():
        # Remove list attributes before adding nodes
        node_data = {k: v for k, v in data.items() if k not in ['neighbors', 'ext_neighbors']}
        G.add_node(uid, **node_data)

    for uid, data in nodes.items():
        for neighbor in data['neighbors']:
            if neighbor in G:
                G.add_edge(uid, neighbor)

        for ext_neighbor in data['ext_neighbors']:
            G.add_edge(uid, ext_neighbor, external=True)

    return G

def export_graph_to_graphml(G, output_path):
    nx.write_graphml(G, output_path)

def convert_cch_to_graphml(file_path):
    nodes = parse_cch(file_path)
    G = build_graph_from_cch(nodes)
    
    # Determine the filename for the GraphML file in the same directory
    output_path = os.path.splitext(file_path)[0] + '.graphml'
    export_graph_to_graphml(G, output_path)

    return output_path

