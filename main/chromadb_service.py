"""
ChromaDB service for vector database operations
"""
import chromadb
from chromadb.config import Settings
from django.conf import settings
import os


class ChromaDBService:
    """Service class for ChromaDB operations"""
    
    _client = None
    _collection = None
    
    @classmethod
    def get_client(cls):
        """Get or create ChromaDB client"""
        if cls._client is None:
            db_path = str(settings.CHROMA_DB_PATH)
            # Create directory if it doesn't exist
            os.makedirs(db_path, exist_ok=True)
            
            cls._client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return cls._client
    
    @classmethod
    def get_collection(cls, collection_name=None):
        """Get or create a collection"""
        if collection_name is None:
            collection_name = settings.CHROMA_COLLECTION_NAME
        
        if cls._collection is None or cls._collection.name != collection_name:
            client = cls.get_client()
            try:
                cls._collection = client.get_collection(name=collection_name)
            except:
                cls._collection = client.create_collection(name=collection_name)
        
        return cls._collection
    
    @classmethod
    def add_documents(cls, documents, ids=None, metadatas=None, embeddings=None):
        """Add documents to the collection"""
        collection = cls.get_collection()
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    @classmethod
    def query(cls, query_texts=None, n_results=10, where=None, where_document=None, include=None):
        """Query the collection"""
        collection = cls.get_collection()
        query_params = {
            "n_results": n_results,
        }
        if query_texts:
            query_params["query_texts"] = query_texts
        if where:
            query_params["where"] = where
        if where_document:
            query_params["where_document"] = where_document
        if include:
            query_params["include"] = include
        return collection.query(**query_params)
    
    @classmethod
    def get_all(cls, ids=None, where=None, limit=None, offset=None, include=None):
        """Get all documents from the collection"""
        collection = cls.get_collection()
        return collection.get(
            ids=ids,
            where=where,
            limit=limit,
            offset=offset,
            include=include
        )
    
    @classmethod
    def delete(cls, ids=None, where=None):
        """Delete documents from the collection"""
        collection = cls.get_collection()
        collection.delete(ids=ids, where=where)
    
    @classmethod
    def update(cls, ids, documents=None, metadatas=None, embeddings=None):
        """Update documents in the collection"""
        collection = cls.get_collection()
        collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    @classmethod
    def reset(cls):
        """Reset the ChromaDB client (for testing)"""
        cls._client = None
        cls._collection = None
