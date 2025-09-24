# -*- coding: utf-8 -*-
"""
LIMIT-Graph RDF Integration Package
Comprehensive RDF support for LIMIT-Graph with multilingual capabilities
"""

from .triple_generator import LimitGraphTripleGenerator, LimitGraphTriple, RDFConversionResult
from .named_graphs import (
    LimitGraphNamedGraphManager, 
    AnnotatorProfile, 
    LanguageAnnotation, 
    RLHFFeedbackTrace
)
from .ontology_templates import (
    LimitGraphOntologyBuilder, 
    OntologyClass, 
    OntologyProperty
)
from .sparql_interface import (
    LimitGraphSPARQLInterface, 
    SPARQLQueryResult, 
    QueryTemplate
)

__version__ = "1.0.0"
__author__ = "LIMIT-Graph RDF Team"

__all__ = [
    # Triple Generation
    'LimitGraphTripleGenerator',
    'LimitGraphTriple', 
    'RDFConversionResult',
    
    # Named Graphs
    'LimitGraphNamedGraphManager',
    'AnnotatorProfile',
    'LanguageAnnotation', 
    'RLHFFeedbackTrace',
    
    # Ontology Templates
    'LimitGraphOntologyBuilder',
    'OntologyClass',
    'OntologyProperty',
    
    # SPARQL Interface
    'LimitGraphSPARQLInterface',
    'SPARQLQueryResult',
    'QueryTemplate'
]

def create_full_rdf_system(base_uri: str = "http://limitgraph.org/"):
    """
    Create a complete RDF system with all components integrated
    
    Returns:
        dict: Dictionary containing all RDF system components
    """
    
    # Initialize components
    triple_generator = LimitGraphTripleGenerator(base_uri)
    named_graph_manager = LimitGraphNamedGraphManager(base_uri)
    ontology_builder = LimitGraphOntologyBuilder(base_uri + "ontology/")
    sparql_interface = LimitGraphSPARQLInterface(named_graph_manager.dataset, base_uri)
    
    # Create core ontology
    ontology_builder.create_core_ontology()
    
    return {
        'triple_generator': triple_generator,
        'named_graph_manager': named_graph_manager,
        'ontology_builder': ontology_builder,
        'sparql_interface': sparql_interface,
        'base_uri': base_uri
    }

def demo_full_integration():
    """Demonstrate full RDF integration capabilities"""
    
    print("🚀 LIMIT-Graph Full RDF Integration Demo")
    
    # Create full system
    rdf_system = create_full_rdf_system()
    
    print("✅ All RDF components initialized successfully!")
    print(f"  - Triple Generator: Ready")
    print(f"  - Named Graph Manager: Ready") 
    print(f"  - Ontology Builder: Ready")
    print(f"  - SPARQL Interface: Ready")
    
    return rdf_system

if __name__ == "__main__":
    demo_full_integration()
