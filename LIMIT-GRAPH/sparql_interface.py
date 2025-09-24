# -*- coding: utf-8 -*-
"""
SPARQL-Compatible Views for LIMIT-Graph RDF Integration
Offers a simple query interface for semantic search across multilingual corpora
Supports Indonesian, Spanish, Arabic, and other languages
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json
import re

# RDF libraries
from rdflib import Graph, URIRef, Literal, Namespace, Dataset
from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD, FOAF, DC, DCTERMS
from rdflib.plugins.sparql import prepareQuery

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

@dataclass
class SPARQLQueryResult:
    """Result of a SPARQL query execution"""
    query: str
    results: List[Dict[str, Any]]
    execution_time: float
    result_count: int
    languages_found: List[str]
    query_type: str

@dataclass
class QueryTemplate:
    """Template for common SPARQL queries"""
    name: str
    description: Dict[str, str]  # language -> description
    template: str
    parameters: List[str]
    example_values: Dict[str, Any]

class LimitGraphSPARQLInterface:
    """
    SPARQL interface for querying LIMIT-Graph RDF data
    Provides simple query methods for multilingual semantic search
    """
    
    def __init__(self, dataset: Dataset, base_uri: str = "http://limitgraph.org/"):
        """Initialize the SPARQL interface"""
        self.dataset = dataset
        self.base_uri = base_uri
        
        # Define namespaces
        self.LG = Namespace(base_uri)
        self.LGONT = Namespace(f"{base_uri}ontology/")
        self.LGDATA = Namespace(f"{base_uri}data/")
        self.LGPROV = Namespace(f"{base_uri}provenance/")
        self.LGRLHF = Namespace(f"{base_uri}rlhf/")
        self.LGANG = Namespace(f"{base_uri}annotators/")
        self.LGLANG = Namespace(f"{base_uri}languages/")
        
        # Language support
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'ar': 'Arabic',
            'id': 'Indonesian',
            'zh': 'Chinese',
            'hi': 'Hindi',
            'fr': 'French',
            'de': 'German'
        }
        
        # Query templates
        self.query_templates = {}
        self._initialize_query_templates()
        
        print("🔍 LIMIT-Graph SPARQL Interface initialized")
    
    def _initialize_query_templates(self):
        """Initialize common query templates"""
        
        # Template 1: Find entities by type
        self.query_templates['entities_by_type'] = QueryTemplate(
            name='entities_by_type',
            description={
                'en': 'Find all entities of a specific type',
                'es': 'Encontrar todas las entidades de un tipo específico',
                'ar': 'العثور على جميع الكيانات من نوع معين',
                'id': 'Temukan semua entitas dengan jenis tertentu'
            },
            template="""
            PREFIX lgont: <{lgont}>
            PREFIX lgdata: <{lgdata}>
            PREFIX rdfs: <{rdfs}>
            
            SELECT ?entity ?label ?type
            WHERE {{
                ?entity rdf:type ?type .
                ?entity rdfs:label ?label .
                FILTER(?type = lgont:{entity_type})
                {language_filter}
            }}
            ORDER BY ?label
            """,
            parameters=['entity_type', 'language'],
            example_values={'entity_type': 'Person', 'language': 'en'}
        )
        
        # Template 2: Find relationships
        self.query_templates['relationships'] = QueryTemplate(
            name='relationships',
            description={
                'en': 'Find relationships between entities',
                'es': 'Encontrar relaciones entre entidades',
                'ar': 'العثور على العلاقات بين الكيانات',
                'id': 'Temukan hubungan antar entitas'
            },
            template="""
            PREFIX lgont: <{lgont}>
            PREFIX lgdata: <{lgdata}>
            PREFIX rdfs: <{rdfs}>
            
            SELECT ?subject ?predicate ?object ?subjectLabel ?objectLabel
            WHERE {{
                ?statement lgont:hasSubject ?subject .
                ?statement lgont:hasPredicate ?predicate .
                ?statement lgont:hasObject ?object .
                ?subject rdfs:label ?subjectLabel .
                ?object rdfs:label ?objectLabel .
                {subject_filter}
                {predicate_filter}
                {language_filter}
            }}
            ORDER BY ?subjectLabel
            """,
            parameters=['subject', 'predicate', 'language'],
            example_values={'subject': 'Andrés', 'predicate': 'likes', 'language': 'es'}
        )
        
        # Template 3: Multilingual search
        self.query_templates['multilingual_search'] = QueryTemplate(
            name='multilingual_search',
            description={
                'en': 'Search across multiple languages',
                'es': 'Buscar en múltiples idiomas',
                'ar': 'البحث عبر لغات متعددة',
                'id': 'Cari di berbagai bahasa'
            },
            template="""
            PREFIX lgont: <{lgont}>
            PREFIX lglang: <{lglang}>
            PREFIX rdfs: <{rdfs}>
            
            SELECT ?entity ?label ?language ?text ?confidence
            WHERE {{
                ?langAnnotation lgont:annotatesStatement ?statement .
                ?langAnnotation lgont:text ?text .
                ?langAnnotation lgont:languageCode ?language .
                ?langAnnotation lgont:confidence ?confidence .
                ?statement lgont:hasSubject ?entity .
                ?entity rdfs:label ?label .
                FILTER(CONTAINS(LCASE(?text), LCASE("{search_term}")))
                {language_filter}
            }}
            ORDER BY DESC(?confidence)
            """,
            parameters=['search_term', 'language'],
            example_values={'search_term': 'manzanas', 'language': 'es'}
        )
        
        # Template 4: RLHF feedback analysis
        self.query_templates['rlhf_analysis'] = QueryTemplate(
            name='rlhf_analysis',
            description={
                'en': 'Analyze RLHF feedback patterns',
                'es': 'Analizar patrones de retroalimentación RLHF',
                'ar': 'تحليل أنماط التغذية الراجعة RLHF',
                'id': 'Analisis pola umpan balik RLHF'
            },
            template="""
            PREFIX lgont: <{lgont}>
            PREFIX lgrlhf: <{lgrlhf}>
            PREFIX dcterms: <{dcterms}>
            
            SELECT ?feedback ?statementId ?feedbackType ?qualityScore 
                   ?relevanceScore ?culturalScore ?annotator ?timestamp
            WHERE {{
                ?feedback lgont:statementId ?statementId .
                ?feedback lgont:feedbackType ?feedbackType .
                ?feedback lgont:qualityScore ?qualityScore .
                ?feedback lgont:relevanceScore ?relevanceScore .
                ?feedback lgont:culturalAppropriateness ?culturalScore .
                ?feedback lgont:providedBy ?annotator .
                ?feedback dcterms:created ?timestamp .
                {feedback_type_filter}
                {quality_filter}
            }}
            ORDER BY DESC(?qualityScore)
            """,
            parameters=['feedback_type', 'min_quality'],
            example_values={'feedback_type': 'positive', 'min_quality': 0.8}
        )
        
        # Template 5: Cross-cultural analysis
        self.query_templates['cross_cultural'] = QueryTemplate(
            name='cross_cultural',
            description={
                'en': 'Compare concepts across cultures and languages',
                'es': 'Comparar conceptos entre culturas e idiomas',
                'ar': 'مقارنة المفاهيم عبر الثقافات واللغات',
                'id': 'Bandingkan konsep lintas budaya dan bahasa'
            },
            template="""
            PREFIX lgont: <{lgont}>
            PREFIX lglang: <{lglang}>
            PREFIX skos: <{skos}>
            PREFIX rdfs: <{rdfs}>
            
            SELECT ?concept ?label ?altLabel ?language ?culturalContext
            WHERE {{
                ?concept rdfs:label ?label .
                ?concept skos:altLabel ?altLabel .
                ?langAnnotation lgont:annotatesStatement ?statement .
                ?statement lgont:hasSubject ?concept .
                ?langAnnotation lgont:languageCode ?language .
                ?langAnnotation lgont:culturalContext ?culturalContext .
                FILTER(CONTAINS(LCASE(?label), LCASE("{concept_term}")) || 
                       CONTAINS(LCASE(?altLabel), LCASE("{concept_term}")))
                {language_filter}
            }}
            ORDER BY ?language ?culturalContext
            """,
            parameters=['concept_term', 'language'],
            example_values={'concept_term': 'apple', 'language': 'all'}
        )
    
    def execute_query(self, query: str, timeout: int = 30) -> SPARQLQueryResult:
        """Execute a SPARQL query and return results"""
        
        start_time = datetime.now()
        
        try:
            # Execute query
            results = list(self.dataset.query(query))
            
            # Process results
            processed_results = []
            languages_found = set()
            
            for row in results:
                result_dict = {}
                for var in row.labels:
                    value = row[var]
                    if isinstance(value, Literal):
                        result_dict[var] = str(value)
                        if hasattr(value, 'language') and value.language:
                            languages_found.add(value.language)
                    else:
                        result_dict[var] = str(value)
                
                processed_results.append(result_dict)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine query type
            query_type = self._determine_query_type(query)
            
            return SPARQLQueryResult(
                query=query,
                results=processed_results,
                execution_time=execution_time,
                result_count=len(processed_results),
                languages_found=list(languages_found),
                query_type=query_type
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return SPARQLQueryResult(
                query=query,
                results=[{'error': str(e)}],
                execution_time=execution_time,
                result_count=0,
                languages_found=[],
                query_type='error'
            )
    
    def find_entities_by_type(self, entity_type: str, language: Optional[str] = None, 
                             limit: int = 50) -> SPARQLQueryResult:
        """Find entities of a specific type"""
        
        template = self.query_templates['entities_by_type']
        
        # Build language filter
        language_filter = ""
        if language and language != 'all':
            language_filter = f'FILTER(LANG(?label) = "{language}")'
        
        # Format query
        query = template.template.format(
            lgont=self.LGONT,
            lgdata=self.LGDATA,
            rdfs=RDFS,
            entity_type=entity_type,
            language_filter=language_filter
        )
        
        # Add limit
        query += f"\nLIMIT {limit}"
        
        return self.execute_query(query)
    
    def find_relationships(self, subject: Optional[str] = None, 
                          predicate: Optional[str] = None,
                          language: Optional[str] = None,
                          limit: int = 50) -> SPARQLQueryResult:
        """Find relationships between entities"""
        
        template = self.query_templates['relationships']
        
        # Build filters
        subject_filter = ""
        if subject:
            subject_filter = f'FILTER(CONTAINS(LCASE(?subjectLabel), LCASE("{subject}")))'
        
        predicate_filter = ""
        if predicate:
            predicate_filter = f'FILTER(CONTAINS(STR(?predicate), "{predicate}"))'
        
        language_filter = ""
        if language and language != 'all':
            language_filter = f'FILTER(LANG(?subjectLabel) = "{language}" || LANG(?objectLabel) = "{language}")'
        
        # Format query
        query = template.template.format(
            lgont=self.LGONT,
            lgdata=self.LGDATA,
            rdfs=RDFS,
            subject_filter=subject_filter,
            predicate_filter=predicate_filter,
            language_filter=language_filter
        )
        
        # Add limit
        query += f"\nLIMIT {limit}"
        
        return self.execute_query(query)
    
    def multilingual_search(self, search_term: str, 
                           languages: Optional[List[str]] = None,
                           min_confidence: float = 0.5,
                           limit: int = 50) -> SPARQLQueryResult:
        """Search across multiple languages"""
        
        template = self.query_templates['multilingual_search']
        
        # Build language filter
        language_filter = ""
        if languages and 'all' not in languages:
            lang_conditions = [f'?language = "{lang}"' for lang in languages]
            language_filter = f'FILTER({" || ".join(lang_conditions)})'
        
        # Add confidence filter
        if language_filter:
            language_filter += f' FILTER(?confidence >= {min_confidence})'
        else:
            language_filter = f'FILTER(?confidence >= {min_confidence})'
        
        # Format query
        query = template.template.format(
            lgont=self.LGONT,
            lglang=self.LGLANG,
            rdfs=RDFS,
            search_term=search_term,
            language_filter=language_filter
        )
        
        # Add limit
        query += f"\nLIMIT {limit}"
        
        return self.execute_query(query)
    
    def analyze_rlhf_feedback(self, feedback_type: Optional[str] = None,
                             min_quality: float = 0.0,
                             limit: int = 100) -> SPARQLQueryResult:
        """Analyze RLHF feedback patterns"""
        
        template = self.query_templates['rlhf_analysis']
        
        # Build filters
        feedback_type_filter = ""
        if feedback_type:
            feedback_type_filter = f'FILTER(?feedbackType = "{feedback_type}")'
        
        quality_filter = ""
        if min_quality > 0:
            quality_filter = f'FILTER(?qualityScore >= {min_quality})'
        
        # Format query
        query = template.template.format(
            lgont=self.LGONT,
            lgrlhf=self.LGRLHF,
            dcterms=DCTERMS,
            feedback_type_filter=feedback_type_filter,
            quality_filter=quality_filter
        )
        
        # Add limit
        query += f"\nLIMIT {limit}"
        
        return self.execute_query(query)
    
    def cross_cultural_analysis(self, concept_term: str,
                               languages: Optional[List[str]] = None,
                               limit: int = 50) -> SPARQLQueryResult:
        """Compare concepts across cultures and languages"""
        
        template = self.query_templates['cross_cultural']
        
        # Build language filter
        language_filter = ""
        if languages and 'all' not in languages:
            lang_conditions = [f'?language = "{lang}"' for lang in languages]
            language_filter = f'FILTER({" || ".join(lang_conditions)})'
        
        # Format query
        query = template.template.format(
            lgont=self.LGONT,
            lglang=self.LGLANG,
            skos=SKOS,
            rdfs=RDFS,
            concept_term=concept_term,
            language_filter=language_filter
        )
        
        # Add limit
        query += f"\nLIMIT {limit}"
        
        return self.execute_query(query)
    
    def custom_query(self, query: str) -> SPARQLQueryResult:
        """Execute a custom SPARQL query"""
        return self.execute_query(query)
    
    def get_query_suggestions(self, language: str = 'en') -> List[Dict[str, Any]]:
        """Get query suggestions based on available templates"""
        
        suggestions = []
        
        for template_name, template in self.query_templates.items():
            suggestion = {
                'name': template_name,
                'description': template.description.get(language, template.description.get('en', '')),
                'parameters': template.parameters,
                'example_values': template.example_values
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def get_available_languages(self) -> List[Dict[str, Any]]:
        """Get list of available languages in the dataset"""
        
        query = f"""
        PREFIX lglang: <{self.LGLANG}>
        PREFIX lgont: <{self.LGONT}>
        
        SELECT DISTINCT ?language ?languageName (COUNT(?annotation) as ?count)
        WHERE {{
            ?annotation lgont:languageCode ?language .
            OPTIONAL {{
                ?langEntity lgont:languageCode ?language .
                ?langEntity rdfs:label ?languageName .
            }}
        }}
        GROUP BY ?language ?languageName
        ORDER BY DESC(?count)
        """
        
        result = self.execute_query(query)
        
        languages = []
        for row in result.results:
            lang_code = row.get('language', '')
            lang_name = row.get('languageName', self.supported_languages.get(lang_code, lang_code))
            count = int(row.get('count', 0))
            
            languages.append({
                'code': lang_code,
                'name': lang_name,
                'annotation_count': count
            })
        
        return languages
    
    def get_entity_types(self) -> List[Dict[str, Any]]:
        """Get list of available entity types"""
        
        query = f"""
        PREFIX lgont: <{self.LGONT}>
        PREFIX rdfs: <{RDFS}>
        
        SELECT DISTINCT ?type ?typeLabel (COUNT(?entity) as ?count)
        WHERE {{
            ?entity rdf:type ?type .
            ?type rdfs:label ?typeLabel .
            FILTER(STRSTARTS(STR(?type), STR(lgont:)))
        }}
        GROUP BY ?type ?typeLabel
        ORDER BY DESC(?count)
        """
        
        result = self.execute_query(query)
        
        entity_types = []
        for row in result.results:
            entity_type = row.get('type', '')
            type_label = row.get('typeLabel', '')
            count = int(row.get('count', 0))
            
            # Extract simple name from URI
            simple_name = entity_type.split('/')[-1] if '/' in entity_type else entity_type
            
            entity_types.append({
                'uri': entity_type,
                'name': simple_name,
                'label': type_label,
                'count': count
            })
        
        return entity_types
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of SPARQL query"""
        
        query_lower = query.lower()
        
        if 'select' in query_lower:
            return 'select'
        elif 'construct' in query_lower:
            return 'construct'
        elif 'ask' in query_lower:
            return 'ask'
        elif 'describe' in query_lower:
            return 'describe'
        else:
            return 'unknown'
    
    def export_query_results(self, result: SPARQLQueryResult, 
                            output_format: str = 'json',
                            output_file: Optional[str] = None) -> str:
        """Export query results to file"""
        
        if output_format == 'json':
            data = {
                'query': result.query,
                'execution_time': result.execution_time,
                'result_count': result.result_count,
                'languages_found': result.languages_found,
                'query_type': result.query_type,
                'results': result.results
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return output_file
            else:
                return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif output_format == 'csv':
            import csv
            import io
            
            if not result.results:
                return ""
            
            output = io.StringIO()
            fieldnames = result.results[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result.results)
            
            csv_content = output.getvalue()
            output.close()
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                return output_file
            else:
                return csv_content
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

# Demo and testing functions
def demo_sparql_interface():
    """Demonstrate SPARQL interface capabilities"""
    
    print("🔍 LIMIT-Graph SPARQL Interface Demo")
    
    # This would typically use a real dataset
    # For demo, we'll create a mock dataset
    from extensions.LIMIT_GRAPH.rdf.named_graphs import LimitGraphNamedGraphManager
    
    # Create mock dataset
    manager = LimitGraphNamedGraphManager()
    
    # Initialize interface
    interface = LimitGraphSPARQLInterface(manager.dataset)
    
    # Demo queries
    print(f"\n📋 Available Query Templates:")
    suggestions = interface.get_query_suggestions('en')
    for suggestion in suggestions:
        print(f"  - {suggestion['name']}: {suggestion['description']}")
    
    # Demo multilingual search
    print(f"\n🔍 Multilingual Search Demo:")
    search_result = interface.multilingual_search(
        search_term="manzanas",
        languages=['es', 'en'],
        min_confidence=0.5
    )
    
    print(f"  - Query executed in {search_result.execution_time:.3f}s")
    print(f"  - Found {search_result.result_count} results")
    print(f"  - Languages: {search_result.languages_found}")
    
    # Demo entity type search
    print(f"\n👥 Entity Types Demo:")
    entity_types = interface.get_entity_types()
    print(f"  - Available entity types: {len(entity_types)}")
    for entity_type in entity_types[:3]:  # Show first 3
        print(f"    • {entity_type['name']}: {entity_type['count']} instances")
    
    # Demo language availability
    print(f"\n🌍 Available Languages:")
    languages = interface.get_available_languages()
    for lang in languages:
        print(f"  - {lang['name']} ({lang['code']}): {lang['annotation_count']} annotations")
    
    return interface

if __name__ == "__main__":
    demo_sparql_interface()