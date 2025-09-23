from typing import List
from langchain.docstore.document import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_docking_knowledge_base() -> List[Document]:
    """Create documents containing knowledge about molecular docking parameters."""
    documents = [
        Document(
            page_content="""
            Exhaustiveness parameter in molecular docking:
            - Range: 1-32
            - Default: 8
            - Low (1-4): Quick preliminary docking
            - Medium (8-16): Standard docking runs
            - High (24-32): Deep search for complex binding sites
            Keywords: quick, fast, thorough, deep, extensive
            """,
            metadata={"param": "exhaustiveness"}
        ),
        Document(
            page_content="""
            Search space size parameters in molecular docking:
            - size_x, size_y, size_z define the search box dimensions
            - Typical ranges: 15-30 Angstroms
            - Small pockets: 15x15x15
            - Medium pockets: 20x20x20
            - Large cavities: 25x25x25 or larger
            Keywords: pocket, cavity, binding site, large, small
            """,
            metadata={"param": "size"}
        ),
        Document(
            page_content="""
            Center coordinates in molecular docking:
            - center_x, center_y, center_z define the search box center
            - Based on known binding site location
            - Can be derived from crystal structure ligand position
            - Often near key residues or cavities
            Keywords: active site, binding site, pocket, cavity, coordinates
            """,
            metadata={"param": "center"}
        ),
        Document(
            page_content="""
            Common docking scenarios:
            1. Active site docking:
            - Known binding pocket
            - Often near catalytic residues
            - Medium search space (20x20x20)
            - Higher exhaustiveness (16+)
            
            2. Blind docking:
            - Unknown binding site
            - Large search space
            - Standard exhaustiveness (8)
            
            3. Refined docking:
            - Small search space
            - Known pocket
            - High exhaustiveness (24+)
            """,
            metadata={"param": "scenarios"}
        ),
    ]
    return documents

def initialize_vector_store():
    """Initialize and populate the MongoDB Atlas Vector Store."""
    # Create MongoDB client
    client = MongoClient(
        os.environ['MONGODB_URI'],
        appname="docking_agent_init"
    )
    
    # Get collection
    collection = client.get_database(os.environ['MONGODB_DB']).get_collection(
        os.environ['MONGODB_VECTOR_COLL']
    )
    
    # Create documents
    documents = create_docking_knowledge_base()
    
    # Initialize vector store
    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=documents,
        embedding=OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY']),
        collection=collection,
        index_name=os.environ['MONGODB_VECTOR_INDEX']
    )
    
    print(f"Successfully initialized vector store with {len(documents)} documents")
    return vector_store

if __name__ == "__main__":
    initialize_vector_store()
