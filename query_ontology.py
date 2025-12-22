"""
Helper script to query and explore the built ontology.
"""

from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.namespace import OWL

# Define namespaces (must match build_ontology.py)
NAS = Namespace("http://example.org/nasdaq/ontology#")
NAS_DATA = Namespace("http://example.org/nasdaq/data#")

def load_ontology(owl_file='nasdaq_ontology.owl'):
    """Load the ontology from OWL file"""
    g = Graph()
    g.parse(owl_file, format='xml')
    return g

def get_all_stocks(g):
    """Get all stock symbols from the ontology"""
    stocks = []
    for stock_uri, _, _ in g.triples((None, RDF.type, NAS.Stock)):
        symbol = g.value(stock_uri, NAS.hasSymbol, None)
        if symbol:
            stocks.append((str(stock_uri), str(symbol)))
    return stocks

def get_stock_articles(g, stock_symbol):
    """Get all articles for a specific stock symbol"""
    # Find the stock URI
    stock_uri = None
    for s, _, _ in g.triples((None, NAS.hasSymbol, None)):
        if str(g.value(s, NAS.hasSymbol, None)) == stock_symbol:
            stock_uri = s
            break
    
    if not stock_uri:
        return []
    
    # Get all articles for this stock
    articles = []
    for _, _, article_uri in g.triples((stock_uri, NAS.hasArticle, None)):
        title = g.value(article_uri, NAS.hasTitle, None)
        date = g.value(article_uri, NAS.hasDate, None)
        url = g.value(article_uri, NAS.hasUrl, None)
        articles.append({
            'uri': str(article_uri),
            'title': str(title) if title else None,
            'date': str(date) if date else None,
            'url': str(url) if url else None
        })
    return articles

def get_ontology_stats(g):
    """Get statistics about the ontology"""
    stats = {
        'stocks': len(list(g.triples((None, RDF.type, NAS.Stock)))),
        'articles': len(list(g.triples((None, RDF.type, NAS.Article)))),
        'summaries': len(list(g.triples((None, RDF.type, NAS.Summary)))),
        'publishers': len(list(g.triples((None, RDF.type, NAS.Publisher)))),
        'authors': len(list(g.triples((None, RDF.type, NAS.Author)))),
        'total_triples': len(g)
    }
    return stats

def print_stock_info(g, stock_symbol):
    """Print detailed information about a stock"""
    print(f"\n=== Stock: {stock_symbol} ===")
    
    # Find stock
    stock_uri = None
    for s, _, _ in g.triples((None, NAS.hasSymbol, None)):
        if str(g.value(s, NAS.hasSymbol, None)) == stock_symbol:
            stock_uri = s
            break
    
    if not stock_uri:
        print(f"Stock {stock_symbol} not found in ontology")
        return
    
    # Get articles
    articles = get_stock_articles(g, stock_symbol)
    print(f"Number of articles: {len(articles)}")
    
    # Show first 5 articles
    print("\nFirst 5 articles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n  {i}. {article['title']}")
        if article['date']:
            print(f"     Date: {article['date']}")
        if article['url']:
            print(f"     URL: {article['url'][:80]}...")

if __name__ == "__main__":
    import sys
    
    print("Loading ontology...")
    g = load_ontology()
    
    print("\n=== Ontology Statistics ===")
    stats = get_ontology_stats(g)
    for key, value in stats.items():
        print(f"{key.capitalize()}: {value}")
    
    print("\n=== Sample Stock Symbols ===")
    stocks = get_all_stocks(g)
    print(f"Total stocks: {len(stocks)}")
    print("\nFirst 10 stock symbols:")
    for uri, symbol in stocks[:10]:
        print(f"  - {symbol}")
    
    # If stock symbol provided as argument, show details
    if len(sys.argv) > 1:
        stock_symbol = sys.argv[1]
        print_stock_info(g, stock_symbol)
    else:
        print("\nTo see details for a specific stock, run:")
        print("  python query_ontology.py <STOCK_SYMBOL>")
        print("\nExample: python query_ontology.py AAPL")

