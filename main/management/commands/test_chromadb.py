"""
Management command to test ChromaDB connection
"""
from django.core.management.base import BaseCommand
from main.chromadb_service import ChromaDBService


class Command(BaseCommand):
    help = 'Test ChromaDB connection and basic operations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing ChromaDB connection...'))
        
        try:
            # Test client connection
            client = ChromaDBService.get_client()
            self.stdout.write(self.style.SUCCESS('[OK] ChromaDB client connected'))
            
            # Test collection creation/retrieval
            collection = ChromaDBService.get_collection()
            self.stdout.write(self.style.SUCCESS(f'[OK] Collection "{collection.name}" ready'))
            
            # Test adding a document
            test_doc = ["This is a test document for ChromaDB"]
            test_ids = ["test_1"]
            test_metadata = [{"source": "test", "type": "sample"}]
            
            ChromaDBService.add_documents(
                documents=test_doc,
                ids=test_ids,
                metadatas=test_metadata
            )
            self.stdout.write(self.style.SUCCESS('[OK] Document added successfully'))
            
            # Test querying
            results = ChromaDBService.query(query_texts=["test"], n_results=1, include=['documents', 'metadatas'])
            self.stdout.write(self.style.SUCCESS('[OK] Query executed successfully'))
            self.stdout.write(self.style.SUCCESS(f'  Found {len(results["ids"][0])} result(s)'))
            
            # Clean up test document
            ChromaDBService.delete(ids=test_ids)
            self.stdout.write(self.style.SUCCESS('[OK] Test document deleted'))
            
            self.stdout.write(self.style.SUCCESS('\n[SUCCESS] ChromaDB is working correctly!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Error: {str(e)}'))
            raise
