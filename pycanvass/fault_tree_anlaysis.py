"""
Try to discover what happened and why it happened.
"""

from graphviz import Digraph

def create_event_tree():
    print("Create a Fault Tree for Event Analysis")
    name_of_tree = input("[?] Name of analysis")
    dot = Digraph(comment=name_of_tree)
    
