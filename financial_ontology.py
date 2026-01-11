"""
Financial Knowledge Graph Ontology based on FinReflectKG dataset.
Based on: https://huggingface.co/datasets/domyn/FinReflectKG

This module defines the ontology for representing financial knowledge graphs
extracted from SEC filings and other financial documents.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import enum
from ontology import ProvableFact

# --- FinReflectKG Entity Types ---
class EntityTypeEnum(str, enum.Enum):
    """
    Entity types from FinReflectKG dataset.
    Based on: https://huggingface.co/datasets/domyn/FinReflectKG#entity-types
    """
    ORG = "ORG"  # Filing Company (public company subject of 10-K filing)
    ORG_GOV = "ORG_GOV"  # Government bodies (e.g., United States Government)
    ORG_REG = "ORG_REG"  # Regulatory bodies (e.g., SEC, Federal Reserve, ECB)
    GPE = "GPE"  # Countries, states, or cities (geographic operations/risks)
    PERSON = "PERSON"  # Key individuals (e.g., CEO, CFO)
    COMP = "COMP"  # External companies (competitors, suppliers, customers, partners)
    PRODUCT = "PRODUCT"  # Products or services (e.g., iPhone, AWS)
    EVENT = "EVENT"  # Material events (pandemics, natural disasters, M&A)
    SECTOR = "SECTOR"  # Sectors or industries (e.g., Technology, Healthcare)
    ECON_IND = "ECON_IND"  # Economic indicators (Inflation Rate, GDP Growth, etc.)
    FIN_INST = "FIN_INST"  # Financial instruments (bonds, derivatives, options)
    FIN_MARKET = "FIN_MARKET"  # Financial indices (S&P 500, Dow Jones)
    CONCEPT = "CONCEPT"  # Abstract concepts (AI, Digital Transformation)
    RAW_MATERIAL = "RAW_MATERIAL"  # Essential raw materials (e.g., Lithium)
    LOGISTICS = "LOGISTICS"  # Supply chain entities (e.g., Ports)
    ACCOUNTING_POLICY = "ACCOUNTING_POLICY"  # Accounting policies (revenue recognition, etc.)
    RISK_FACTOR = "RISK_FACTOR"  # Documented risks (market risk, cybersecurity, etc.)
    LITIGATION = "LITIGATION"  # Legal disputes or proceedings
    SEGMENT = "SEGMENT"  # Business segments (Cloud segment, North America retail)
    FIN_METRIC = "FIN_METRIC"  # Financial metrics (Net Income, EBITDA, CapEx)
    ESG_TOPIC = "ESG_TOPIC"  # ESG themes (Carbon Emissions, DEI, Renewable Energy)
    MACRO_CONDITION = "MACRO_CONDITION"  # Macroeconomic trends (Recession, Inflation)
    REGULATORY_REQUIREMENT = "REGULATORY_REQUIREMENT"  # Regulations (Basel III, SEC rules, GDPR)
    COMMENTARY = "COMMENTARY"  # Management statements (outlooks, explanations, guidance)

# --- FinReflectKG Relationship Types ---
class RelationshipTypeEnum(str, enum.Enum):
    """
    Relationship types from FinReflectKG dataset.
    Based on: https://huggingface.co/datasets/domyn/FinReflectKG#relationship-types
    """
    HAS_STAKE_IN = "Has_Stake_In"  # Ownership or equity interest
    ANNOUNCES = "Announces"  # Publicly discloses or communicates
    OPERATES_IN = "Operates_In"  # Operational geography or market presence
    INTRODUCES = "Introduces"  # Rolls out new product, policy, or segment
    PRODUCES = "Produces"  # Manufactures or develops product/service
    REGULATES = "Regulates"  # Exerts control or regulatory oversight
    INVOLVED_IN = "Involved_In"  # Direct involvement in event (M&A, litigation)
    IMPACTED_BY = "Impacted_By"  # Materially affected by major event
    IMPACTS = "Impacts"  # Broad influence or effect
    POSITIVELY_IMPACTS = "Positively_Impacts"  # Contributes to positive outcomes
    NEGATIVELY_IMPACTS = "Negatively_Impacts"  # Contributes to adverse outcomes
    RELATED_TO = "Related_To"  # General connection or relationship
    MEMBER_OF = "Member_Of"  # Formal affiliation or group membership
    INVESTS_IN = "Invests_In"  # Allocates financial or strategic capital
    INCREASES = "Increases"  # Growth or rise in value/activity
    DECREASES = "Decreases"  # Decline in value/activity
    DEPENDS_ON = "Depends_On"  # Requires support or shows reliance
    CAUSES_SHORTAGE_OF = "Causes_Shortage_Of"  # Supply constraint driven by event
    AFFECTS_STOCK = "Affects_Stock"  # Direct influence on stock price/valuation
    STOCK_DECLINE_DUE_TO = "Stock_Decline_Due_To"  # Factor causing stock price drop
    STOCK_RISE_DUE_TO = "Stock_Rise_Due_To"  # Factor causing stock price increase
    MARKET_REACTS_TO = "Market_Reacts_To"  # Market response to external events
    DISCLOSES = "Discloses"  # Reveals or reports
    FACES = "Faces"  # Encounters legal or regulatory challenges
    GUIDES_ON = "Guides_On"  # Provides management commentary or forecast
    COMPLIES_WITH = "Complies_With"  # Meets regulatory or policy requirements
    SUBJECT_TO = "Subject_To"  # Governed or affected by
    SUPPLIES = "Supplies"  # Vendor or supplier relationship
    PARTNERS_WITH = "Partners_With"  # Formal or strategic collaboration

# --- Financial Knowledge Graph Models (FinReflectKG) ---
class EntityModel(BaseModel):
    """Represents a financial entity in the knowledge graph."""
    name: ProvableFact = Field(..., description="Normalized entity name (e.g., 'aapl', 'Apple Inc.')")
    entity_type: EntityTypeEnum = Field(..., description="Type of entity (ORG, PERSON, COMP, etc.)")

class RelationshipModel(BaseModel):
    """Represents a relationship type in the knowledge graph."""
    relationship: RelationshipTypeEnum = Field(..., description="Type of relationship (e.g., 'Discloses', 'Operates_In')")
    evidence: Optional[ProvableFact] = Field(None, description="Evidence text supporting the relationship extraction")

class TemporalInfoModel(BaseModel):
    """
    Temporal information for relationships.
    Dates are in "Month YYYY" format (e.g., "January 2024").
    """
    start_date: Optional[str] = Field(None, description="Relationship start date in 'Month YYYY' format or 'default_start_timestamp'")
    end_date: Optional[str] = Field(None, description="Relationship end date in 'Month YYYY' format or 'default_end_timestamp'")
    extraction_type: str = Field("default", description="'extracted' if both dates extracted, 'default' otherwise")

class FinancialTripletModel(BaseModel):
    """
    A single financial knowledge graph triplet following FinReflectKG format.
    Represents a structured fact: (entity, relationship, target)
    """
    triplet_id: Optional[str] = Field(None, description="Unique identifier for the triplet")
    entity: EntityModel = Field(..., description="Source entity of the relationship")
    relationship: RelationshipModel = Field(..., description="Relationship type")
    target: EntityModel = Field(..., description="Target entity of the relationship")
    temporal_info: Optional[TemporalInfoModel] = Field(None, description="Temporal validity of the relationship")
    chunk_text: Optional[str] = Field(None, description="Full text context surrounding the triplet")
    chunk_id: Optional[str] = Field(None, description="Text chunk identifier")
    page_id: Optional[str] = Field(None, description="Source document page identifier")

class DocumentMetadataModel(BaseModel):
    """Metadata about the source document for a triplet."""
    ticker: Optional[str] = Field(None, description="Company ticker symbol (e.g., 'aapl', 'msft')")
    year: Optional[int] = Field(None, description="Filing year")
    source_file: Optional[str] = Field(None, description="Original PDF filename")
    page_id: Optional[str] = Field(None, description="PDF page identifier")
    chunk_id: Optional[str] = Field(None, description="Text chunk identifier")

class FinancialKnowledgeGraphData(BaseModel):
    """
    Top-level schema for extracting financial knowledge graph data.
    Can represent single triplets or collections of triplets from financial documents.
    """
    triplets: List[FinancialTripletModel] = Field(default_factory=list, description="List of extracted triplets")
    document_metadata: Optional[DocumentMetadataModel] = Field(None, description="Source document information")
    
    def add_triplet(self, triplet: FinancialTripletModel) -> None:
        """Helper method to add a triplet to the collection."""
        self.triplets.append(triplet)
    
    def get_triplets_by_entity_type(self, entity_type: EntityTypeEnum) -> List[FinancialTripletModel]:
        """Filter triplets by entity type (either source or target)."""
        return [
            t for t in self.triplets 
            if t.entity.entity_type == entity_type or t.target.entity_type == entity_type
        ]
    
    def get_triplets_by_relationship(self, relationship: RelationshipTypeEnum) -> List[FinancialTripletModel]:
        """Filter triplets by relationship type."""
        return [t for t in self.triplets if t.relationship.relationship == relationship]
    
    def get_triplets_by_ticker(self, ticker: str) -> List[FinancialTripletModel]:
        """Filter triplets by company ticker symbol."""
        if not self.document_metadata or not self.document_metadata.ticker:
            return []
        if self.document_metadata.ticker.lower() == ticker.lower():
            return self.triplets
        return []

