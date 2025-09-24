from rdflib import Graph, URIRef, Literal, Namespace

def limitgraph_to_rdf(triples, base_uri="http://limitgraph.org/"):
    g = Graph()
    LG = Namespace(base_uri)

    for subj, pred, obj in triples:
        g.add((URIRef(LG[subj]), URIRef(LG[pred]), URIRef(LG[obj])))

    return g
