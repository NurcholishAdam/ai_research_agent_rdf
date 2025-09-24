# -*- coding: utf-8 -*-
"""
Triple Generator Scaffold for LIMIT-Graph RDF Integration
Converts LIMIT-Graph edges into RDF triples using rdflib
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

# RDF libraries
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD, FOAF, DC, DCTERMS

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

@dataclass
class LimitGraphTriple:
    """Represents a LIMIT-Graph triple with metadata"""
    subject: str
    predicate: str
    object: str
    confidence: float
    source_language: str
    annotator_id: str
    timestamp: datetime
    rlhf_feedback: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None

@dataclass
class RDFConversionResult:
    """Result of RDF conversion process"""
    graph: Graph
    triples_count: int
    languages_detected: List[str]
    annotators: List[str]
    conversion_metadata: Dict[str, Any]

class LimitGraphTripleGenerator:
    """
    Converts LIMIT-Graph edges into RDF triples with full provenance tracking
    Supports multilingual annotations and RLHF feedback integration
    """
    
    def __init__(self, base_uri: str = "http://limitgraph.org/"):
        """Initialize the triple generator"""
        self.base_uri = base_uri
        
        # Define namespaces
        self.LG = Namespace(base_uri)
        self.LGONT = Namespace(f"{base_uri}ontology/")
        self.LGDATA = Namespace(f"{base_uri}data/")
        self.LGPROV = Namespace(f"{base_uri}provenance/")
        self.LGRLHF = Namespace(f"{base_uri}rlhf/")
        
        # Initialize RDF graph
        self.graph = Graph()
        self._bind_namespaces()
        
        # Language detection patterns
        self.language_patterns = {
            'es': ['el', 'la', 'los', 'las', 'de', 'del', 'en', 'con', 'por', 'para', 'que', 'es', 'son'],
            'ar': ['في', 'من', 'إلى', 'على', 'مع', 'هو', 'هي', 'التي', 'الذي'],
            'id': ['yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'dengan', 'adalah', 'ini', 'itu'],
            'en': ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'from', 'with', 'is', 'are']
        }
        
        print("🔗 LIMIT-Graph Triple Generator initialized")
    
    def _bind_namespaces(self):
        """Bind common namespaces to the graph"""
        self.graph.bind("lg", self.LG)
        self.graph.bind("lgont", self.LGONT)
        self.graph.bind("lgdata", self.LGDATA)
        self.graph.bind("lgprov", self.LGPROV)
        self.graph.bind("lgrlhf", self.LGRLHF)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("skos", SKOS)
        self.graph.bind("foaf", FOAF)
        self.graph.bind("dc", DC)
        self.graph.bind("dcterms", DCTERMS)
    
    def detect_language(self, text: str) -> str:
        """Detect language of text using simple pattern matching"""
        if not text:
            return "en"  # Default to English
        
        text_lower = text.lower()
        words = text_lower.split()
        
        language_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = sum(1 for word in words if word in patterns)
            if score > 0:
                language_scores[lang] = score / len(words)
        
        if language_scores:
            return max(language_scores.items(), key=lambda x: x[1])[0]
        
        return "en"  # Default fallback
    
    def convert_limitgraph_edge_to_triple(self, 
                                        subject: str, 
                                        predicate: str, 
                                        object_value: str,
                                        confidence: float = 1.0,
                                        annotator_id: str = "system",
                                        rlhf_feedback: Optional[Dict[str, Any]] = None,
                                        source_text: str = "") -> LimitGraphTriple:
        """Convert a LIMIT-Graph edge to a structured triple"""
        
        # Detect language
        combined_text = f"{subject} {predicate} {object_value} {source_text}"
        detected_language = self.detect_language(combined_text)
        
        # Create provenance information
        provenance = {
            "extraction_method": "limitgraph_conversion",
            "source_system": "LIMIT-Graph",
            "conversion_timestamp": datetime.now().isoformat(),
            "source_text": source_text
        }
        
        return LimitGraphTriple(
            subject=subject,
            predicate=predicate,
            object=object_value,
            confidence=confidence,
            source_language=detected_language,
            annotator_id=annotator_id,
            timestamp=datetime.now(),
            rlhf_feedback=rlhf_feedback,
            provenance=provenance
        )
    
    def add_triple_to_graph(self, triple: LimitGraphTriple) -> str:
        """Add a LIMIT-Graph triple to the RDF graph with full provenance"""
        
        # Create URIs
        subject_uri = self.LGDATA[self._clean_uri_component(triple.subject)]
        predicate_uri = self.LGONT[self._clean_uri_component(triple.predicate)]
        
        # Handle object (could be URI or literal)
        if self._is_entity(triple.object):
            object_uri = self.LGDATA[self._clean_uri_component(triple.object)]
        else:
            # Create literal with language tag
            object_uri = Literal(triple.object, lang=triple.source_language)
        
        # Add main triple
        self.graph.add((subject_uri, predicate_uri, object_uri))
        
        # Create statement URI for provenance
        statement_id = str(uuid.uuid4())
        statement_uri = self.LGPROV[f"statement_{statement_id}"]
        
        # Add provenance information using named graphs approach
        self._add_provenance_triples(statement_uri, triple, subject_uri, predicate_uri, object_uri)
        
        # Add RLHF feedback if available
        if triple.rlhf_feedback:
            self._add_rlhf_triples(statement_uri, triple.rlhf_feedback)
        
        return statement_id
    
    def _add_provenance_triples(self, statement_uri: URIRef, triple: LimitGraphTriple,
                               subject_uri: URIRef, predicate_uri: URIRef, object_uri: Union[URIRef, Literal]):
        """Add provenance triples for a statement"""
        
        # Statement metadata
        self.graph.add((statement_uri, RDF.type, self.LGONT.Statement))
        self.graph.add((statement_uri, self.LGONT.hasSubject, subject_uri))
        self.graph.add((statement_uri, self.LGONT.hasPredicate, predicate_uri))
        self.graph.add((statement_uri, self.LGONT.hasObject, object_uri))
        
        # Confidence and quality metrics
        self.graph.add((statement_uri, self.LGONT.confidence, Literal(triple.confidence, datatype=XSD.float)))
        self.graph.add((statement_uri, self.LGONT.sourceLanguage, Literal(triple.source_language, datatype=XSD.string)))
        self.graph.add((statement_uri, self.LGONT.annotatorId, Literal(triple.annotator_id, datatype=XSD.string)))
        self.graph.add((statement_uri, self.LGONT.timestamp, Literal(triple.timestamp.isoformat(), datatype=XSD.dateTime)))
        
        # Provenance details
        if triple.provenance:
            for key, value in triple.provenance.items():
                prop_uri = self.LGPROV[self._clean_uri_component(key)]
                self.graph.add((statement_uri, prop_uri, Literal(str(value), datatype=XSD.string)))
    
    def _add_rlhf_triples(self, statement_uri: URIRef, rlhf_feedback: Dict[str, Any]):
        """Add RLHF feedback triples"""
        
        feedback_uri = self.LGRLHF[f"feedback_{uuid.uuid4()}"]
        self.graph.add((feedback_uri, RDF.type, self.LGONT.RLHFFeedback))
        self.graph.add((statement_uri, self.LGONT.hasRLHFFeedback, feedback_uri))
        
        # Add feedback details
        for key, value in rlhf_feedback.items():
            prop_uri = self.LGRLHF[self._clean_uri_component(key)]
            if isinstance(value, (int, float)):
                datatype = XSD.float if isinstance(value, float) else XSD.integer
                self.graph.add((feedback_uri, prop_uri, Literal(value, datatype=datatype)))
            else:
                self.graph.add((feedback_uri, prop_uri, Literal(str(value), datatype=XSD.string)))
    
    def _clean_uri_component(self, component: str) -> str:
        """Clean a string to be used as URI component"""
        # Replace spaces and special characters
        cleaned = component.replace(" ", "_").replace("-", "_")
        # Remove non-alphanumeric characters except underscores
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")
        return cleaned
    
    def _is_entity(self, value: str) -> bool:
        """Determine if a value should be treated as an entity (URI) or literal"""
        # Simple heuristic: if it looks like an entity name or ID
        if len(value) < 50 and not any(char in value for char in ['.', '!', '?', ',']):
            return True
        return False
    
    def convert_limitgraph_corpus(self, corpus_data: List[Dict[str, Any]], 
                                 annotator_id: str = "corpus_processor") -> RDFConversionResult:
        """Convert an entire LIMIT-Graph corpus to RDF"""
        
        languages_detected = set()
        annotators = set([annotator_id])
        triples_added = 0
        
        for doc in corpus_data:
            doc_id = doc.get('_id', f"doc_{uuid.uuid4()}")
            text = doc.get('text', '')
            
            if not text:
                continue
            
            # Detect language
            language = self.detect_language(text)
            languages_detected.add(language)
            
            # Create document entity
            doc_uri = self.LGDATA[f"document_{self._clean_uri_component(doc_id)}"]
            self.graph.add((doc_uri, RDF.type, self.LGONT.Document))
            self.graph.add((doc_uri, RDFS.label, Literal(f"Document {doc_id}", lang=language)))
            self.graph.add((doc_uri, self.LGONT.content, Literal(text, lang=language)))
            self.graph.add((doc_uri, self.LGONT.documentId, Literal(doc_id, datatype=XSD.string)))
            self.graph.add((doc_uri, self.LGONT.language, Literal(language, datatype=XSD.string)))
            
            # Extract simple triples from text (basic NLP)
            extracted_triples = self._extract_simple_triples(text, doc_id, language)
            
            for triple_data in extracted_triples:
                triple = self.convert_limitgraph_edge_to_triple(
                    subject=triple_data['subject'],
                    predicate=triple_data['predicate'],
                    object_value=triple_data['object'],
                    confidence=triple_data.get('confidence', 0.8),
                    annotator_id=annotator_id,
                    source_text=text
                )
                
                self.add_triple_to_graph(triple)
                triples_added += 1
        
        conversion_metadata = {
            "conversion_timestamp": datetime.now().isoformat(),
            "documents_processed": len(corpus_data),
            "triples_generated": triples_added,
            "languages_detected": list(languages_detected),
            "annotators": list(annotators)
        }
        
        return RDFConversionResult(
            graph=self.graph,
            triples_count=triples_added,
            languages_detected=list(languages_detected),
            annotators=list(annotators),
            conversion_metadata=conversion_metadata
        )
    
    def _extract_simple_triples(self, text: str, doc_id: str, language: str) -> List[Dict[str, Any]]:
        """Extract simple triples from text using basic patterns"""
        triples = []
        
        # Language-specific patterns
        if language == 'es':
            # Spanish patterns: "A X le gusta Y" -> (X, likes, Y)
            import re
            
            # Pattern: "A [person] le gusta [object]"
            pattern = r"A\s+(\w+)\s+le\s+gusta[n]?\s+(.+?)(?:\.|$)"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                person = match.group(1).strip()
                object_liked = match.group(2).strip()
                
                triples.append({
                    'subject': person,
                    'predicate': 'likes',
                    'object': object_liked,
                    'confidence': 0.9,
                    'source_doc': doc_id
                })
            
            # Pattern: "[person] es alérgica a [object]"
            pattern = r"(\w+)\s+es\s+alérgic[ao]\s+a\s+(.+?)(?:\.|$)"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                person = match.group(1).strip()
                allergen = match.group(2).strip()
                
                triples.append({
                    'subject': person,
                    'predicate': 'allergic_to',
                    'object': allergen,
                    'confidence': 0.9,
                    'source_doc': doc_id
                })
        
        elif language == 'en':
            # English patterns
            import re
            
            # Pattern: "[person] likes [object]"
            pattern = r"(\w+)\s+likes?\s+(.+?)(?:\.|$)"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                person = match.group(1).strip()
                object_liked = match.group(2).strip()
                
                triples.append({
                    'subject': person,
                    'predicate': 'likes',
                    'object': object_liked,
                    'confidence': 0.9,
                    'source_doc': doc_id
                })
        
        # Add document containment triples
        triples.append({
            'subject': f"document_{doc_id}",
            'predicate': 'contains_text',
            'object': text,
            'confidence': 1.0,
            'source_doc': doc_id
        })
        
        return triples
    
    def export_to_formats(self, output_dir: str = "output/rdf/"):
        """Export RDF graph to multiple formats"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        formats = {
            'turtle': 'ttl',
            'xml': 'rdf',
            'n3': 'n3',
            'json-ld': 'jsonld'
        }
        
        exported_files = {}
        
        for format_name, extension in formats.items():
            try:
                filename = f"limitgraph_triples.{extension}"
                filepath = os.path.join(output_dir, filename)
                
                self.graph.serialize(destination=filepath, format=format_name)
                exported_files[format_name] = filepath
                print(f"✅ Exported {format_name} to {filepath}")
                
            except Exception as e:
                print(f"❌ Failed to export {format_name}: {e}")
        
        return exported_files
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the RDF graph"""
        
        # Count triples by type
        statement_count = len(list(self.graph.subjects(RDF.type, self.LGONT.Statement)))
        document_count = len(list(self.graph.subjects(RDF.type, self.LGONT.Document)))
        
        # Count languages
        languages = set()
        for _, _, lang_literal in self.graph.triples((None, self.LGONT.language, None)):
            languages.add(str(lang_literal))
        
        # Count annotators
        annotators = set()
        for _, _, annotator_literal in self.graph.triples((None, self.LGONT.annotatorId, None)):
            annotators.add(str(annotator_literal))
        
        return {
            "total_triples": len(self.graph),
            "statements": statement_count,
            "documents": document_count,
            "languages": list(languages),
            "annotators": list(annotators),
            "namespaces": list(self.graph.namespaces())
        }

# Demo and testing functions
def demo_triple_generation():
    """Demonstrate triple generation capabilities"""
    
    print("🔗 LIMIT-Graph Triple Generation Demo")
    
    # Initialize generator
    generator = LimitGraphTripleGenerator()
    
    # Sample corpus data
    corpus_data = [
        {"_id": "d12", "text": "A Andrés le gustan las manzanas."},
        {"_id": "d27", "text": "Juana es alérgica a las manzanas pero le gustan mucho."},
        {"_id": "d1", "text": "Alice likes apples and oranges."},
        {"_id": "d2", "text": "Bob owns a red car."}
    ]
    
    # Convert corpus
    result = generator.convert_limitgraph_corpus(corpus_data, annotator_id="demo_annotator")
    
    print(f"\n📊 Conversion Results:")
    print(f"  - Triples generated: {result.triples_count}")
    print(f"  - Languages detected: {result.languages_detected}")
    print(f"  - Annotators: {result.annotators}")
    
    # Get statistics
    stats = generator.get_statistics()
    print(f"\n📈 Graph Statistics:")
    print(f"  - Total triples: {stats['total_triples']}")
    print(f"  - Documents: {stats['documents']}")
    print(f"  - Statements: {stats['statements']}")
    print(f"  - Languages: {stats['languages']}")
    
    # Export to formats
    exported_files = generator.export_to_formats()
    print(f"\n💾 Exported files: {list(exported_files.keys())}")
    
    return generator, result

if __name__ == "__main__":
    demo_triple_generation()