import os
import xml.etree.ElementTree as ET
import networkx as nx

def convert_xml_to_graphml(xml_file):
    # Read the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Create an empty directed multigraph
    G = nx.MultiGraph()

    # Iterate over nodes in the XML and add them to the graph
    for node in root.findall('.//{http://sndlib.zib.de/network}node'):
        node_id = node.get('id')
        x = float(node.find('.//{http://sndlib.zib.de/network}x').text)
        y = float(node.find('.//{http://sndlib.zib.de/network}y').text)
        G.add_node(node_id, x=x, y=y)

    # Iterate over links in the XML and add them to the graph
    for link in root.findall('.//{http://sndlib.zib.de/network}link'):
        link_id = link.get('id')
        source = link.find('.//{http://sndlib.zib.de/network}source').text
        target = link.find('.//{http://sndlib.zib.de/network}target').text
        capacity = float(link.find('.//{http://sndlib.zib.de/network}capacity').text)
        cost = float(link.find('.//{http://sndlib.zib.de/network}cost').text)
        G.add_edge(source, target, id=link_id, capacity=capacity, cost=cost)

    # Determine the filename for the GraphML file
    graphml_filename = os.path.splitext(xml_file)[0] + '.graphml'

    # Save the graph as a GraphML file
    nx.write_graphml(G, graphml_filename)

    return graphml_filename

