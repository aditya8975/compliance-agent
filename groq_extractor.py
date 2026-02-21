"""
Groq-Powered Compliance Requirement Extractor
The AI brain that understands circular meaning and extracts obligations
"""

from groq import Groq
import json
import logging
from typing import Dict, List, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import streamlit as st


class GroqComplianceExtractor:
    """Uses Groq LLM to intelligently extract compliance requirements"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Get free key from https://console.groq.com"
            )
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Current Groq free tier model (2025)
        logger.info(f"Initialized Groq extractor with model: {self.model}")
    
    def extract_requirements(self, circular: Dict, circular_text: str = "") -> Dict:
        """
        Extract compliance requirements from circular using Groq AI
        
        Args:
            circular: Circular metadata (id, title, date, category, etc.)
            circular_text: Full text of the circular
            
        Returns:
            Extracted requirements with AI analysis
        """
        try:
            logger.info(f"Extracting requirements from {circular['id']} using Groq AI...")
            
            # Prepare the prompt
            prompt = self._build_extraction_prompt(circular, circular_text)
            
            # Call Groq API (correct syntax: chat.completions, not messages)
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            extracted = self._parse_extraction_response(response_text, circular)
            
            logger.info(f"Successfully extracted requirements from {circular['id']}")
            return extracted
        
        except Exception as e:
            logger.error(f"Error extracting requirements: {str(e)}")
            return self._fallback_extraction(circular)
    
    def _build_extraction_prompt(self, circular: Dict, text: str) -> str:
        """Build the extraction prompt for Groq"""
        
        prompt = f"""You are a compliance expert analyzing a SEBI regulatory circular.

CIRCULAR INFORMATION:
Title: {circular['title']}
Date: {circular['date']}
Category: {circular['category']}
ID: {circular['id']}

CIRCULAR TEXT:
{text[:3000] if text else "Full text not available"}

TASK: Extract compliance requirements in JSON format with these fields:
1. key_obligations: List of specific things companies must do
2. deadline: When compliance is required (extract date if mentioned)
3. applicable_to: Which entities must comply (e.g., "All Listed Companies", "AMCs", "Brokers")
4. penalties: What happens if not complied
5. implementation_steps: How to implement
6. impact_level: HIGH/MEDIUM/LOW based on scope
7. affected_departments: Which departments in a company are affected

Respond ONLY with valid JSON, no other text.

Example format:
{{
    "key_obligations": ["Obligation 1", "Obligation 2"],
    "deadline": "2024-03-31",
    "applicable_to": ["All Listed Companies"],
    "penalties": ["Fine up to X", "Suspension"],
    "implementation_steps": ["Step 1", "Step 2"],
    "impact_level": "HIGH",
    "affected_departments": ["Compliance", "Legal"]
}}"""
        
        return prompt
    
    def _parse_extraction_response(self, response: str, circular: Dict) -> Dict:
        """Parse Groq response and structure it"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                extracted_data = json.loads(json_match.group(0))
            else:
                extracted_data = {}
            
            # Ensure all required fields exist
            result = {
                "circular_id": circular['id'],
                "title": circular['title'],
                "date": circular['date'],
                "category": circular['category'],
                "key_obligations": extracted_data.get('key_obligations', []),
                "deadline": extracted_data.get('deadline', self._estimate_deadline(circular['date'])),
                "applicable_to": extracted_data.get('applicable_to', self._get_default_applicable(circular['category'])),
                "penalties": extracted_data.get('penalties', []),
                "implementation_steps": extracted_data.get('implementation_steps', []),
                "impact_level": extracted_data.get('impact_level', 'MEDIUM'),
                "affected_departments": extracted_data.get('affected_departments', []),
                "ai_extracted": True
            }
            
            return result
        
        except Exception as e:
            logger.warning(f"Error parsing extraction response: {str(e)}")
            return self._fallback_extraction(circular)
    
    def _estimate_deadline(self, circular_date: str) -> str:
        """Estimate compliance deadline from circular date"""
        try:
            from datetime import datetime, timedelta
            
            # Parse date
            date_obj = datetime.strptime(circular_date, "%d-%m-%Y")
            
            # Add 30 days for compliance
            deadline = date_obj + timedelta(days=30)
            
            return deadline.strftime("%d-%m-%Y")
        except:
            return circular_date
    
    def _get_default_applicable(self, category: str) -> List[str]:
        """Get default applicable entities based on category"""
        category_mapping = {
            "Disclosure": ["All Listed Entities"],
            "Mutual Funds": ["All AMCs", "Mutual Fund Distributors"],
            "Corporate Governance": ["All Listed Companies"],
            "Market Regulation": ["All Market Participants"],
            "Brokers": ["All Registered Brokers"],
            "Depository": ["All Depositories"],
            "Risk Management": ["All Intermediaries"],
            "Compliance": ["All Regulated Entities"]
        }
        return category_mapping.get(category, ["All Market Participants"])
    
    def _fallback_extraction(self, circular: Dict) -> Dict:
        """Fallback extraction if AI fails"""
        return {
            "circular_id": circular['id'],
            "title": circular['title'],
            "date": circular['date'],
            "category": circular['category'],
            "key_obligations": ["Review circular for compliance requirements"],
            "deadline": self._estimate_deadline(circular['date']),
            "applicable_to": self._get_default_applicable(circular['category']),
            "penalties": ["Regulatory action"],
            "implementation_steps": ["Assign to compliance team", "Review requirements", "Implement changes"],
            "impact_level": "MEDIUM",
            "affected_departments": ["Compliance", "Legal"],
            "ai_extracted": False
        }
    
    def batch_extract(self, circulars: List[Dict], texts: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract requirements from multiple circulars
        
        Args:
            circulars: List of circular dictionaries
            texts: Optional list of circular texts
            
        Returns:
            List of extracted requirements
        """
        results = []
        
        for i, circular in enumerate(circulars):
            text = texts[i] if texts and i < len(texts) else ""
            extracted = self.extract_requirements(circular, text)
            results.append(extracted)
        
        return results
    
    def generate_summary(self, requirements: List[Dict]) -> str:
        """
        Generate executive summary of all requirements
        
        Args:
            requirements: List of extracted requirements
            
        Returns:
            Summary text
        """
        try:
            logger.info("Generating compliance summary...")
            
            # Count by impact level
            high_impact = sum(1 for r in requirements if r.get('impact_level') == 'HIGH')
            medium_impact = sum(1 for r in requirements if r.get('impact_level') == 'MEDIUM')
            low_impact = sum(1 for r in requirements if r.get('impact_level') == 'LOW')
            
            summary_prompt = f"""Based on these compliance requirements, generate a brief executive summary:

HIGH PRIORITY: {high_impact} items
MEDIUM PRIORITY: {medium_impact} items
LOW PRIORITY: {low_impact} items

Key obligations:
{json.dumps([r['key_obligations'] for r in requirements[:3]], indent=2)}

Generate a 2-3 sentence summary for a compliance officer."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Generated {len(requirements)} compliance requirements for review."


if __name__ == "__main__":
    # Test the extractor
    import os
    from sebi_scraper import SEBIScraper
    
    # Check for API key
    if not st.secrets.get("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set. Get free key from https://console.groq.com")
        print("Then set: export GROQ_API_KEY=your_key_here")
    else:
        scraper = SEBIScraper()
        extractor = GroqComplianceExtractor()
        
        # Fetch a circular
        circulars = scraper.fetch_latest_circulars(limit=1)
        
        if circulars:
            circular = circulars[0]
            print(f"\n📄 Processing: {circular['title']}")
            
            # Extract requirements
            requirements = extractor.extract_requirements(circular)
            
            print("\n" + "="*60)
            print("EXTRACTED REQUIREMENTS")
            print("="*60)
            print(json.dumps(requirements, indent=2))
