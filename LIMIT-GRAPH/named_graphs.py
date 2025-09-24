# -*- coding: utf-8 -*-
"""
Named Graphs for Provenance in LIMIT-Graph RDF Integration
Uses RDF named graphs to track annotator identity, language annotations, and RLHF feedback traces
Supports multilingual traceability and ethical audit trails
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

# RDF libraries
from rdflib import Graph, URIRef, Literal, Namespace, BNode, Dataset
from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD, FOAF, DC, DCTERMS

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

@dataclass
class AnnotatorProfile:
    """Profile information for an annotator"""
    annotator_id: str
    name: str
    expertise_domains: List[str]
    languages: List[str]
    reliability_score: float
    annotation_count: int
    created_date: datetime

@dataclass
class LanguageAnnotation:
    """Language-specific annotation metadata"""
    text: str
    language_code: str
    confidence: float
    detection_method: str
    cultural_context: Optional[str] = None
    dialect_variant: Optional[str] = None

@dataclass
class RLHFFeedbackTrace:
    """RLHF feedback trace with full audit trail"""
    feedback_id: str
    statement_id: str
    feedback_type: str  # 'positive', 'negative', 'correction'
    quality_score: float
    relevance_score: float
    cultural_appropriateness: float
    feedback_text: Optional[str]
    annotator_id: str
    timestamp: datetime
    session_id: Optional[str] = None

class LimitGraphNamedGraphManager:
    """
    Manages named graphs for LIMIT-Graph RDF data with comprehensive provenance tracking
    Supports multilingual annotations, annotator profiles, and RLHF feedback traces
    """
    
    def __init__(self, base_uri: str = "http://limitgraph.org/"):
        """Initialize the named graph manager"""
        self.base_uri = base_uri
        
        # Define namespaces
        self.LG = Namespace(base_uri)
        self.LGONT = Namespace(f"{base_uri}ontology/")
        self.LGDATA = Namespace(f"{base_uri}data/")
        self.LGPROV = Namespace(f"{base_uri}provenance/")
        self.LGRLHF = Namespace(f"{base_uri}rlhf/")
        self.LGANG = Namespace(f"{base_uri}annotators/")
        self.LGLANG = Namespace(f"{base_uri}languages/")
        
        # Initialize RDF dataset (supports named graphs)
        self.dataset = Dataset()
        self._bind_namespaces()
        
        # Named graph URIs
        self.graphs = {
            'main': URIRef(f"{base_uri}graphs/main"),
            'provenance': URIRef(f"{base_uri}graphs/provenance"),
            'annotators': URIRef(f"{base_uri}graphs/annotators"),
            'languages': URIRef(f"{base_uri}graphs/languages"),
            'rlhf': URIRef(f"{base_uri}graphs/rlhf"),
            'audit': URIRef(f"{base_uri}graphs/audit")
        }
        
        # Initialize named graphs
        for graph_name, graph_uri in self.graphs.items():
            self.dataset.graph(graph_uri)
        
        # Annotator registry
        self.annotators: Dict[str, AnnotatorProfile] = {}
        
        # Language support
        self.supported_languages = {
            'en': {'name': 'English', 'rtl': False, 'script': 'Latin'},
            'es': {'name': 'Spanish', 'rtl': False, 'script': 'Latin'},
            'ar': {'name': 'Arabic', 'rtl': True, 'script': 'Arabic'},
            'id': {'name': 'Indonesian', 'rtl': False, 'script': 'Latin'},
            'zh': {'name': 'Chinese', 'rtl': False, 'script': 'Chinese'},
            'hi': {'name': 'Hindi', 'rtl': False, 'script': 'Devanagari'}
        }
        
        print("🏷️ LIMIT-Graph Named Graph Manager initialized")
    
    def _bind_namespaces(self):
        """Bind common namespaces to all graphs"""
        namespaces = [
            ("lg", self.LG),
            ("lgont", self.LGONT),
            ("lgdata", self.LGDATA),
            ("lgprov", self.LGPROV),
            ("lgrlhf", self.LGRLHF),
            ("lgang", self.LGANG),
            ("lglang", self.LGLANG),
            ("rdf", RDF),
            ("rdfs", RDFS),
            ("owl", OWL),
            ("skos", SKOS),
            ("foaf", FOAF),
            ("dc", DC),
            ("dcterms", DCTERMS)
        ]
        
        for prefix, namespace in namespaces:
            for graph in self.dataset.graphs():
                graph.bind(prefix, namespace)
    
    def register_annotator(self, annotator_profile: AnnotatorProfile) -> str:
        """Register an annotator and create their profile in the annotators graph"""
        
        self.annotators[annotator_profile.annotator_id] = annotator_profile
        
        # Add to annotators named graph
        annotators_graph = self.dataset.graph(self.graphs['annotators'])
        annotator_uri = self.LGANG[annotator_profile.annotator_id]
        
        # Basic profile information
        annotators_graph.add((annotator_uri, RDF.type, self.LGONT.Annotator))
        annotators_graph.add((annotator_uri, FOAF.name, Literal(annotator_profile.name)))
        annotators_graph.add((annotator_uri, self.LGONT.annotatorId, Literal(annotator_profile.annotator_id)))
        annotators_graph.add((annotator_uri, self.LGONT.reliabilityScore, 
                             Literal(annotator_profile.reliability_score, datatype=XSD.float)))
        annotators_graph.add((annotator_uri, self.LGONT.annotationCount, 
                             Literal(annotator_profile.annotation_count, datatype=XSD.integer)))
        annotators_graph.add((annotator_uri, DCTERMS.created, 
                             Literal(annotator_profile.created_date.isoformat(), datatype=XSD.dateTime)))
        
        # Expertise domains
        for domain in annotator_profile.expertise_domains:
            annotators_graph.add((annotator_uri, self.LGONT.expertiseIn, Literal(domain)))
        
        # Languages
        for lang in annotator_profile.languages:
            lang_uri = self.LGLANG[lang]
            annotators_graph.add((annotator_uri, self.LGONT.speaksLanguage, lang_uri))
        
        print(f"👤 Registered annotator: {annotator_profile.name} ({annotator_profile.annotator_id})")
        return annotator_profile.annotator_id
    
    def add_language_annotation(self, statement_uri: URIRef, 
                               language_annotation: LanguageAnnotation) -> str:
        """Add language annotation to the languages named graph"""
        
        languages_graph = self.dataset.graph(self.graphs['languages'])
        
        # Create language annotation URI
        lang_annotation_id = str(uuid.uuid4())
        lang_annotation_uri = self.LGLANG[f"annotation_{lang_annotation_id}"]
        
        # Add language annotation
        languages_graph.add((lang_annotation_uri, RDF.type, self.LGONT.LanguageAnnotation))
        languages_graph.add((lang_annotation_uri, self.LGONT.annotatesStatement, statement_uri))
        languages_graph.add((lang_annotation_uri, self.LGONT.text, 
                            Literal(language_annotation.text, lang=language_annotation.language_code)))
        languages_graph.add((lang_annotation_uri, self.LGONT.languageCode, 
                            Literal(language_annotation.language_code)))
        languages_graph.add((lang_annotation_uri, self.LGONT.confidence, 
                            Literal(language_annotation.confidence, datatype=XSD.float)))
        languages_graph.add((lang_annotation_uri, self.LGONT.detectionMethod, 
                            Literal(language_annotation.detection_method)))
        
        # Optional cultural context
        if language_annotation.cultural_context:
            languages_graph.add((lang_annotation_uri, self.LGONT.culturalContext, 
                               Literal(language_annotation.cultural_context)))
        
        # Optional dialect variant
        if language_annotation.dialect_variant:
            languages_graph.add((lang_annotation_uri, self.LGONT.dialectVariant, 
                               Literal(language_annotation.dialect_variant)))
        
        # Add language metadata if not exists
        self._ensure_language_metadata(language_annotation.language_code)
        
        return lang_annotation_id
    
    def add_rlhf_feedback_trace(self, feedback_trace: RLHFFeedbackTrace) -> str:
        """Add RLHF feedback trace to the RLHF named graph"""
        
        rlhf_graph = self.dataset.graph(self.graphs['rlhf'])
        
        # Create feedback URI
        feedback_uri = self.LGRLHF[f"feedback_{feedback_trace.feedback_id}"]
        
        # Add feedback trace
        rlhf_graph.add((feedback_uri, RDF.type, self.LGONT.RLHFFeedback))
        rlhf_graph.add((feedback_uri, self.LGONT.feedbackId, Literal(feedback_trace.feedback_id)))
        rlhf_graph.add((feedback_uri, self.LGONT.statementId, Literal(feedback_trace.statement_id)))
        rlhf_graph.add((feedback_uri, self.LGONT.feedbackType, Literal(feedback_trace.feedback_type)))
        rlhf_graph.add((feedback_uri, self.LGONT.qualityScore, 
                       Literal(feedback_trace.quality_score, datatype=XSD.float)))
        rlhf_graph.add((feedback_uri, self.LGONT.relevanceScore, 
                       Literal(feedback_trace.relevance_score, datatype=XSD.float)))
        rlhf_graph.add((feedback_uri, self.LGONT.culturalAppropriateness, 
                       Literal(feedback_trace.cultural_appropriateness, datatype=XSD.float)))
        rlhf_graph.add((feedback_uri, DCTERMS.created, 
                       Literal(feedback_trace.timestamp.isoformat(), datatype=XSD.dateTime)))
        
        # Annotator reference
        annotator_uri = self.LGANG[feedback_trace.annotator_id]
        rlhf_graph.add((feedback_uri, self.LGONT.providedBy, annotator_uri))
        
        # Optional feedback text
        if feedback_trace.feedback_text:
            rlhf_graph.add((feedback_uri, self.LGONT.feedbackText, 
                           Literal(feedback_trace.feedback_text)))
        
        # Optional session ID
        if feedback_trace.session_id:
            rlhf_graph.add((feedback_uri, self.LGONT.sessionId, 
                           Literal(feedback_trace.session_id)))
        
        # Add to audit trail
        self._add_audit_entry("rlhf_feedback_added", {
            "feedback_id": feedback_trace.feedback_id,
            "annotator_id": feedback_trace.annotator_id,
            "feedback_type": feedback_trace.feedback_type
        })
        
        return feedback_trace.feedback_id
    
    def add_provenance_trace(self, statement_uri: URIRef, provenance_data: Dict[str, Any]) -> str:
        """Add comprehensive provenance information to the provenance named graph"""
        
        provenance_graph = self.dataset.graph(self.graphs['provenance'])
        
        # Create provenance URI
        prov_id = str(uuid.uuid4())
        prov_uri = self.LGPROV[f"provenance_{prov_id}"]
        
        # Add provenance information
        provenance_graph.add((prov_uri, RDF.type, self.LGONT.ProvenanceRecord))
        provenance_graph.add((prov_uri, self.LGONT.tracesStatement, statement_uri))
        provenance_graph.add((prov_uri, DCTERMS.created, 
                             Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Add provenance details
        for key, value in provenance_data.items():
            prop_uri = self.LGPROV[self._clean_uri_component(key)]
            
            if isinstance(value, (int, float)):
                datatype = XSD.float if isinstance(value, float) else XSD.integer
                provenance_graph.add((prov_uri, prop_uri, Literal(value, datatype=datatype)))
            elif isinstance(value, bool):
                provenance_graph.add((prov_uri, prop_uri, Literal(value, datatype=XSD.boolean)))
            elif isinstance(value, datetime):
                provenance_graph.add((prov_uri, prop_uri, Literal(value.isoformat(), datatype=XSD.dateTime)))
            else:
                provenance_graph.add((prov_uri, prop_uri, Literal(str(value))))
        
        return prov_id
    
    def _ensure_language_metadata(self, language_code: str):
        """Ensure language metadata exists in the languages graph"""
        
        languages_graph = self.dataset.graph(self.graphs['languages'])
        lang_uri = self.LGLANG[language_code]
        
        # Check if language already exists
        if (lang_uri, RDF.type, self.LGONT.Language) in languages_graph:
            return
        
        # Add language metadata
        languages_graph.add((lang_uri, RDF.type, self.LGONT.Language))
        languages_graph.add((lang_uri, self.LGONT.languageCode, Literal(language_code)))
        
        if language_code in self.supported_languages:
            lang_info = self.supported_languages[language_code]
            languages_graph.add((lang_uri, RDFS.label, Literal(lang_info['name'])))
            languages_graph.add((lang_uri, self.LGONT.isRightToLeft, 
                               Literal(lang_info['rtl'], datatype=XSD.boolean)))
            languages_graph.add((lang_uri, self.LGONT.script, Literal(lang_info['script'])))
    
    def _add_audit_entry(self, action: str, details: Dict[str, Any]):
        """Add entry to audit trail"""
        
        audit_graph = self.dataset.graph(self.graphs['audit'])
        
        # Create audit entry
        audit_id = str(uuid.uuid4())
        audit_uri = self.LGPROV[f"audit_{audit_id}"]
        
        audit_graph.add((audit_uri, RDF.type, self.LGONT.AuditEntry))
        audit_graph.add((audit_uri, self.LGONT.action, Literal(action)))
        audit_graph.add((audit_uri, DCTERMS.created, 
                        Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Add details
        for key, value in details.items():
            prop_uri = self.LGPROV[self._clean_uri_component(key)]
            audit_graph.add((audit_uri, prop_uri, Literal(str(value))))
    
    def _clean_uri_component(self, component: str) -> str:
        """Clean a string to be used as URI component"""
        cleaned = component.replace(" ", "_").replace("-", "_")
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")
        return cleaned
    
    def query_by_annotator(self, annotator_id: str) -> List[Dict[str, Any]]:
        """Query all statements by a specific annotator"""
        
        query = f"""
        PREFIX lg: <{self.LG}>
        PREFIX lgont: <{self.LGONT}>
        PREFIX lgprov: <{self.LGPROV}>
        PREFIX lgang: <{self.LGANG}>
        
        SELECT ?statement ?subject ?predicate ?object ?confidence ?timestamp
        WHERE {{
            GRAPH <{self.graphs['provenance']}> {{
                ?prov lgont:tracesStatement ?statement .
                ?prov lgont:annotatorId "{annotator_id}" .
                ?prov lgont:confidence ?confidence .
                ?prov lgont:timestamp ?timestamp .
            }}
            GRAPH <{self.graphs['main']}> {{
                ?statement lgont:hasSubject ?subject .
                ?statement lgont:hasPredicate ?predicate .
                ?statement lgont:hasObject ?object .
            }}
        }}
        ORDER BY DESC(?timestamp)
        """
        
        results = []
        for row in self.dataset.query(query):
            results.append({
                'statement': str(row.statement),
                'subject': str(row.subject),
                'predicate': str(row.predicate),
                'object': str(row.object),
                'confidence': float(row.confidence),
                'timestamp': str(row.timestamp)
            })
        
        return results
    
    def query_by_language(self, language_code: str) -> List[Dict[str, Any]]:
        """Query all statements in a specific language"""
        
        query = f"""
        PREFIX lg: <{self.LG}>
        PREFIX lgont: <{self.LGONT}>
        PREFIX lglang: <{self.LGLANG}>
        
        SELECT ?statement ?text ?confidence ?detectionMethod
        WHERE {{
            GRAPH <{self.graphs['languages']}> {{
                ?langAnnotation lgont:annotatesStatement ?statement .
                ?langAnnotation lgont:languageCode "{language_code}" .
                ?langAnnotation lgont:text ?text .
                ?langAnnotation lgont:confidence ?confidence .
                ?langAnnotation lgont:detectionMethod ?detectionMethod .
            }}
        }}
        ORDER BY DESC(?confidence)
        """
        
        results = []
        for row in self.dataset.query(query):
            results.append({
                'statement': str(row.statement),
                'text': str(row.text),
                'confidence': float(row.confidence),
                'detection_method': str(row.detectionMethod)
            })
        
        return results
    
    def query_rlhf_feedback(self, feedback_type: Optional[str] = None, 
                           min_quality_score: float = 0.0) -> List[Dict[str, Any]]:
        """Query RLHF feedback with optional filters"""
        
        filter_clause = ""
        if feedback_type:
            filter_clause += f'FILTER(?feedbackType = "{feedback_type}") .'
        if min_quality_score > 0:
            filter_clause += f'FILTER(?qualityScore >= {min_quality_score}) .'
        
        query = f"""
        PREFIX lg: <{self.LG}>
        PREFIX lgont: <{self.LGONT}>
        PREFIX lgrlhf: <{self.LGRLHF}>
        PREFIX dcterms: <{DCTERMS}>
        
        SELECT ?feedback ?statementId ?feedbackType ?qualityScore ?relevanceScore 
               ?culturalAppropriateness ?annotatorId ?timestamp
        WHERE {{
            GRAPH <{self.graphs['rlhf']}> {{
                ?feedback lgont:statementId ?statementId .
                ?feedback lgont:feedbackType ?feedbackType .
                ?feedback lgont:qualityScore ?qualityScore .
                ?feedback lgont:relevanceScore ?relevanceScore .
                ?feedback lgont:culturalAppropriateness ?culturalAppropriateness .
                ?feedback dcterms:created ?timestamp .
            }}
            GRAPH <{self.graphs['annotators']}> {{
                ?annotator lgont:annotatorId ?annotatorId .
            }}
            GRAPH <{self.graphs['rlhf']}> {{
                ?feedback lgont:providedBy ?annotator .
            }}
            {filter_clause}
        }}
        ORDER BY DESC(?timestamp)
        """
        
        results = []
        for row in self.dataset.query(query):
            results.append({
                'feedback_id': str(row.feedback),
                'statement_id': str(row.statementId),
                'feedback_type': str(row.feedbackType),
                'quality_score': float(row.qualityScore),
                'relevance_score': float(row.relevanceScore),
                'cultural_appropriateness': float(row.culturalAppropriateness),
                'annotator_id': str(row.annotatorId),
                'timestamp': str(row.timestamp)
            })
        
        return results
    
    def export_named_graphs(self, output_dir: str = "output/rdf/named_graphs/"):
        """Export each named graph to separate files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = {}
        
        for graph_name, graph_uri in self.graphs.items():
            graph = self.dataset.graph(graph_uri)
            
            # Export in multiple formats
            formats = {'turtle': 'ttl', 'xml': 'rdf', 'json-ld': 'jsonld'}
            
            for format_name, extension in formats.items():
                try:
                    filename = f"{graph_name}_graph.{extension}"
                    filepath = os.path.join(output_dir, filename)
                    
                    graph.serialize(destination=filepath, format=format_name)
                    
                    if graph_name not in exported_files:
                        exported_files[graph_name] = {}
                    exported_files[graph_name][format_name] = filepath
                    
                    print(f"✅ Exported {graph_name} graph ({format_name}) to {filepath}")
                    
                except Exception as e:
                    print(f"❌ Failed to export {graph_name} graph ({format_name}): {e}")
        
        return exported_files
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all named graphs"""
        
        stats = {}
        
        for graph_name, graph_uri in self.graphs.items():
            graph = self.dataset.graph(graph_uri)
            stats[graph_name] = {
                'triples_count': len(graph),
                'subjects_count': len(set(graph.subjects())),
                'predicates_count': len(set(graph.predicates())),
                'objects_count': len(set(graph.objects()))
            }
        
        # Overall statistics
        stats['overall'] = {
            'total_triples': sum(stats[g]['triples_count'] for g in stats),
            'annotators_registered': len(self.annotators),
            'languages_supported': len(self.supported_languages),
            'named_graphs': len(self.graphs)
        }
        
        return stats

# Demo and testing functions
def demo_named_graphs():
    """Demonstrate named graphs capabilities"""
    
    print("🏷️ LIMIT-Graph Named Graphs Demo")
    
    # Initialize manager
    manager = LimitGraphNamedGraphManager()
    
    # Register annotators
    annotator1 = AnnotatorProfile(
        annotator_id="ann_001",
        name="Dr. Maria Rodriguez",
        expertise_domains=["linguistics", "spanish_nlp"],
        languages=["es", "en"],
        reliability_score=0.95,
        annotation_count=1250,
        created_date=datetime.now()
    )
    
    annotator2 = AnnotatorProfile(
        annotator_id="ann_002",
        name="Ahmad Hassan",
        expertise_domains=["arabic_nlp", "cultural_studies"],
        languages=["ar", "en"],
        reliability_score=0.92,
        annotation_count=890,
        created_date=datetime.now()
    )
    
    manager.register_annotator(annotator1)
    manager.register_annotator(annotator2)
    
    # Create sample statement URI
    statement_uri = URIRef("http://limitgraph.org/data/statement_001")
    
    # Add language annotation
    lang_annotation = LanguageAnnotation(
        text="A Andrés le gustan las manzanas",
        language_code="es",
        confidence=0.98,
        detection_method="pattern_matching",
        cultural_context="latin_american",
        dialect_variant="mexican_spanish"
    )
    
    manager.add_language_annotation(statement_uri, lang_annotation)
    
    # Add RLHF feedback
    rlhf_feedback = RLHFFeedbackTrace(
        feedback_id="fb_001",
        statement_id="statement_001",
        feedback_type="positive",
        quality_score=0.9,
        relevance_score=0.85,
        cultural_appropriateness=0.95,
        feedback_text="Excellent extraction of Spanish preference statement",
        annotator_id="ann_001",
        timestamp=datetime.now(),
        session_id="session_123"
    )
    
    manager.add_rlhf_feedback_trace(rlhf_feedback)
    
    # Add provenance
    provenance_data = {
        "extraction_method": "regex_pattern",
        "source_document": "d12",
        "extraction_confidence": 0.92,
        "processing_time_ms": 45,
        "model_version": "v1.2.3"
    }
    
    manager.add_provenance_trace(statement_uri, provenance_data)
    
    # Query examples
    print(f"\n🔍 Query Results:")
    
    # Query by annotator
    ann_results = manager.query_by_annotator("ann_001")
    print(f"  - Statements by ann_001: {len(ann_results)}")
    
    # Query by language
    es_results = manager.query_by_language("es")
    print(f"  - Spanish statements: {len(es_results)}")
    
    # Query RLHF feedback
    feedback_results = manager.query_rlhf_feedback(feedback_type="positive")
    print(f"  - Positive feedback: {len(feedback_results)}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\n📊 Named Graphs Statistics:")
    for graph_name, graph_stats in stats.items():
        if graph_name != 'overall':
            print(f"  - {graph_name}: {graph_stats['triples_count']} triples")
    
    print(f"  - Overall: {stats['overall']['total_triples']} total triples")
    
    # Export named graphs
    exported_files = manager.export_named_graphs()
    print(f"\n💾 Exported named graphs: {len(exported_files)} graphs")
    
    return manager

if __name__ == "__main__":
    demo_named_graphs()