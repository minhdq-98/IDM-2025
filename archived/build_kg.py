#!/usr/bin/env python
# coding: utf-8

# # Concatennate relevant information

# In[1]:


import numpy as np
import pandas as pd


# In[19]:


df = pd.read_csv("nasdaq_100.csv")
df['Date'] = pd.to_datetime(df['Date'])
df_filtered = df[(df['Date'].dt.date == pd.to_datetime('2023-12-01 00:00:00+00:00').date()) & (df['Stock_symbol'] == 'AAPL')]
df_filtered = df_filtered.drop(['Lsa_summary', 'Luhn_summary', 'Textrank_summary'], axis=1)
df_filtered


# In[99]:


def join_string(item):
    Date, Article_title, Stock_symbol, Lexrank_summary = item
    final_string = ""

    # Check if column has a unique value
    if pd.notna(Date):
        final_string += f"Date: {Date}"

    if pd.notna(Article_title):
        if final_string:
            final_string += " | "
        final_string += f"Article Title: {Article_title}"

    if pd.notna(Stock_symbol):
        if final_string:
            final_string += " | "
        final_string += f"Stock Symbol: {Stock_symbol}"

    if pd.notna(Lexrank_summary):
        if final_string:
            final_string += " | "
        final_string += f"Summary: {Lexrank_summary}"

    return final_string

# Apply the function to create the 'information' column
df_filtered['Information'] = df_filtered[
    ['Date', 'Article_title', 'Stock_symbol','Lexrank_summary']
].apply(join_string, axis=1)

# Group by Date and concatenate Information with newline separator
df_grouped = df_filtered.groupby('Date')['Information'].apply(lambda x: '\n'.join(x)).reset_index()


# In[100]:


sample = df_grouped.head().iloc[0]['Information']
print(sample)


# # Represent as JSON format with LLMs

# In[109]:


get_ipython().run_cell_magic('capture', '', '!pip install google-generativeai\n')


# In[123]:


import json
import os
from google import genai
from google.genai import types

# Set API key
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

def extract_entities_and_relationship(text):
    prompt = (
        f"Extract a high-fidelity Knowledge Graph (entities and relationships) from the following financial news. "
        f"Focus on capturing causal links, market movements, and corporate actions.\n\n"

        f"ENTITY TYPES TO USE:\n"
        f"- Organization (Companies, Banks, Regulatory Bodies like 'Fed' or 'EU')\n"
        f"- Person (Executives, Analysts, Chairs)\n"
        f"- FinancialMetric (Specific figures: 'Revenue: $55B', 'Stock Price: $189.95', 'Gain: 9.29%')\n"
        f"- Product_Service (e.g., 'Apple TV+', 'Safari', 'Streaming Bundle')\n"
        f"- MarketIndex (e.g., 'S&P 500', 'Nasdaq', 'Dow')\n"
        f"- Event (e.g., 'Santa Rally', 'Legal Appeal', 'Rate Hike')\n"
        f"Add more ENTITY TYPES if necessary.\n\n"

        f"RELATIONSHIP TYPES TO USE:\n"
        f"- REPORTS_METRIC (Organization -> FinancialMetric)\n"
        f"- COMPETES_WITH (Organization -> Organization)\n"
        f"- PARTNERED_WITH (Organization -> Organization)\n"
        f"- SUBJECT_TO (Organization -> Event/RegulatoryBody)\n"
        f"- INFLUENCES (Event/Person -> MarketIndex/Organization)\n"
        f"- OWNS_PRODUCT (Organization -> Product_Service)\n"
        f"Add more RELATIONSHIP TYPES if necessary.\n\n"

        f"IMPORTANT INSTRUCTIONS:\n"
        f"1. Preserve ALL numerical figures and dates exactly.\n"
        f"2. Keep ALL dates in their original format.\n"

        f"Return a JSON object:\n"
        f"{{\n"
        f"  \"entities\": [{{ \"name\": \"...\", \"type\": \"...\" }}],\n"
        f"  \"relationships\": [\n"
        f"    {{ \"source\": \"...\", \"relationship\": \"...\", \"target\": \"...\", \"date\": \"...\" //if mentioned (optional)}}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Text:\n{text}"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)
    return result

# Apply to data
result = extract_entities_and_relationship(sample)
print(json.dumps(result, indent=2))


# # Represent in Knowledge Graph

# In[108]:


get_ipython().run_cell_magic('capture', '', '!pip install -U langchain-neo4j\n')


# In[95]:

import os
from langchain_neo4j import Neo4jGraph


NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

graph = Neo4jGraph(
    url=NEO4J_URL,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE
)


# In[119]:


# Helper function for kg
def cypher_string(s):
    if not isinstance(s, str):
        s = str(s)
    return s.replace("'", "\\'")


# In[124]:


for entity in result.get('entities', []):
    name = cypher_string(entity['name'])
    props = [f"name: '{name}'"]
    props.append(f"{}")


# In[136]:


def add_to_kg(kg, json_data):
    with kg._driver.session() as session:
        for entity in json_data.get('entities', []):
            try:
                session.run(
                    "MERGE (e:Entity {name: $name}) "
                    "SET e.type = $type",
                    name=entity['name'], type=entity['type']
                )
            except Exception as e:
                print(f"Error in adding entity: {e}")

        for relationship in json_data.get('relationships', []):
            try:
                session.run(
                    "MATCH (a:Entity {name: $source}), (b:Entity {name: $target}) "
                    "MERGE (a)-[r:RELATED_TO]->(b) "
                    "SET r.type = $rel_type, r.date = $date",
                    source=relationship['source'], 
                    target=relationship['target'], 
                    rel_type=relationship['relationship'], 
                    date=relationship.get('date', 'N/A')       
                )
            except Exception as e:
                print(f"Error in adding relationship: {e}")


# In[137]:


add_to_kg(graph, result)


# In[129]:


get_ipython().run_cell_magic('capture', '', '!pip install pyvis\n')


# In[138]:


from pyvis.network import Network
from IPython.display import FileLink

def visualize_kg(graph_wrapper, filename="financial_graph.html"):
    query = """
    MATCH (n:Entity)-[r:RELATED_TO]->(m:Entity) 
    RETURN n.name AS source, m.name AS target, r.type AS rel_type
    """
    results = graph_wrapper.query(query)

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)

    for record in results:
        net.add_node(record['source'], label=record['source'], color="#00d4ff", title=record['source'])
        net.add_node(record['target'], label=record['target'], color="#00d4ff", title=record['target'])
        net.add_edge(record['source'], record['target'], label=record['rel_type'])

    net.save_graph(filename)
    return FileLink(filename)


# In[139]:


visualize_kg(graph)


# In[ ]:




