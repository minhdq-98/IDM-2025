"""
Build an ontology from nasdaq_dec2023.csv file.
Creates an OWL ontology with stock symbols as entities and their associated articles.
"""

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.namespace import FOAF, DCTERMS
import urllib.parse
from tqdm import tqdm

# Define namespaces
NAS = Namespace("http://example.org/nasdaq/ontology#")
NAS_DATA = Namespace("http://example.org/nasdaq/data#")

def sanitize_uri(text):
    """Sanitize text to be used in URIs"""
    if pd.isna(text) or text == '':
        return "unknown"
    # Remove special characters and replace spaces
    text = str(text)
    text = urllib.parse.quote(text, safe='')
    return text[:100]  # Limit length

def build_ontology(csv_file, output_file='nasdaq_ontology.owl', sample_size=None):
    """
    Build an ontology from the CSV file.
    
    Args:
        csv_file: Path to the CSV file
        output_file: Output OWL file path
        sample_size: If specified, only process first N rows (for testing)
    """
    print("Loading CSV data...")
    df = pd.read_csv(csv_file, dtype=str, low_memory=False)
    
    if sample_size:
        df = df.head(sample_size)
        print(f"Processing sample of {sample_size} rows...")
    else:
        print(f"Processing {len(df)} rows...")
    
    # Initialize RDF graph
    g = Graph()
    
    # Bind namespaces
    g.bind("nas", NAS)
    g.bind("nasdata", NAS_DATA)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("foaf", FOAF)
    g.bind("dcterms", DCTERMS)
    
    print("Defining ontology classes and properties...")
    
    # Define Classes
    Stock = NAS.Stock
    Article = NAS.Article
    Summary = NAS.Summary
    Publisher = NAS.Publisher
    Author = NAS.Author
    
    g.add((Stock, RDF.type, OWL.Class))
    g.add((Stock, RDFS.label, Literal("Stock", lang="en")))
    g.add((Stock, RDFS.comment, Literal("A stock symbol entity representing a publicly traded company", lang="en")))
    
    g.add((Article, RDF.type, OWL.Class))
    g.add((Article, RDFS.label, Literal("Article", lang="en")))
    g.add((Article, RDFS.comment, Literal("A news article about a stock", lang="en")))
    
    g.add((Summary, RDF.type, OWL.Class))
    g.add((Summary, RDFS.label, Literal("Summary", lang="en")))
    g.add((Summary, RDFS.comment, Literal("A summary of an article", lang="en")))
    
    g.add((Publisher, RDF.type, OWL.Class))
    g.add((Publisher, RDFS.label, Literal("Publisher", lang="en")))
    
    g.add((Author, RDF.type, OWL.Class))
    g.add((Author, RDFS.label, Literal("Author", lang="en")))
    
    # Define Object Properties
    hasArticle = NAS.hasArticle
    hasSummary = NAS.hasSummary
    hasPublisher = NAS.hasPublisher
    hasAuthor = NAS.hasAuthor
    
    g.add((hasArticle, RDF.type, OWL.ObjectProperty))
    g.add((hasArticle, RDFS.domain, Stock))
    g.add((hasArticle, RDFS.range, Article))
    g.add((hasArticle, RDFS.label, Literal("hasArticle", lang="en")))
    
    g.add((hasSummary, RDF.type, OWL.ObjectProperty))
    g.add((hasSummary, RDFS.domain, Article))
    g.add((hasSummary, RDFS.range, Summary))
    g.add((hasSummary, RDFS.label, Literal("hasSummary", lang="en")))
    
    g.add((hasPublisher, RDF.type, OWL.ObjectProperty))
    g.add((hasPublisher, RDFS.domain, Article))
    g.add((hasPublisher, RDFS.range, Publisher))
    g.add((hasPublisher, RDFS.label, Literal("hasPublisher", lang="en")))
    
    g.add((hasAuthor, RDF.type, OWL.ObjectProperty))
    g.add((hasAuthor, RDFS.domain, Article))
    g.add((hasAuthor, RDFS.range, Author))
    g.add((hasAuthor, RDFS.label, Literal("hasAuthor", lang="en")))
    
    # Define Datatype Properties
    hasSymbol = NAS.hasSymbol
    hasTitle = NAS.hasTitle
    hasUrl = NAS.hasUrl
    hasDate = NAS.hasDate
    hasContent = NAS.hasContent
    hasLsaSummary = NAS.hasLsaSummary
    hasLuhnSummary = NAS.hasLuhnSummary
    hasTextrankSummary = NAS.hasTextrankSummary
    hasLexrankSummary = NAS.hasLexrankSummary
    publisherName = NAS.publisherName
    authorName = NAS.authorName
    
    datatype_props = [
        (hasSymbol, Stock, "stock symbol"),
        (hasTitle, Article, "article title"),
        (hasUrl, Article, "article URL"),
        (hasDate, Article, "publication date"),
        (hasContent, Article, "article content"),
        (hasLsaSummary, Summary, "LSA summary"),
        (hasLuhnSummary, Summary, "Luhn summary"),
        (hasTextrankSummary, Summary, "TextRank summary"),
        (hasLexrankSummary, Summary, "LexRank summary"),
        (publisherName, Publisher, "publisher name"),
        (authorName, Author, "author name"),
    ]
    
    for prop, domain, label in datatype_props:
        g.add((prop, RDF.type, OWL.DatatypeProperty))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, XSD.string))
        g.add((prop, RDFS.label, Literal(label, lang="en")))
    
    print("Creating instances and relationships...")
    
    # Track unique entities to avoid duplicates
    stocks_created = set()
    publishers_created = set()
    authors_created = set()
    
    # Process each row
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        try:
            stock_symbol = str(row['Stock_symbol']).strip() if pd.notna(row['Stock_symbol']) else None
            if not stock_symbol or stock_symbol == 'nan':
                continue
            
            # Create or get Stock instance
            stock_uri = NAS_DATA[f"stock_{sanitize_uri(stock_symbol)}"]
            if stock_symbol not in stocks_created:
                g.add((stock_uri, RDF.type, Stock))
                g.add((stock_uri, hasSymbol, Literal(stock_symbol)))
                g.add((stock_uri, RDFS.label, Literal(f"Stock {stock_symbol}", lang="en")))
                stocks_created.add(stock_symbol)
            
            # Create Article instance
            article_id = f"article_{idx}"
            article_uri = NAS_DATA[article_id]
            g.add((article_uri, RDF.type, Article))
            
            # Link stock to article
            g.add((stock_uri, hasArticle, article_uri))
            
            # Add article properties
            if pd.notna(row.get('Article_title')):
                title = str(row['Article_title']).strip()
                g.add((article_uri, hasTitle, Literal(title)))
                g.add((article_uri, RDFS.label, Literal(title[:100], lang="en")))
            
            if pd.notna(row.get('Url')):
                g.add((article_uri, hasUrl, Literal(str(row['Url']).strip())))
            
            if pd.notna(row.get('Date')):
                date_str = str(row['Date']).strip()
                g.add((article_uri, hasDate, Literal(date_str, datatype=XSD.dateTime)))
            
            if pd.notna(row.get('Article')):
                content = str(row['Article']).strip()
                # Truncate very long content
                if len(content) > 10000:
                    content = content[:10000] + "..."
                g.add((article_uri, hasContent, Literal(content)))
            
            # Create Publisher if exists
            if pd.notna(row.get('Publisher')):
                pub_name = str(row['Publisher']).strip()
                if pub_name and pub_name.lower() != 'nan':
                    pub_id = sanitize_uri(pub_name)
                    publisher_uri = NAS_DATA[f"publisher_{pub_id}"]
                    
                    if pub_id not in publishers_created:
                        g.add((publisher_uri, RDF.type, Publisher))
                        g.add((publisher_uri, publisherName, Literal(pub_name)))
                        g.add((publisher_uri, RDFS.label, Literal(pub_name, lang="en")))
                        publishers_created.add(pub_id)
                    
                    g.add((article_uri, hasPublisher, publisher_uri))
            
            # Create Author if exists
            if pd.notna(row.get('Author')):
                auth_name = str(row['Author']).strip()
                if auth_name and auth_name.lower() != 'nan':
                    auth_id = sanitize_uri(auth_name)
                    author_uri = NAS_DATA[f"author_{auth_id}"]
                    
                    if auth_id not in authors_created:
                        g.add((author_uri, RDF.type, Author))
                        g.add((author_uri, authorName, Literal(auth_name)))
                        g.add((author_uri, RDFS.label, Literal(auth_name, lang="en")))
                        authors_created.add(auth_id)
                    
                    g.add((article_uri, hasAuthor, author_uri))
            
            # Create Summary instance if any summary exists
            summaries = []
            if pd.notna(row.get('Lsa_summary')):
                summaries.append(('LSA', row['Lsa_summary']))
            if pd.notna(row.get('Luhn_summary')):
                summaries.append(('Luhn', row['Luhn_summary']))
            if pd.notna(row.get('Textrank_summary')):
                summaries.append(('Textrank', row['Textrank_summary']))
            if pd.notna(row.get('Lexrank_summary')):
                summaries.append(('Lexrank', row['Lexrank_summary']))
            
            if summaries:
                summary_uri = NAS_DATA[f"summary_{idx}"]
                g.add((summary_uri, RDF.type, Summary))
                g.add((article_uri, hasSummary, summary_uri))
                
                for summary_type, summary_text in summaries:
                    if summary_text and str(summary_text).strip():
                        summary_text = str(summary_text).strip()
                        if len(summary_text) > 5000:
                            summary_text = summary_text[:5000] + "..."
                        
                        if summary_type == 'LSA':
                            g.add((summary_uri, hasLsaSummary, Literal(summary_text)))
                        elif summary_type == 'Luhn':
                            g.add((summary_uri, hasLuhnSummary, Literal(summary_text)))
                        elif summary_type == 'Textrank':
                            g.add((summary_uri, hasTextrankSummary, Literal(summary_text)))
                        elif summary_type == 'Lexrank':
                            g.add((summary_uri, hasLexrankSummary, Literal(summary_text)))
        
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    print(f"\nOntology statistics:")
    print(f"  - Stocks created: {len(stocks_created)}")
    print(f"  - Publishers created: {len(publishers_created)}")
    print(f"  - Authors created: {len(authors_created)}")
    print(f"  - Total triples: {len(g)}")
    
    print(f"\nSaving ontology to {output_file}...")
    g.serialize(destination=output_file, format='xml')
    print(f"Ontology saved successfully!")
    
    return g

if __name__ == "__main__":
    import sys
    
    # Check if sample size is provided as argument
    sample_size = None
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
            print(f"Running in sample mode: processing first {sample_size} rows")
        except ValueError:
            print("Invalid sample size, processing all data")
    
    build_ontology('nasdaq_dec2023.csv', 'nasdaq_ontology.owl', sample_size=sample_size)

