# LIMIT-Graph RDF Integration - Contributor Onboarding Guide

Welcome to the LIMIT-Graph RDF integration project! This guide will help you understand RDF, contribute to our multilingual knowledge graph, and validate your contributions.

## 🎯 What is RDF and Why It Matters

### Resource Description Framework (RDF) Basics

**RDF** is a standard for representing information about resources on the web. Think of it as a way to make statements about things using a simple **Subject-Predicate-Object** structure, like:

- **Subject**: "Andrés" (a person)
- **Predicate**: "likes" (a relationship)  
- **Object**: "apples" (what he likes)

This creates the statement: **"Andrés likes apples"**

### Why RDF Matters for LIMIT-Graph

1. **Multilingual Support**: RDF naturally handles multiple languages with language tags
2. **Semantic Interoperability**: Different systems can understand and share our data
3. **Cultural Sensitivity**: We can track cultural context and annotator identity
4. **Quality Assurance**: RLHF feedback is embedded directly in the knowledge graph
5. **Provenance Tracking**: Every statement includes who created it, when, and how

### Real-World Example

Instead of just storing text like:
```
"A Andrés le gustan las manzanas"
```

We create rich, queryable knowledge:
```turtle
# The main statement
:statement_001 a lgont:Statement ;
    lgont:hasSubject :Andrés ;
    lgont:hasPredicate lgont:likes ;
    lgont:hasObject :apples ;
    lgont:confidence 0.95 .

# Language annotation
:lang_annotation_001 a lgont:LanguageAnnotation ;
    lgont:annotatesStatement :statement_001 ;
    lgont:text "A Andrés le gustan las manzanas"@es ;
    lgont:languageCode "es" ;
    lgont:culturalContext "latin_american" .

# Annotator information
:annotator_maria a lgont:Annotator ;
    foaf:name "Dr. Maria Rodriguez" ;
    lgont:speaksLanguage :spanish, :english ;
    lgont:expertiseIn "spanish_nlp" .

# RLHF feedback
:feedback_001 a lgont:RLHFFeedback ;
    lgont:statementId "statement_001" ;
    lgont:qualityScore 0.92 ;
    lgont:culturalAppropriateness 0.98 ;
    lgont:providedBy :annotator_maria .
```

## 🚀 Getting Started

### Prerequisites

```bash
# Install required Python packages
pip install rdflib sparqlwrapper pandas

# Optional: Install additional RDF tools
pip install owlrl pyshacl
```

### Quick Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd hybrid-ai-research-agent/extensions/LIMIT-GRAPH/rdf/
```

2. **Run the demo**:
```bash
python triple_generator.py
```

3. **Explore the generated RDF files**:
```bash
ls output/rdf/
# You'll see: limitgraph_triples.ttl, limitgraph_triples.rdf, etc.
```

## 📊 How to Export LIMIT-Graph Triples

### Method 1: Using the Triple Generator

```python
from extensions.LIMIT_GRAPH.rdf.triple_generator import LimitGraphTripleGenerator

# Initialize generator
generator = LimitGraphTripleGenerator()

# Convert your corpus data
corpus_data = [
    {"_id": "d12", "text": "A Andrés le gustan las manzanas."},
    {"_id": "d27", "text": "Juana es alérgica a las manzanas pero le gustan mucho."}
]

# Generate RDF triples
result = generator.convert_limitgraph_corpus(corpus_data, annotator_id="your_name")

# Export to multiple formats
exported_files = generator.export_to_formats("output/rdf/")
print(f"Exported files: {exported_files}")
```

### Method 2: Using the Named Graphs Manager

```python
from extensions.LIMIT_GRAPH.rdf.named_graphs import LimitGraphNamedGraphManager
from extensions.LIMIT_GRAPH.rdf.named_graphs import AnnotatorProfile
from datetime import datetime

# Initialize manager
manager = LimitGraphNamedGraphManager()

# Register yourself as an annotator
your_profile = AnnotatorProfile(
    annotator_id="contributor_001",
    name="Your Name",
    expertise_domains=["nlp", "linguistics"],
    languages=["en", "es"],  # Languages you work with
    reliability_score=0.9,
    annotation_count=0,
    created_date=datetime.now()
)

manager.register_annotator(your_profile)

# Export all named graphs
exported_files = manager.export_named_graphs("output/rdf/named_graphs/")
```

### Method 3: Direct RDF Export

```python
from rdflib import Graph

# Load existing RDF data
g = Graph()
g.parse("output/rdf/limitgraph_triples.ttl", format="turtle")

# Add your own triples
from rdflib import URIRef, Literal, Namespace
LG = Namespace("http://limitgraph.org/data/")
LGONT = Namespace("http://limitgraph.org/ontology/")

# Add a new statement
g.add((LG.Bob, LGONT.likes, LG.oranges))
g.add((LG.Bob, LGONT.confidence, Literal(0.95)))

# Export in your preferred format
g.serialize("my_contributions.ttl", format="turtle")
g.serialize("my_contributions.rdf", format="xml")
g.serialize("my_contributions.jsonld", format="json-ld")
```

## ✅ How to Validate RDF with SHACL or OWL

### SHACL Validation (Recommended)

SHACL (Shapes Constraint Language) validates the structure and content of RDF data.

```python
import pyshacl
from rdflib import Graph

# Load your RDF data
data_graph = Graph()
data_graph.parse("output/rdf/limitgraph_triples.ttl", format="turtle")

# Load SHACL shapes (validation rules)
shapes_graph = Graph()
shapes_graph.parse("extensions/LIMIT-GRAPH/rdf/validation/limitgraph_shapes.ttl", format="turtle")

# Validate
conforms, results_graph, results_text = pyshacl.validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    debug=True
)

if conforms:
    print("✅ RDF data is valid!")
else:
    print("❌ Validation errors found:")
    print(results_text)
```

### OWL Validation

```python
import owlrl
from rdflib import Graph

# Load your RDF data and ontology
g = Graph()
g.parse("output/rdf/limitgraph_triples.ttl", format="turtle")
g.parse("output/rdf/ontologies/limitgraph_ontology.owl", format="xml")

# Apply OWL reasoning
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)

# Check for inconsistencies
# (This is a simplified check - real OWL validation is more complex)
print(f"Graph has {len(g)} triples after reasoning")
```

### Custom Validation Script

```python
def validate_limitgraph_rdf(rdf_file):
    """Custom validation for LIMIT-Graph RDF data"""
    
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF, RDFS
    
    g = Graph()
    g.parse(rdf_file, format="turtle")
    
    LGONT = Namespace("http://limitgraph.org/ontology/")
    
    errors = []
    warnings = []
    
    # Check 1: All statements have required properties
    for statement in g.subjects(RDF.type, LGONT.Statement):
        if not list(g.objects(statement, LGONT.hasSubject)):
            errors.append(f"Statement {statement} missing hasSubject")
        if not list(g.objects(statement, LGONT.hasPredicate)):
            errors.append(f"Statement {statement} missing hasPredicate")
        if not list(g.objects(statement, LGONT.hasObject)):
            errors.append(f"Statement {statement} missing hasObject")
    
    # Check 2: Confidence scores are in valid range
    for statement, confidence in g.subject_objects(LGONT.confidence):
        try:
            conf_value = float(confidence)
            if not (0.0 <= conf_value <= 1.0):
                errors.append(f"Invalid confidence score: {conf_value}")
        except ValueError:
            errors.append(f"Non-numeric confidence score: {confidence}")
    
    # Check 3: Language codes are valid
    valid_languages = ['en', 'es', 'ar', 'id', 'zh', 'hi', 'fr', 'de']
    for annotation, lang_code in g.subject_objects(LGONT.languageCode):
        if str(lang_code) not in valid_languages:
            warnings.append(f"Unusual language code: {lang_code}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'total_triples': len(g)
    }

# Use the validator
result = validate_limitgraph_rdf("output/rdf/limitgraph_triples.ttl")
if result['valid']:
    print("✅ RDF validation passed!")
else:
    print("❌ Validation failed:")
    for error in result['errors']:
        print(f"  - {error}")
```

## 🌍 How to Contribute Multilingual Ontology Terms

### Adding New Language Support

1. **Extend the language patterns** in `triple_generator.py`:

```python
# Add your language patterns
self.language_patterns = {
    'es': ['el', 'la', 'los', 'las', 'de', 'del', 'en', 'con'],
    'ar': ['في', 'من', 'إلى', 'على', 'مع', 'هو', 'هي'],
    'id': ['yang', 'dan', 'di', 'ke', 'dari', 'untuk'],
    'your_lang': ['word1', 'word2', 'word3']  # Add your language
}
```

2. **Add extraction patterns** for your language:

```python
def _extract_simple_triples(self, text: str, doc_id: str, language: str):
    if language == 'your_lang':
        # Add patterns for your language
        pattern = r"(\w+)\s+likes\s+(.+?)(?:\.|$)"  # Adapt to your language
        matches = re.finditer(pattern, text, re.IGNORECASE)
        # Process matches...
```

### Contributing Ontology Terms

1. **Add multilingual labels** to existing classes:

```python
from extensions.LIMIT_GRAPH.rdf.ontology_templates import LimitGraphOntologyBuilder

builder = LimitGraphOntologyBuilder()

# Add labels for your language
builder.add_multilingual_alignment(
    entity_uri=str(builder.LGONT.Person),
    same_as_uris=[],
    alt_labels={
        'your_lang': ['Person_in_your_language', 'Alternative_term'],
        'en': ['Human Being', 'Individual']
    }
)
```

2. **Create domain-specific ontologies**:

```python
# Example: Food domain in multiple languages
food_classes = [
    OntologyClass(
        class_uri=str(builder.LGONT.Food),
        labels={
            'en': 'Food',
            'es': 'Comida', 
            'ar': 'طعام',
            'id': 'Makanan',
            'your_lang': 'Food_in_your_language'
        },
        alt_labels={
            'en': ['Edible', 'Nourishment'],
            'your_lang': ['Alt1', 'Alt2']
        },
        description={
            'en': 'Edible substance that provides nutrition',
            'your_lang': 'Description in your language'
        },
        parent_classes=[str(builder.LGONT.Entity)],
        properties=['hasNutrient', 'hasCalories']
    )
]

builder.create_domain_specific_ontology("food", food_classes, [])
```

### Cultural Context Annotations

Add cultural context to your annotations:

```python
from extensions.LIMIT_GRAPH.rdf.named_graphs import LanguageAnnotation

# Create culturally-aware annotation
lang_annotation = LanguageAnnotation(
    text="Your text in your language",
    language_code="your_lang",
    confidence=0.95,
    detection_method="native_speaker",
    cultural_context="your_cultural_context",  # e.g., "southeast_asian", "middle_eastern"
    dialect_variant="your_dialect"  # e.g., "jakarta_indonesian", "egyptian_arabic"
)
```

## 🔧 Development Workflow

### 1. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks (if configured)
pre-commit install
```

### 2. Make Your Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-language-support`
3. **Make your changes** following the patterns above
4. **Add tests** for your contributions
5. **Validate your RDF** using the methods above

### 3. Testing Your Contributions

```bash
# Run unit tests
python -m pytest tests/rdf/ -v

# Run integration tests
python extensions/LIMIT-GRAPH/rdf/triple_generator.py
python extensions/LIMIT-GRAPH/rdf/named_graphs.py
python extensions/LIMIT-GRAPH/rdf/ontology_templates.py
python extensions/LIMIT-GRAPH/rdf/sparql_interface.py

# Validate RDF output
python -c "
from extensions.LIMIT_GRAPH.rdf.triple_generator import demo_triple_generation
demo_triple_generation()
"
```

### 4. Submit Your Contribution

1. **Commit your changes**: `git commit -m "Add support for [your language]"`
2. **Push to your fork**: `git push origin feature/your-language-support`
3. **Create a Pull Request** with:
   - Clear description of what you added
   - Examples of the new functionality
   - Test results showing validation passes

## 📚 Common Patterns and Examples

### Pattern 1: Adding a New Language

```python
# 1. Add language detection patterns
self.language_patterns['hi'] = ['है', 'का', 'की', 'के', 'में', 'से', 'को']

# 2. Add extraction patterns
if language == 'hi':
    # Hindi pattern: "[person] को [object] पसंद है"
    pattern = r"(\w+)\s+को\s+(.+?)\s+पसंद\s+है"
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

# 3. Add to supported languages
self.supported_languages['hi'] = {'name': 'Hindi', 'rtl': False, 'script': 'Devanagari'}
```

### Pattern 2: Adding Cultural Context

```python
# Detect cultural context based on language and content
def detect_cultural_context(self, text: str, language: str) -> str:
    cultural_indicators = {
        'es': {
            'latin_american': ['peso', 'dólar', 'mate', 'empanada'],
            'iberian': ['euro', 'paella', 'siesta', 'tapas']
        },
        'ar': {
            'gulf': ['درهم', 'ريال', 'خليج'],
            'levantine': ['ليرة', 'شام', 'بلاد']
        }
    }
    
    if language in cultural_indicators:
        for context, indicators in cultural_indicators[language].items():
            if any(indicator in text for indicator in indicators):
                return context
    
    return f"{language}_general"
```

### Pattern 3: Quality Assurance

```python
# Add quality checks for your contributions
def validate_language_annotation(annotation: LanguageAnnotation) -> List[str]:
    errors = []
    
    # Check confidence range
    if not (0.0 <= annotation.confidence <= 1.0):
        errors.append("Confidence must be between 0.0 and 1.0")
    
    # Check language code format
    if len(annotation.language_code) != 2:
        errors.append("Language code should be 2 characters (ISO 639-1)")
    
    # Check text-language consistency
    if annotation.language_code == 'ar' and not any('\u0600' <= c <= '\u06FF' for c in annotation.text):
        errors.append("Arabic language code but no Arabic script detected")
    
    return errors
```

## 🎯 Contribution Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to all public functions
- Include multilingual examples in docstrings

### RDF Best Practices
- Use meaningful URIs
- Include rdfs:label for all resources
- Add language tags to all literals
- Provide confidence scores for extracted data
- Include provenance information

### Testing Requirements
- Add unit tests for new language patterns
- Include integration tests for RDF generation
- Validate RDF output with SHACL/OWL
- Test with real multilingual data

### Documentation
- Update this guide with new language support
- Add examples for your contributions
- Include cultural context explanations
- Provide validation examples

## 🆘 Getting Help

### Common Issues

**Issue**: "Language not detected correctly"
```python
# Solution: Add more language patterns
self.language_patterns['your_lang'].extend(['new', 'patterns', 'here'])
```

**Issue**: "RDF validation fails"
```python
# Solution: Check required properties
# Every statement needs: hasSubject, hasPredicate, hasObject
```

**Issue**: "Cultural context not recognized"
```python
# Solution: Add cultural indicators
cultural_context = detect_cultural_context(text, language)
```

### Resources

- **RDF Tutorial**: https://www.w3.org/TR/rdf11-primer/
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **SHACL Specification**: https://www.w3.org/TR/shacl/
- **OWL Guide**: https://www.w3.org/TR/owl2-primer/

### Community

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute code and documentation

## 🏆 Recognition

Contributors will be:
- Listed in the project contributors
- Credited in academic publications
- Invited to present at conferences
- Given priority access to new features


Thank you for contributing to LIMIT-Graph RDF integration! Your work helps create a more inclusive and culturally-aware AI system. 🌍✨
