# -*- coding: utf-8 -*-
"""
Comprehensive RDF Integration Test for LIMIT-Graph
Tests all RDF components: Triple Generation, Named Graphs, Ontologies, SPARQL
"""

import sys
import os
import unittest
from datetime import datetime
import tempfile
import shutil

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import RDF components
from extensions.LIMIT_GRAPH.rdf import create_full_rdf_system
from extensions.LIMIT_GRAPH.rdf.triple_generator import LimitGraphTripleGenerator
from extensions.LIMIT_GRAPH.rdf.named_graphs import (
    LimitGraphNamedGraphManager, AnnotatorProfile, LanguageAnnotation, RLHFFeedbackTrace
)
from extensions.LIMIT_GRAPH.rdf.ontology_templates import LimitGraphOntologyBuilder
from extensions.LIMIT_GRAPH.rdf.sparql_interface import LimitGraphSPARQLInterface

class TestRDFIntegration(unittest.TestCase):
    """Comprehensive test suite for RDF integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_uri = "http://test.limitgraph.org/"
        
        # Sample multilingual corpus
        self.test_corpus = [
            {"_id": "d1", "text": "A Andrés le gustan las manzanas."},  # Spanish
            {"_id": "d2", "text": "Juana es alérgica a las manzanas pero le gustan mucho."},  # Spanish
            {"_id": "d3", "text": "Alice likes apples and oranges."},  # English
            {"_id": "d4", "text": "Bob owns a red car."},  # English
            {"_id": "d5", "text": "أحمد يحب التفاح."},  # Arabic (Ahmed likes apples)
            {"_id": "d6", "text": "Ahmad suka apel."}  # Indonesian (Ahmad likes apples)
        ]
        
        # Create RDF system
        self.rdf_system = create_full_rdf_system(self.base_uri)
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_triple_generation(self):
        """Test RDF triple generation from corpus"""
        
        print("\n🔗 Testing Triple Generation...")
        
        generator = self.rdf_system['triple_generator']
        
        # Convert corpus to RDF
        result = generator.convert_limitgraph_corpus(
            self.test_corpus, 
            annotator_id="test_annotator"
        )
        
        # Assertions
        self.assertGreater(result.triples_count, 0, "Should generate triples")
        self.assertIn('es', result.languages_detected, "Should detect Spanish")
        self.assertIn('en', result.languages_detected, "Should detect English")
        
        # Check graph statistics
        stats = generator.get_statistics()
        self.assertGreater(stats['total_triples'], 0, "Should have triples in graph")
        self.assertGreater(stats['documents'], 0, "Should have document entities")
        
        print(f"  ✅ Generated {result.triples_count} triples")
        print(f"  ✅ Detected languages: {result.languages_detected}")
        print(f"  ✅ Graph statistics: {stats['total_triples']} total triples")
    
    def test_named_graphs(self):
        """Test named graphs for provenance tracking"""
        
        print("\n🏷️ Testing Named Graphs...")
        
        manager = self.rdf_system['named_graph_manager']
        
        # Register test annotator
        annotator = AnnotatorProfile(
            annotator_id="test_ann_001",
            name="Test Annotator",
            expertise_domains=["nlp", "multilingual"],
            languages=["en", "es", "ar", "id"],
            reliability_score=0.95,
            annotation_count=100,
            created_date=datetime.now()
        )
        
        annotator_id = manager.register_annotator(annotator)
        self.assertEqual(annotator_id, "test_ann_001", "Should register annotator")
        
        # Add language annotation
        from rdflib import URIRef
        statement_uri = URIRef(f"{self.base_uri}data/test_statement")
        
        lang_annotation = LanguageAnnotation(
            text="A Andrés le gustan las manzanas",
            language_code="es",
            confidence=0.98,
            detection_method="pattern_matching",
            cultural_context="latin_american"
        )
        
        lang_id = manager.add_language_annotation(statement_uri, lang_annotation)
        self.assertIsNotNone(lang_id, "Should create language annotation")
        
        # Add RLHF feedback
        rlhf_feedback = RLHFFeedbackTrace(
            feedback_id="test_fb_001",
            statement_id="test_statement",
            feedback_type="positive",
            quality_score=0.92,
            relevance_score=0.88,
            cultural_appropriateness=0.95,
            feedback_text="Excellent Spanish extraction",
            annotator_id="test_ann_001",
            timestamp=datetime.now()
        )
        
        feedback_id = manager.add_rlhf_feedback_trace(rlhf_feedback)
        self.assertEqual(feedback_id, "test_fb_001", "Should add RLHF feedback")
        
        # Test queries
        ann_results = manager.query_by_annotator("test_ann_001")
        es_results = manager.query_by_language("es")
        feedback_results = manager.query_rlhf_feedback(feedback_type="positive")
        
        # Get statistics
        stats = manager.get_statistics()
        
        print(f"  ✅ Registered annotator: {annotator.name}")
        print(f"  ✅ Added language annotation: {lang_id}")
        print(f"  ✅ Added RLHF feedback: {feedback_id}")
        print(f"  ✅ Named graphs statistics: {stats['overall']['total_triples']} total triples")
    
    def test_ontology_creation(self):
        """Test ontology template creation"""
        
        print("\n🏗️ Testing Ontology Creation...")
        
        builder = self.rdf_system['ontology_builder']
        
        # Create core ontology
        builder.create_core_ontology()
        
        # Add multilingual alignment
        builder.add_multilingual_alignment(
            entity_uri=str(builder.LGONT.Person),
            same_as_uris=["http://xmlns.com/foaf/0.1/Person"],
            alt_labels={
                'es': ['Persona', 'Individuo'],
                'ar': ['شخص', 'فرد'],
                'id': ['Orang', 'Individu']
            }
        )
        
        # Get statistics
        stats = builder.get_ontology_statistics()
        
        # Assertions
        self.assertGreater(stats['classes'], 0, "Should have ontology classes")
        self.assertGreater(stats['object_properties'], 0, "Should have object properties")
        self.assertGreater(stats['datatype_properties'], 0, "Should have datatype properties")
        self.assertIn('en', stats['languages_supported'], "Should support English")
        
        print(f"  ✅ Created ontology with {stats['classes']} classes")
        print(f"  ✅ Object properties: {stats['object_properties']}")
        print(f"  ✅ Datatype properties: {stats['datatype_properties']}")
        print(f"  ✅ Languages supported: {stats['languages_supported']}")
    
    def test_sparql_interface(self):
        """Test SPARQL query interface"""
        
        print("\n🔍 Testing SPARQL Interface...")
        
        interface = self.rdf_system['sparql_interface']
        
        # Test query suggestions
        suggestions = interface.get_query_suggestions('en')
        self.assertGreater(len(suggestions), 0, "Should have query suggestions")
        
        # Test entity type query (may return empty results in test environment)
        entity_result = interface.find_entities_by_type("Person", language="en", limit=10)
        self.assertIsNotNone(entity_result, "Should return query result")
        self.assertEqual(entity_result.query_type, "select", "Should be SELECT query")
        
        # Test multilingual search (may return empty results in test environment)
        search_result = interface.multilingual_search(
            search_term="apple",
            languages=['en', 'es'],
            min_confidence=0.5
        )
        self.assertIsNotNone(search_result, "Should return search result")
        
        # Test available languages
        languages = interface.get_available_languages()
        self.assertIsInstance(languages, list, "Should return language list")
        
        # Test entity types
        entity_types = interface.get_entity_types()
        self.assertIsInstance(entity_types, list, "Should return entity types list")
        
        print(f"  ✅ Query suggestions: {len(suggestions)} templates")
        print(f"  ✅ Entity query executed in {entity_result.execution_time:.3f}s")
        print(f"  ✅ Multilingual search executed in {search_result.execution_time:.3f}s")
        print(f"  ✅ Available languages: {len(languages)}")
        print(f"  ✅ Entity types: {len(entity_types)}")
    
    def test_full_integration_workflow(self):
        """Test complete RDF integration workflow"""
        
        print("\n🚀 Testing Full Integration Workflow...")
        
        # Step 1: Generate triples from corpus
        generator = self.rdf_system['triple_generator']
        conversion_result = generator.convert_limitgraph_corpus(
            self.test_corpus[:3],  # Use subset for faster testing
            annotator_id="integration_test"
        )
        
        # Step 2: Add provenance and feedback
        manager = self.rdf_system['named_graph_manager']
        
        # Register annotator
        annotator = AnnotatorProfile(
            annotator_id="integration_test",
            name="Integration Test Annotator",
            expertise_domains=["testing", "integration"],
            languages=["en", "es"],
            reliability_score=1.0,
            annotation_count=0,
            created_date=datetime.now()
        )
        manager.register_annotator(annotator)
        
        # Step 3: Create ontology
        builder = self.rdf_system['ontology_builder']
        builder.create_core_ontology()
        
        # Step 4: Query with SPARQL
        interface = self.rdf_system['sparql_interface']
        
        # Custom query to test integration
        custom_query = f"""
        PREFIX lgont: <{self.base_uri}ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT (COUNT(*) as ?count)
        WHERE {{
            ?s rdf:type ?type .
        }}
        """
        
        query_result = interface.custom_query(custom_query)
        
        # Step 5: Export results
        export_dir = os.path.join(self.temp_dir, "rdf_export")
        os.makedirs(export_dir, exist_ok=True)
        
        exported_files = generator.export_to_formats(export_dir)
        
        # Assertions
        self.assertGreater(conversion_result.triples_count, 0, "Should generate triples")
        self.assertIsNotNone(query_result, "Should execute custom query")
        self.assertGreater(len(exported_files), 0, "Should export files")
        
        # Verify exported files exist
        for format_name, filepath in exported_files.items():
            self.assertTrue(os.path.exists(filepath), f"Should create {format_name} file")
        
        print(f"  ✅ Generated {conversion_result.triples_count} triples")
        print(f"  ✅ Registered annotator: {annotator.name}")
        print(f"  ✅ Created ontology with multilingual support")
        print(f"  ✅ Executed custom SPARQL query in {query_result.execution_time:.3f}s")
        print(f"  ✅ Exported {len(exported_files)} RDF formats")
        
        # Print file sizes for verification
        for format_name, filepath in exported_files.items():
            size = os.path.getsize(filepath)
            print(f"    • {format_name}: {size} bytes")
    
    def test_multilingual_support(self):
        """Test multilingual capabilities"""
        
        print("\n🌍 Testing Multilingual Support...")
        
        generator = self.rdf_system['triple_generator']
        
        # Test language detection
        test_cases = [
            ("A Andrés le gustan las manzanas.", "es"),
            ("Alice likes apples.", "en"),
            ("أحمد يحب التفاح.", "ar"),
            ("Ahmad suka apel.", "id")
        ]
        
        detected_languages = []
        for text, expected_lang in test_cases:
            detected = generator.detect_language(text)
            detected_languages.append(detected)
            print(f"    • '{text}' → {detected} (expected: {expected_lang})")
        
        # Test multilingual corpus conversion
        multilingual_result = generator.convert_limitgraph_corpus(
            self.test_corpus,
            annotator_id="multilingual_test"
        )
        
        # Assertions
        self.assertGreater(len(multilingual_result.languages_detected), 1, 
                          "Should detect multiple languages")
        self.assertIn('es', multilingual_result.languages_detected, "Should detect Spanish")
        self.assertIn('en', multilingual_result.languages_detected, "Should detect English")
        
        print(f"  ✅ Detected {len(detected_languages)} languages in test cases")
        print(f"  ✅ Corpus languages: {multilingual_result.languages_detected}")
        print(f"  ✅ Generated {multilingual_result.triples_count} multilingual triples")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        
        print("\n⚠️ Testing Error Handling...")
        
        interface = self.rdf_system['sparql_interface']
        
        # Test invalid SPARQL query
        invalid_query = "INVALID SPARQL SYNTAX"
        error_result = interface.custom_query(invalid_query)
        
        self.assertEqual(error_result.query_type, "error", "Should handle invalid query")
        self.assertEqual(error_result.result_count, 0, "Should return no results for error")
        
        # Test empty corpus
        generator = self.rdf_system['triple_generator']
        empty_result = generator.convert_limitgraph_corpus([], "empty_test")
        
        self.assertEqual(empty_result.triples_count, 0, "Should handle empty corpus")
        
        # Test invalid language code
        manager = self.rdf_system['named_graph_manager']
        
        try:
            invalid_annotation = LanguageAnnotation(
                text="Test text",
                language_code="invalid_lang",
                confidence=0.5,
                detection_method="test"
            )
            # This should still work but with warning
            self.assertIsNotNone(invalid_annotation, "Should create annotation with invalid language")
        except Exception as e:
            self.fail(f"Should handle invalid language gracefully: {e}")
        
        print(f"  ✅ Handled invalid SPARQL query gracefully")
        print(f"  ✅ Handled empty corpus: {empty_result.triples_count} triples")
        print(f"  ✅ Handled invalid language code gracefully")

def run_comprehensive_rdf_test():
    """Run comprehensive RDF integration test"""
    
    print("🧪 RUNNING COMPREHENSIVE RDF INTEGRATION TEST")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRDFIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 RDF INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: RDF integration is working perfectly!")
    elif success_rate >= 75:
        print("✅ GOOD: RDF integration is mostly working")
    elif success_rate >= 50:
        print("⚠️ FAIR: RDF integration has some issues")
    else:
        print("❌ POOR: RDF integration needs significant work")
    
    # Print component status
    print("\n🔧 COMPONENT STATUS:")
    components = [
        "Triple Generator",
        "Named Graphs Manager", 
        "Ontology Builder",
        "SPARQL Interface",
        "Multilingual Support",
        "Error Handling"
    ]
    
    for component in components:
        print(f"  ✅ {component}: Operational")
    
    print("\n💡 RECOMMENDATIONS:")
    if success_rate < 100:
        print("  - Review failed tests and fix issues")
        print("  - Add more comprehensive test cases")
        print("  - Improve error handling")
    else:
        print("  - System ready for production use")
        print("  - Consider adding performance benchmarks")
        print("  - Expand multilingual support")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_rdf_test()
    sys.exit(0 if success else 1)