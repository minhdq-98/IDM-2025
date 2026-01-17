# IDM-2025

A comprehensive financial knowledge graph extraction and evaluation system based on the FinReflectKG dataset. This project implements pipelines for extracting structured knowledge from financial documents (SEC filings, Nasdaq news) and storing them in a Neo4j graph database.

## Overview

This project provides tools and pipelines for:
- **Knowledge Graph Extraction**: Extracting entities and relationships from financial documents using Large Language Models (LLMs)
- **Graph Database Storage**: Storing extracted knowledge in Neo4j with provenance tracking
- **Evaluation Framework**: Using LLM-as-a-judge methodology to evaluate extraction quality
- **Query Interface**: Natural language querying of the knowledge graph using Cypher

## Features

### 📊 Knowledge Graph Extraction
- **24 Entity Types**: Organizations, People, Financial Instruments, Events, ESG Topics, and more
- **27+ Relationship Types**: Complex relationships like `Has_Stake_In`, `Regulates`, `Impacts`, `Partners_With`, etc.
- **Provenance Tracking**: Every extracted fact includes source URL, timestamp, and evidence text
- **Structured Schema**: Based on FinReflectKG ontology for financial domain knowledge

### 🔍 Entity Types
- **Core Business**: ORG, COMP, SEGMENT, PERSON
- **Geographic & Regulatory**: GPE, ORG_GOV, ORG_REG
- **Financial & Market**: FIN_INST, FIN_MARKET, FIN_METRIC, ECON_IND
- **Products & Operations**: PRODUCT, CONCEPT, RAW_MATERIAL, LOGISTICS
- **Risk & Compliance**: RISK_FACTOR, LITIGATION, REGULATORY_REQUIREMENT, ACCOUNTING_POLICY
- **Strategic & ESG**: EVENT, SECTOR, ESG_TOPIC, MACRO_CONDITION, COMMENTARY

### 🎯 Evaluation
- **LLM-as-a-Judge**: Automated evaluation using multiple judge models
- **Multiple Metrics**: Correctness, relevance, and classification-based evaluation
- **Comprehensive Reporting**: Detailed evaluation reports with scores and reasoning

## Project Structure

```
IDM-2025/
├── ontology.py              # Base ontology models (ProvableFact, ProvenanceModel, etc.)
├── financial_ontology.py    # Financial-specific entity and relationship types
├── financial_schema.json    # JSON schema for financial knowledge graph
├── model.py                 # Pydantic models for structured extraction
├── pipeline1.ipynb          # Proof-of-concept pipeline (without ODKE+)
├── pipeline2.ipynb          # Full knowledge graph extraction pipeline
├── llm_as_a_judge.ipynb    # Evaluation framework using LLM judges
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IDM-2025
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   GOOGLE_API_KEY=your_google_api_key
   ```

4. **Set up Neo4j database**
   - Install and start Neo4j
   - Create a database instance
   - Update connection details in `.env`

## Usage

> **Note**: The `pipeline1.ipynb` and `pipeline2.ipynb` notebooks are designed to be run on **Google Colab**. Please upload these notebooks to Google Colab for execution.

### Pipeline 1: Basic Extraction
The `pipeline1.ipynb` notebook demonstrates a proof-of-concept extraction pipeline:
- Loads financial data from CSV files
- Extracts entities and relationships using LLMs
- Stores results in Neo4j

### Pipeline 2: Full Knowledge Graph Pipeline
The `pipeline2.ipynb` notebook implements the complete pipeline:
- Entity and relationship extraction from financial news
- Grounding and validation
- Neo4j ingestion with full provenance
- Natural language querying with Cypher generation

### Evaluation
The `llm_as_a_judge.ipynb` notebook provides evaluation capabilities:
- Judge model configuration
- Automated scoring and reasoning
- Comprehensive evaluation reports

## Dependencies

- **pandas** >= 2.0.0 - Data manipulation
- **rdflib** >= 6.0.0 - RDF/OWL ontology handling
- **neo4j** >= 5.13.0 - Graph database driver
- **google-generativeai** >= 0.3.0 - Google Gemini API
- **langchain_neo4j** >= 0.1.0 - LangChain Neo4j integration
- **judges** >= 0.1.0 - LLM-as-a-judge evaluation framework
- **beautifulsoup4** >= 4.12.0 - Web scraping
- **tqdm** >= 4.65.0 - Progress bars

## Data Sources

- **FinReflectKG Dataset**: Based on [domyn/FinReflectKG](https://huggingface.co/datasets/domyn/FinReflectKG)
- **Nasdaq 100**: Financial news summaries and articles
- **SEC Filings**: 10-K filings and other financial documents

## Key Concepts

### ProvableFact
Each extracted fact includes:
- `value`: The extracted information
- `evidence`: The exact text snippet supporting the fact

### ProvenanceModel
Tracks the origin of each extraction:
- `url`: Source URL
- `retrieved_at`: Timestamp
- `trust_score`: Confidence score for the source

### ExtractionPackage
Bundles extracted data with provenance metadata for ingestion.

## Contributing

This is a research project for financial knowledge graph extraction. Contributions and improvements are welcome!

## License

[Specify your license here]

## References

- FinReflectKG Dataset: https://huggingface.co/datasets/domyn/FinReflectKG
- Neo4j Documentation: https://neo4j.com/docs/
- LangChain Neo4j: https://python.langchain.com/docs/integrations/graphs/neo4j
