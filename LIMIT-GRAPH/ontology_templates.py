# -*- coding: utf-8 -*-
"""
Ontology Templates for LIMIT-Graph RDF Integration
Scaffolds lightweight OWL ontologies for Agent, Entity, Relation, Language, Annotation
Uses rdfs:label, owl:sameAs and skos:altLabel for multilingual alignment
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json

# RDF libraries
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD, FOAF, DC, DCTERMS

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

@dataclass
class OntologyClass:
    """Represents an ontology class with multilingual labels"""
    class_uri: str
    labels: Dict[str, str]  # language -> label
    alt_labels: Dict[str, List[str]]  # language -> alternative labels
    description: Dict[str, str]  # language -> description
    parent_classes: List[str]
    properties: List[str]

@dataclass
class OntologyProperty:
    """Represents an ontology property with multilingual labels"""
    property_uri: str
    property_type: str  # 'ObjectProperty', 'DatatypeProperty', 'AnnotationProperty'
    labels: Dict[str, str]
    alt_labels: Dict[str, List[str]]
    description: Dict[str, str]
    domain: Optional[str]
    range: Optional[str]
    parent_properties: List[str]

class LimitGraphOntologyBuilder:
    """
    Builds lightweight OWL ontologies for LIMIT-Graph components
    Supports multilingual alignment and cross-cultural knowledge representation
    """
    
    def __init__(self, base_uri: str = "http://limitgraph.org/ontology/"):
        """Initialize the ontology builder"""
        self.base_uri = base_uri
        
        # Define namespaces
        self.LGONT = Namespace(base_uri)
        self.LG = Namespace("http://limitgraph.org/")
        
        # Initialize ontology graph
        self.ontology = Graph()
        self._bind_namespaces()
        
        # Multilingual support
        self.supported_languages = ['en', 'es', 'ar', 'id', 'zh', 'hi', 'fr', 'de']
        
        # Core ontology classes and properties
        self.core_classes = {}
        self.core_properties = {}
        
        print("🏗️ LIMIT-Graph Ontology Builder initialized")
    
    def _bind_namespaces(self):
        """Bind namespaces to the ontology graph"""
        self.ontology.bind("lgont", self.LGONT)
        self.ontology.bind("lg", self.LG)
        self.ontology.bind("rdf", RDF)
        self.ontology.bind("rdfs", RDFS)
        self.ontology.bind("owl", OWL)
        self.ontology.bind("skos", SKOS)
        self.ontology.bind("foaf", FOAF)
        self.ontology.bind("dc", DC)
        self.ontology.bind("dcterms", DCTERMS)
    
    def create_core_ontology(self):
        """Create the core LIMIT-Graph ontology with all essential classes and properties"""
        
        # Ontology metadata
        self.ontology.add((URIRef(self.base_uri), RDF.type, OWL.Ontology))
        self.ontology.add((URIRef(self.base_uri), RDFS.label, Literal("LIMIT-Graph Core Ontology", lang="en")))
        self.ontology.add((URIRef(self.base_uri), RDFS.label, Literal("Ontología Central LIMIT-Graph", lang="es")))
        self.ontology.add((URIRef(self.base_uri), RDFS.label, Literal("أنطولوجيا LIMIT-Graph الأساسية", lang="ar")))
        self.ontology.add((URIRef(self.base_uri), RDFS.label, Literal("Ontologi Inti LIMIT-Graph", lang="id")))
        self.ontology.add((URIRef(self.base_uri), DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.ontology.add((URIRef(self.base_uri), DCTERMS.description, 
                          Literal("Core ontology for LIMIT-Graph multilingual knowledge representation", lang="en")))
        
        # Create core classes
        self._create_agent_classes()
        self._create_entity_classes()
        self._create_relation_classes()
        self._create_language_classes()
        self._create_annotation_classes()
        
        # Create core properties
        self._create_core_properties()
        
        print("✅ Core ontology created with multilingual support")
    
    def _create_agent_classes(self):
        """Create agent-related classes"""
        
        # Agent class
        agent_class = OntologyClass(
            class_uri=str(self.LGONT.Agent),
            labels={
                'en': 'Agent',
                'es': 'Agente',
                'ar': 'وكيل',
                'id': 'Agen',
                'zh': '代理',
                'hi': 'एजेंट'
            },
            alt_labels={
                'en': ['Actor', 'Entity', 'Participant'],
                'es': ['Actor', 'Entidad', 'Participante'],
                'ar': ['فاعل', 'كيان', 'مشارك'],
                'id': ['Aktor', 'Entitas', 'Peserta']
            },
            description={
                'en': 'An autonomous entity that can perform actions and make decisions',
                'es': 'Una entidad autónoma que puede realizar acciones y tomar decisiones',
                'ar': 'كيان مستقل يمكنه أداء الأعمال واتخاذ القرارات',
                'id': 'Entitas otonom yang dapat melakukan tindakan dan membuat keputusan'
            },
            parent_classes=[str(OWL.Thing)],
            properties=['hasCapability', 'performsAction', 'hasGoal']
        )
        
        self._add_class_to_ontology(agent_class)
        
        # Annotator subclass
        annotator_class = OntologyClass(
            class_uri=str(self.LGONT.Annotator),
            labels={
                'en': 'Annotator',
                'es': 'Anotador',
                'ar': 'مُعلِّق',
                'id': 'Anotator',
                'zh': '注释者',
                'hi': 'एनोटेटर'
            },
            alt_labels={
                'en': ['Labeler', 'Tagger', 'Marker'],
                'es': ['Etiquetador', 'Marcador'],
                'ar': ['مُصنِّف', 'مُعلِّم'],
                'id': ['Pelabel', 'Penanda']
            },
            description={
                'en': 'An agent that provides annotations and labels for data',
                'es': 'Un agente que proporciona anotaciones y etiquetas para datos',
                'ar': 'وكيل يقدم التعليقات والتسميات للبيانات',
                'id': 'Agen yang memberikan anotasi dan label untuk data'
            },
            parent_classes=[str(self.LGONT.Agent)],
            properties=['annotates', 'hasExpertise', 'speaksLanguage']
        )
        
        self._add_class_to_ontology(annotator_class)
    
    def _create_entity_classes(self):
        """Create entity-related classes"""
        
        # Entity class
        entity_class = OntologyClass(
            class_uri=str(self.LGONT.Entity),
            labels={
                'en': 'Entity',
                'es': 'Entidad',
                'ar': 'كيان',
                'id': 'Entitas',
                'zh': '实体',
                'hi': 'इकाई'
            },
            alt_labels={
                'en': ['Thing', 'Object', 'Item'],
                'es': ['Cosa', 'Objeto', 'Elemento'],
                'ar': ['شيء', 'كائن', 'عنصر'],
                'id': ['Benda', 'Objek', 'Item']
            },
            description={
                'en': 'A distinct object or concept that can be identified and described',
                'es': 'Un objeto o concepto distinto que puede ser identificado y descrito',
                'ar': 'كائن أو مفهوم متميز يمكن تحديده ووصفه',
                'id': 'Objek atau konsep yang berbeda yang dapat diidentifikasi dan dijelaskan'
            },
            parent_classes=[str(OWL.Thing)],
            properties=['hasProperty', 'relatedTo', 'partOf']
        )
        
        self._add_class_to_ontology(entity_class)
        
        # Person subclass
        person_class = OntologyClass(
            class_uri=str(self.LGONT.Person),
            labels={
                'en': 'Person',
                'es': 'Persona',
                'ar': 'شخص',
                'id': 'Orang',
                'zh': '人',
                'hi': 'व्यक्ति'
            },
            alt_labels={
                'en': ['Individual', 'Human', 'People'],
                'es': ['Individuo', 'Humano', 'Gente'],
                'ar': ['فرد', 'إنسان', 'أشخاص'],
                'id': ['Individu', 'Manusia', 'Orang-orang']
            },
            description={
                'en': 'A human being',
                'es': 'Un ser humano',
                'ar': 'كائن بشري',
                'id': 'Seorang manusia'
            },
            parent_classes=[str(self.LGONT.Entity), str(FOAF.Person)],
            properties=['hasName', 'likes', 'owns', 'livesIn']
        )
        
        self._add_class_to_ontology(person_class)
        
        # Location subclass
        location_class = OntologyClass(
            class_uri=str(self.LGONT.Location),
            labels={
                'en': 'Location',
                'es': 'Ubicación',
                'ar': 'موقع',
                'id': 'Lokasi',
                'zh': '位置',
                'hi': 'स्थान'
            },
            alt_labels={
                'en': ['Place', 'Position', 'Site'],
                'es': ['Lugar', 'Posición', 'Sitio'],
                'ar': ['مكان', 'موضع', 'موقع'],
                'id': ['Tempat', 'Posisi', 'Situs']
            },
            description={
                'en': 'A spatial region or geographical area',
                'es': 'Una región espacial o área geográfica',
                'ar': 'منطقة مكانية أو منطقة جغرافية',
                'id': 'Wilayah spasial atau area geografis'
            },
            parent_classes=[str(self.LGONT.Entity)],
            properties=['contains', 'locatedIn', 'hasCoordinates']
        )
        
        self._add_class_to_ontology(location_class)
    
    def _create_relation_classes(self):
        """Create relation-related classes"""
        
        # Relation class
        relation_class = OntologyClass(
            class_uri=str(self.LGONT.Relation),
            labels={
                'en': 'Relation',
                'es': 'Relación',
                'ar': 'علاقة',
                'id': 'Relasi',
                'zh': '关系',
                'hi': 'संबंध'
            },
            alt_labels={
                'en': ['Relationship', 'Connection', 'Association'],
                'es': ['Relación', 'Conexión', 'Asociación'],
                'ar': ['رابطة', 'اتصال', 'ارتباط'],
                'id': ['Hubungan', 'Koneksi', 'Asosiasi']
            },
            description={
                'en': 'A connection or association between two or more entities',
                'es': 'Una conexión o asociación entre dos o más entidades',
                'ar': 'اتصال أو ارتباط بين كيانين أو أكثر',
                'id': 'Koneksi atau asosiasi antara dua atau lebih entitas'
            },
            parent_classes=[str(OWL.Thing)],
            properties=['hasSubject', 'hasObject', 'hasType', 'hasConfidence']
        )
        
        self._add_class_to_ontology(relation_class)
        
        # Statement class
        statement_class = OntologyClass(
            class_uri=str(self.LGONT.Statement),
            labels={
                'en': 'Statement',
                'es': 'Declaración',
                'ar': 'بيان',
                'id': 'Pernyataan',
                'zh': '陈述',
                'hi': 'कथन'
            },
            alt_labels={
                'en': ['Assertion', 'Claim', 'Proposition'],
                'es': ['Afirmación', 'Reclamo', 'Proposición'],
                'ar': ['تأكيد', 'ادعاء', 'اقتراح'],
                'id': ['Pernyataan', 'Klaim', 'Proposisi']
            },
            description={
                'en': 'A declarative sentence that expresses a fact or assertion',
                'es': 'Una oración declarativa que expresa un hecho o afirmación',
                'ar': 'جملة تصريحية تعبر عن حقيقة أو تأكيد',
                'id': 'Kalimat deklaratif yang mengekspresikan fakta atau pernyataan'
            },
            parent_classes=[str(self.LGONT.Relation)],
            properties=['hasSubject', 'hasPredicate', 'hasObject', 'hasProvenance']
        )
        
        self._add_class_to_ontology(statement_class)
    
    def _create_language_classes(self):
        """Create language-related classes"""
        
        # Language class
        language_class = OntologyClass(
            class_uri=str(self.LGONT.Language),
            labels={
                'en': 'Language',
                'es': 'Idioma',
                'ar': 'لغة',
                'id': 'Bahasa',
                'zh': '语言',
                'hi': 'भाषा'
            },
            alt_labels={
                'en': ['Tongue', 'Speech', 'Dialect'],
                'es': ['Lengua', 'Habla', 'Dialecto'],
                'ar': ['لسان', 'كلام', 'لهجة'],
                'id': ['Lidah', 'Ucapan', 'Dialek']
            },
            description={
                'en': 'A system of communication used by humans',
                'es': 'Un sistema de comunicación utilizado por los humanos',
                'ar': 'نظام تواصل يستخدمه البشر',
                'id': 'Sistem komunikasi yang digunakan oleh manusia'
            },
            parent_classes=[str(OWL.Thing)],
            properties=['hasCode', 'hasScript', 'isRightToLeft', 'hasDialect']
        )
        
        self._add_class_to_ontology(language_class)
        
        # LanguageAnnotation class
        lang_annotation_class = OntologyClass(
            class_uri=str(self.LGONT.LanguageAnnotation),
            labels={
                'en': 'Language Annotation',
                'es': 'Anotación de Idioma',
                'ar': 'تعليق لغوي',
                'id': 'Anotasi Bahasa',
                'zh': '语言注释',
                'hi': 'भाषा एनोटेशन'
            },
            alt_labels={
                'en': ['Language Tag', 'Language Label'],
                'es': ['Etiqueta de Idioma', 'Etiqueta Lingüística'],
                'ar': ['علامة لغوية', 'تسمية لغوية'],
                'id': ['Tag Bahasa', 'Label Bahasa']
            },
            description={
                'en': 'An annotation that identifies the language of text content',
                'es': 'Una anotación que identifica el idioma del contenido del texto',
                'ar': 'تعليق يحدد لغة محتوى النص',
                'id': 'Anotasi yang mengidentifikasi bahasa konten teks'
            },
            parent_classes=[str(self.LGONT.Annotation)],
            properties=['annotatesStatement', 'hasLanguage', 'hasConfidence']
        )
        
        self._add_class_to_ontology(lang_annotation_class)
    
    def _create_annotation_classes(self):
        """Create annotation-related classes"""
        
        # Annotation class
        annotation_class = OntologyClass(
            class_uri=str(self.LGONT.Annotation),
            labels={
                'en': 'Annotation',
                'es': 'Anotación',
                'ar': 'تعليق',
                'id': 'Anotasi',
                'zh': '注释',
                'hi': 'एनोटेशन'
            },
            alt_labels={
                'en': ['Note', 'Comment', 'Label'],
                'es': ['Nota', 'Comentario', 'Etiqueta'],
                'ar': ['ملاحظة', 'تعليق', 'تسمية'],
                'id': ['Catatan', 'Komentar', 'Label']
            },
            description={
                'en': 'Additional information or metadata attached to content',
                'es': 'Información adicional o metadatos adjuntos al contenido',
                'ar': 'معلومات إضافية أو بيانات وصفية مرفقة بالمحتوى',
                'id': 'Informasi tambahan atau metadata yang dilampirkan pada konten'
            },
            parent_classes=[str(OWL.Thing)],
            properties=['annotates', 'hasAnnotator', 'hasTimestamp', 'hasConfidence']
        )
        
        self._add_class_to_ontology(annotation_class)
        
        # RLHFFeedback class
        rlhf_class = OntologyClass(
            class_uri=str(self.LGONT.RLHFFeedback),
            labels={
                'en': 'RLHF Feedback',
                'es': 'Retroalimentación RLHF',
                'ar': 'تغذية راجعة RLHF',
                'id': 'Umpan Balik RLHF',
                'zh': 'RLHF反馈',
                'hi': 'RLHF फीडबैक'
            },
            alt_labels={
                'en': ['Human Feedback', 'Quality Assessment'],
                'es': ['Retroalimentación Humana', 'Evaluación de Calidad'],
                'ar': ['تغذية راجعة بشرية', 'تقييم الجودة'],
                'id': ['Umpan Balik Manusia', 'Penilaian Kualitas']
            },
            description={
                'en': 'Human feedback for reinforcement learning systems',
                'es': 'Retroalimentación humana para sistemas de aprendizaje por refuerzo',
                'ar': 'تغذية راجعة بشرية لأنظمة التعلم المعزز',
                'id': 'Umpan balik manusia untuk sistem pembelajaran penguatan'
            },
            parent_classes=[str(self.LGONT.Annotation)],
            properties=['hasQualityScore', 'hasRelevanceScore', 'hasFeedbackType']
        )
        
        self._add_class_to_ontology(rlhf_class)
    
    def _create_core_properties(self):
        """Create core ontology properties"""
        
        # Object properties
        object_properties = [
            {
                'uri': str(self.LGONT.hasSubject),
                'labels': {'en': 'has subject', 'es': 'tiene sujeto', 'ar': 'له موضوع', 'id': 'memiliki subjek'},
                'description': {'en': 'Relates a statement to its subject'},
                'domain': str(self.LGONT.Statement),
                'range': str(self.LGONT.Entity)
            },
            {
                'uri': str(self.LGONT.hasPredicate),
                'labels': {'en': 'has predicate', 'es': 'tiene predicado', 'ar': 'له محمول', 'id': 'memiliki predikat'},
                'description': {'en': 'Relates a statement to its predicate'},
                'domain': str(self.LGONT.Statement),
                'range': str(self.LGONT.Relation)
            },
            {
                'uri': str(self.LGONT.hasObject),
                'labels': {'en': 'has object', 'es': 'tiene objeto', 'ar': 'له مفعول', 'id': 'memiliki objek'},
                'description': {'en': 'Relates a statement to its object'},
                'domain': str(self.LGONT.Statement),
                'range': str(OWL.Thing)
            },
            {
                'uri': str(self.LGONT.likes),
                'labels': {'en': 'likes', 'es': 'le gusta', 'ar': 'يحب', 'id': 'suka'},
                'description': {'en': 'Expresses preference or enjoyment'},
                'domain': str(self.LGONT.Person),
                'range': str(self.LGONT.Entity)
            },
            {
                'uri': str(self.LGONT.owns),
                'labels': {'en': 'owns', 'es': 'posee', 'ar': 'يملك', 'id': 'memiliki'},
                'description': {'en': 'Indicates ownership or possession'},
                'domain': str(self.LGONT.Person),
                'range': str(self.LGONT.Entity)
            },
            {
                'uri': str(self.LGONT.locatedIn),
                'labels': {'en': 'located in', 'es': 'ubicado en', 'ar': 'يقع في', 'id': 'terletak di'},
                'description': {'en': 'Indicates spatial containment'},
                'domain': str(self.LGONT.Entity),
                'range': str(self.LGONT.Location)
            }
        ]
        
        for prop_data in object_properties:
            prop = OntologyProperty(
                property_uri=prop_data['uri'],
                property_type='ObjectProperty',
                labels=prop_data['labels'],
                alt_labels={},
                description=prop_data['description'],
                domain=prop_data.get('domain'),
                range=prop_data.get('range'),
                parent_properties=[]
            )
            self._add_property_to_ontology(prop)
        
        # Datatype properties
        datatype_properties = [
            {
                'uri': str(self.LGONT.confidence),
                'labels': {'en': 'confidence', 'es': 'confianza', 'ar': 'ثقة', 'id': 'kepercayaan'},
                'description': {'en': 'Confidence score for a statement or annotation'},
                'range': str(XSD.float)
            },
            {
                'uri': str(self.LGONT.timestamp),
                'labels': {'en': 'timestamp', 'es': 'marca de tiempo', 'ar': 'طابع زمني', 'id': 'cap waktu'},
                'description': {'en': 'Time when something was created or modified'},
                'range': str(XSD.dateTime)
            },
            {
                'uri': str(self.LGONT.languageCode),
                'labels': {'en': 'language code', 'es': 'código de idioma', 'ar': 'رمز اللغة', 'id': 'kode bahasa'},
                'description': {'en': 'ISO language code'},
                'range': str(XSD.string)
            },
            {
                'uri': str(self.LGONT.annotatorId),
                'labels': {'en': 'annotator ID', 'es': 'ID del anotador', 'ar': 'معرف المُعلِّق', 'id': 'ID anotator'},
                'description': {'en': 'Unique identifier for an annotator'},
                'range': str(XSD.string)
            }
        ]
        
        for prop_data in datatype_properties:
            prop = OntologyProperty(
                property_uri=prop_data['uri'],
                property_type='DatatypeProperty',
                labels=prop_data['labels'],
                alt_labels={},
                description=prop_data['description'],
                domain=None,
                range=prop_data.get('range'),
                parent_properties=[]
            )
            self._add_property_to_ontology(prop)
    
    def _add_class_to_ontology(self, ontology_class: OntologyClass):
        """Add a class to the ontology with multilingual labels"""
        
        class_uri = URIRef(ontology_class.class_uri)
        
        # Add class declaration
        self.ontology.add((class_uri, RDF.type, OWL.Class))
        
        # Add labels
        for lang, label in ontology_class.labels.items():
            self.ontology.add((class_uri, RDFS.label, Literal(label, lang=lang)))
        
        # Add alternative labels
        for lang, alt_labels in ontology_class.alt_labels.items():
            for alt_label in alt_labels:
                self.ontology.add((class_uri, SKOS.altLabel, Literal(alt_label, lang=lang)))
        
        # Add descriptions
        for lang, description in ontology_class.description.items():
            self.ontology.add((class_uri, RDFS.comment, Literal(description, lang=lang)))
        
        # Add parent classes
        for parent_class in ontology_class.parent_classes:
            self.ontology.add((class_uri, RDFS.subClassOf, URIRef(parent_class)))
        
        # Store in registry
        self.core_classes[ontology_class.class_uri] = ontology_class
    
    def _add_property_to_ontology(self, ontology_property: OntologyProperty):
        """Add a property to the ontology with multilingual labels"""
        
        prop_uri = URIRef(ontology_property.property_uri)
        
        # Add property declaration
        if ontology_property.property_type == 'ObjectProperty':
            self.ontology.add((prop_uri, RDF.type, OWL.ObjectProperty))
        elif ontology_property.property_type == 'DatatypeProperty':
            self.ontology.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        elif ontology_property.property_type == 'AnnotationProperty':
            self.ontology.add((prop_uri, RDF.type, OWL.AnnotationProperty))
        
        # Add labels
        for lang, label in ontology_property.labels.items():
            self.ontology.add((prop_uri, RDFS.label, Literal(label, lang=lang)))
        
        # Add alternative labels
        for lang, alt_labels in ontology_property.alt_labels.items():
            for alt_label in alt_labels:
                self.ontology.add((prop_uri, SKOS.altLabel, Literal(alt_label, lang=lang)))
        
        # Add descriptions
        for lang, description in ontology_property.description.items():
            self.ontology.add((prop_uri, RDFS.comment, Literal(description, lang=lang)))
        
        # Add domain and range
        if ontology_property.domain:
            self.ontology.add((prop_uri, RDFS.domain, URIRef(ontology_property.domain)))
        
        if ontology_property.range:
            self.ontology.add((prop_uri, RDFS.range, URIRef(ontology_property.range)))
        
        # Add parent properties
        for parent_prop in ontology_property.parent_properties:
            self.ontology.add((prop_uri, RDFS.subPropertyOf, URIRef(parent_prop)))
        
        # Store in registry
        self.core_properties[ontology_property.property_uri] = ontology_property
    
    def add_multilingual_alignment(self, entity_uri: str, same_as_uris: List[str], 
                                  alt_labels: Dict[str, List[str]]):
        """Add multilingual alignment using owl:sameAs and skos:altLabel"""
        
        entity = URIRef(entity_uri)
        
        # Add owl:sameAs relationships
        for same_as_uri in same_as_uris:
            self.ontology.add((entity, OWL.sameAs, URIRef(same_as_uri)))
        
        # Add alternative labels
        for lang, labels in alt_labels.items():
            for label in labels:
                self.ontology.add((entity, SKOS.altLabel, Literal(label, lang=lang)))
    
    def create_domain_specific_ontology(self, domain: str, 
                                       domain_classes: List[OntologyClass],
                                       domain_properties: List[OntologyProperty]):
        """Create a domain-specific ontology extension"""
        
        # Create domain namespace
        domain_ns = Namespace(f"{self.base_uri}{domain}/")
        self.ontology.bind(domain, domain_ns)
        
        # Add domain classes
        for domain_class in domain_classes:
            self._add_class_to_ontology(domain_class)
        
        # Add domain properties
        for domain_property in domain_properties:
            self._add_property_to_ontology(domain_property)
        
        print(f"✅ Created domain-specific ontology for: {domain}")
    
    def export_ontology(self, output_dir: str = "output/rdf/ontologies/"):
        """Export ontology to multiple formats"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        formats = {
            'turtle': 'ttl',
            'xml': 'owl',
            'n3': 'n3',
            'json-ld': 'jsonld'
        }
        
        exported_files = {}
        
        for format_name, extension in formats.items():
            try:
                filename = f"limitgraph_ontology.{extension}"
                filepath = os.path.join(output_dir, filename)
                
                self.ontology.serialize(destination=filepath, format=format_name)
                exported_files[format_name] = filepath
                print(f"✅ Exported ontology ({format_name}) to {filepath}")
                
            except Exception as e:
                print(f"❌ Failed to export ontology ({format_name}): {e}")
        
        return exported_files
    
    def get_ontology_statistics(self) -> Dict[str, Any]:
        """Get statistics about the ontology"""
        
        # Count different types of resources
        classes = len(list(self.ontology.subjects(RDF.type, OWL.Class)))
        object_props = len(list(self.ontology.subjects(RDF.type, OWL.ObjectProperty)))
        datatype_props = len(list(self.ontology.subjects(RDF.type, OWL.DatatypeProperty)))
        annotation_props = len(list(self.ontology.subjects(RDF.type, OWL.AnnotationProperty)))
        
        # Count multilingual labels
        labels = len(list(self.ontology.triples((None, RDFS.label, None))))
        alt_labels = len(list(self.ontology.triples((None, SKOS.altLabel, None))))
        
        # Count languages
        languages = set()
        for _, _, literal in self.ontology.triples((None, RDFS.label, None)):
            if hasattr(literal, 'language') and literal.language:
                languages.add(literal.language)
        
        return {
            'total_triples': len(self.ontology),
            'classes': classes,
            'object_properties': object_props,
            'datatype_properties': datatype_props,
            'annotation_properties': annotation_props,
            'labels': labels,
            'alternative_labels': alt_labels,
            'languages_supported': list(languages),
            'namespaces': list(self.ontology.namespaces())
        }

# Demo and testing functions
def demo_ontology_creation():
    """Demonstrate ontology creation capabilities"""
    
    print("🏗️ LIMIT-Graph Ontology Creation Demo")
    
    # Initialize builder
    builder = LimitGraphOntologyBuilder()
    
    # Create core ontology
    builder.create_core_ontology()
    
    # Add multilingual alignments
    builder.add_multilingual_alignment(
        entity_uri=str(builder.LGONT.Person),
        same_as_uris=[str(FOAF.Person), "http://schema.org/Person"],
        alt_labels={
            'en': ['Human Being', 'Individual'],
            'es': ['Ser Humano', 'Individuo'],
            'ar': ['كائن بشري', 'فرد'],
            'id': ['Manusia', 'Individu']
        }
    )
    
    # Create domain-specific extension (food domain)
    food_classes = [
        OntologyClass(
            class_uri=str(builder.LGONT.Food),
            labels={'en': 'Food', 'es': 'Comida', 'ar': 'طعام', 'id': 'Makanan'},
            alt_labels={'en': ['Edible', 'Nourishment'], 'es': ['Comestible', 'Alimento']},
            description={'en': 'Edible substance that provides nutrition'},
            parent_classes=[str(builder.LGONT.Entity)],
            properties=['hasNutrient', 'hasCalories']
        )
    ]
    
    food_properties = [
        OntologyProperty(
            property_uri=str(builder.LGONT.hasNutrient),
            property_type='ObjectProperty',
            labels={'en': 'has nutrient', 'es': 'tiene nutriente'},
            alt_labels={},
            description={'en': 'Indicates nutritional content'},
            domain=str(builder.LGONT.Food),
            range=str(builder.LGONT.Entity),
            parent_properties=[]
        )
    ]
    
    builder.create_domain_specific_ontology("food", food_classes, food_properties)
    
    # Get statistics
    stats = builder.get_ontology_statistics()
    print(f"\n📊 Ontology Statistics:")
    print(f"  - Total triples: {stats['total_triples']}")
    print(f"  - Classes: {stats['classes']}")
    print(f"  - Object properties: {stats['object_properties']}")
    print(f"  - Datatype properties: {stats['datatype_properties']}")
    print(f"  - Labels: {stats['labels']}")
    print(f"  - Alternative labels: {stats['alternative_labels']}")
    print(f"  - Languages: {stats['languages_supported']}")
    
    # Export ontology
    exported_files = builder.export_ontology()
    print(f"\n💾 Exported ontology files: {list(exported_files.keys())}")
    
    return builder

if __name__ == "__main__":
    demo_ontology_creation()