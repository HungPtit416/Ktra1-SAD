"""
RAG Engine - Simplified version using TF-IDF instead of embeddings
For lightweight, CPU-friendly deployment
"""

import os
import json
import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Lightweight RAG system using TF-IDF for fast deployment
    """
    
    def __init__(self):
        """Khởi tạo RAG Engine"""
        try:
            self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            self.documents = []
            self.vectors = None
            self.kb_data = {}
            
            # RAG config
            self.chunk_size = settings.RAG_CONFIG.get('chunk_size', 500)
            self.top_k_retrieval = settings.RAG_CONFIG.get('top_k_retrieval', 5)
            
            logger.info("✅ RAG Engine initialized (TF-IDF mode)")
        except Exception as e:
            logger.error(f"Error initializing RAG Engine: {str(e)}")
            raise
    
    def add_documents_to_kb(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Knowledge Base"""
        try:
            for doc in documents:
                # Tách nội dung thành chunks
                chunks = self._chunk_text(doc['content'])
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc['id']}_chunk_{i}"
                    
                    self.documents.append(chunk)
                    self.kb_data[chunk_id] = {
                        'content': chunk,
                        'source_id': doc['id'],
                        'source_title': doc.get('title', ''),
                        'chunk_index': i,
                        'metadata': doc.get('metadata', {})
                    }
            
            # Train vectorizer
            if len(self.documents) > 0:
                self.vectors = self.vectorizer.fit_transform(self.documents)
            
            logger.info(f"✅ Added {len(documents)} documents to KB")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Truy xuất context từ KB với query type detection"""
        # Lazy load KB from database on first retrieval
        if len(self.documents) == 0:
            self._load_kb_from_db()
        
        if top_k is None:
            top_k = self.top_k_retrieval
        
        try:
            if self.vectors is None or len(self.documents) == 0:
                logger.warning("No documents in RAG engine")
                return []
            
            # Detect query type BEFORE expansion
            query_type = self._detect_query_type(query)
            
            # Vectorize original query (not expanded - simpler approach)
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarity
            similarities = cosine_similarity(query_vector, self.vectors)[0]
            
            # Get top-k results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            query_lower = query.lower()
            is_phone_query = any(term in query_lower for term in ['điện thoại', 'mobile', 'phone', 'smartphone', 'iphone', 'samsung', 'xiaomi', 'vivo', 'oppo'])
            is_laptop_query = any(term in query_lower for term in ['laptop', 'máy tính', 'computer', 'notebook'])
            is_game_phone_query = is_phone_query and any(term in query_lower for term in ['game', 'chơi', 'gaming', 'mượt'])
            
            retrieved_docs = []
            for idx in top_indices:
                # Dynamic threshold: phones = 0.10, laptops = 0.10, games = 0.08
                min_threshold = 0.08 if is_game_phone_query else 0.10
                if similarities[idx] < min_threshold:
                    continue
                    
                doc_data = self.kb_data.get(list(self.kb_data.keys())[idx], {})
                doc_title = doc_data.get('source_title', '').lower()
                doc_content = self.documents[idx].lower()
                doc_category = str(doc_data.get('metadata', {}).get('category', '')).lower()
                
                # STRICT category matching to avoid cross-category contamination
                phone_keywords = {'điện thoại', 'mobile', 'phone', 'smartphone', 'iphone', 'samsung', 'xiaomi', 'vivo', 'oppo', 'realme', 'motorola', 'google'}
                laptop_keywords = {'laptop', 'máy tính', 'notebook', 'dell', 'asus', 'hp', 'lenovo', 'macbook', 'computer', 'msi', 'razer'}
                
                # Get dominant category from doc
                has_phone_term = any(term in doc_title + doc_category for term in phone_keywords)
                has_laptop_term = any(term in doc_title + doc_category for term in laptop_keywords)
                
                # STRICT filter: reject if category completely mismatches
                if is_phone_query and has_laptop_term and not has_phone_term:
                    continue  # User wants phone, but doc is clearly laptop
                if is_laptop_query and has_phone_term and not has_laptop_term:
                    continue  # User wants laptop, but doc is clearly phone
                
                # Boost confidence if category matches
                final_similarity = similarities[idx]
                if is_phone_query and has_phone_term:
                    final_similarity = min(similarities[idx] * 1.15, 1.0)  # Boost matching phones
                if is_laptop_query and has_laptop_term:
                    final_similarity = min(similarities[idx] * 1.15, 1.0)  # Boost matching laptops
                if is_game_phone_query and has_phone_term and any(g in query_lower for g in ['game', 'gaming']):
                    final_similarity = min(similarities[idx] * 1.2, 1.0)  # Extra boost for gaming phones
                
                # Append to results (moved OUTSIDE all conditionals)
                retrieved_docs.append({
                    'content': self.documents[idx],
                    'source_id': doc_data.get('source_id'),
                    'source_title': doc_data.get('source_title'),
                    'similarity_score': float(final_similarity),
                    'metadata': doc_data.get('metadata', {}),
                    'query_type': query_type
                })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents for query: '{query}' (type: {query_type})")
            return retrieved_docs
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def _expand_query(self, query: str) -> str:
        """Expand query with context-specific keywords for better retrieval"""
        query_lower = query.lower()
        expanded = query
        
        # Gaming-related expansion
        if 'gaming' in query_lower or 'game' in query_lower:
            expanded += " RTX GPU 165Hz refresh rate tản nhiệt performance"
        
        # Programming-related expansion
        elif 'lập trình' in query_lower or 'code' in query_lower or 'developer' in query_lower:
            expanded += " RAM CPU SSD bàn phím editor IDE"
        
        # Design/Video editing expansion
        elif 'design' in query_lower or 'video' in query_lower or 'edit' in query_lower:
            expanded += " màn hình 4K color accuracy RAM SSD render"
        
        # Budget-focused expansion
        if 'dưới' in query_lower or 'rẻ' in query_lower or 'giá thấp' in query_lower:
            expanded += " giá tốt nhất budget"
        
        # Premium expansion
        if 'premium' in query_lower or 'cao cấp' in query_lower or 'tốt nhất' in query_lower:
            expanded += " performance hiệu suất cao đỉnh professional"
        
        return expanded
    
    def _detect_query_type(self, query: str) -> str:
        """Detect query type for smart recommendations"""
        query_lower = query.lower()
        
        if 'gaming' in query_lower or 'game' in query_lower:
            return 'gaming'
        elif 'lập trình' in query_lower or 'code' in query_lower or 'developer' in query_lower:
            return 'programming'
        elif 'design' in query_lower or 'video' in query_lower or 'edit' in query_lower:
            return 'design'
        elif 'student' in query_lower or 'sinh viên' in query_lower or 'học sinh' in query_lower:
            return 'student'
        elif 'nomad' in query_lower or 'portable' in query_lower or 'di động' in query_lower:
            return 'portable'
        return 'general'
    
    def _load_kb_from_db(self):
        """Load KB from database (lazy load on first use)"""
        try:
            from advisor.models import KnowledgeBase
            
            kb_documents = KnowledgeBase.objects.filter(is_active=True).values('id', 'title', 'content', 'content_type')
            
            if not kb_documents.exists():
                logger.warning("⚠️ No active KB documents found in database")
                return False
            
            docs_to_add = [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'metadata': {'content_type': doc['content_type']}
                }
                for doc in kb_documents
            ]
            
            success = self.add_documents_to_kb(docs_to_add)
            if success:
                logger.info(f"📚 Loaded {len(docs_to_add)} KB documents from database")
            return success
        except Exception as e:
            logger.error(f"Error loading KB from database: {str(e)}")
            return False
    
    def generate_response(self, query: str, session_context: List[Dict] = None) -> Dict[str, Any]:
        """Generate response using RAG"""
        try:
            # Retrieve context
            retrieved_context = self.retrieve_context(query)
            
            if not retrieved_context:
                return {
                    'answer': 'Xin lỗi, tôi không có thông tin về nhu cầu này. Vui lòng liên hệ hỗ trợ.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Format context
            context_text = self._format_context(retrieved_context)
            
            # Generate response using template
            answer = self._generate_template_answer(query, context_text, retrieved_context)
            
            # Calculate confidence
            confidence = np.mean([doc['similarity_score'] for doc in retrieved_context[:3]])
            
            # Extract sources
            sources = [
                {
                    'title': doc['source_title'],
                    'similarity': float(doc['similarity_score'])
                }
                for doc in retrieved_context[:3]
            ]
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': float(confidence)
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'answer': 'Lỗi hệ thống. Vui lòng thử lại sau.',
                'sources': [],
                'confidence': 0.0
            }
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks if chunks else [text]
    
    def _format_context(self, retrieved_docs: List[Dict]) -> str:
        """Format context from documents - ultra-concise (80 chars max)"""
        if not retrieved_docs:
            return ""
        
        # Only show top 1 document
        doc = retrieved_docs[0]
        content = doc['content'].strip()
        
        # Extreme limit: 80 characters max
        if len(content) > 80:
            truncated = content[:80]
            last_space = truncated.rfind(' ')
            if last_space > 20:
                content = truncated[:last_space]
            else:
                content = truncated
        
        return content
    
    def _generate_template_answer(self, query: str, context: str, docs: List[Dict]) -> str:
        """Generate smart answer based on query type with specific recommendations"""
        if not context:
            return "Không có thông tin phù hợp."
        
        # Get query type from first doc if available
        query_type = docs[0].get('query_type', 'general') if docs else 'general'
        query_lower = query.lower()
        
        # Filter out generic/brand-analysis responses if they exist
        content_lower = context.lower()
        is_generic = any(phrase in content_lower for phrase in [
            'phân tích brand', 'top trend', 'ecosystem', 'hệ sinh thái'
        ])
        
        if is_generic and len(docs) > 1:
            # Try to find a more specific document
            for doc in docs[1:]:
                specific_content = doc['content'].lower()
                if not any(p in specific_content for p in ['phân tích brand', 'top trend', 'ecosystem']):
                    context = doc['content']
                    break
        
        # *** NEW: Phone Gaming - Dành riêng ***
        is_phone_game_query = ('điện thoại' in query_lower or 'phone' in query_lower) and any(g in query_lower for g in ['game', 'chơi', 'gaming', 'mượt'])
        if is_phone_game_query:
            return f"{context}\n\n🎮 Dành cho Gaming Mobile: Snapdragon 7-8 Gen+, 120Hz+, RAM 8GB+, pin bền, tản nhiệt tốt."
        
        # Gaming recommendations
        if query_type == 'gaming' or 'gaming' in query_lower or 'game' in query_lower:
            return f"{context}\n\n💎 Dành cho Gaming: Ưu tiên RTX (4060+), CPU mạnh, refresh rate 144Hz+, tản nhiệt tốt."
        
        # Programming recommendations
        elif query_type == 'programming' or 'lập trình' in query_lower or 'code' in query_lower:
            return f"{context}\n\n💻 Dành cho Lập trình: CPU nhanh (i7/Ryzen 7), RAM 16GB, SSD 512GB+, bàn phím tốt."
        
        # Design/Video editing
        elif query_type == 'design' or 'design' in query_lower or 'video' in query_lower:
            return f"{context}\n\n🎨 Dành cho Design/Video: Màn hình color-accurate, RAM 16GB+, GPU cao, SSD nhanh."
        
        # Student budget-conscious
        elif query_type == 'student' or 'sinh viên' in query_lower or 'học sinh' in query_lower:
            return f"{context}\n\n📚 Dành cho Sinh viên: Đủ xử lý lập trình, browsing, văn bản. Budget 14-18 triệu."
        
        # Portable/nomad
        elif query_type == 'portable' or 'portable' in query_lower or 'di động' in query_lower:
            return f"{context}\n\n✈️ Dành cho Nomad: Nhẹ <1.4kg, pin 12h+, sạc nhanh, cổng USB-C đa năng."
        
        # Phone-specific queries
        elif 'điện thoại' in query_lower or 'phone' in query_lower or 'camera' in query_lower:
            return f"{context}\n\n📱 Điểm mạnh: Camera chất lượng cao, pin bền, hiệu suất ổn định."
        
        # Price/Budget queries
        elif any(word in query_lower for word in ['dưới', 'rẻ', 'giá', 'triệu', 'budget']):
            return f"{context}\n\n💰 Lựa chọn tối ưu: Cân bằng giá - hiệu năng - chất lượng."
        
        # Default - just return context
        else:
            return context
    
    def update_kb_from_db(self):
        """Update KB from database"""
        try:
            from advisor.models import KnowledgeBase
            
            kb_docs = KnowledgeBase.objects.filter(is_active=True).values(
                'id', 'title', 'content', 'content_type', 'tags'
            )
            
            documents = []
            for doc in kb_docs:
                documents.append({
                    'id': str(doc['id']),
                    'title': doc['title'],
                    'content': doc['content'],
                    'metadata': {
                        'content_type': doc['content_type'],
                        'tags': doc.get('tags', [])
                    }
                })
            
            self.add_documents_to_kb(documents)
            logger.info(f"✅ Updated KB with {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error updating KB: {str(e)}")
            return False
