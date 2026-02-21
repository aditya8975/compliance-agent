"""
Autonomous Compliance Agent
Continuously monitors for new circulars and processes them automatically
"""

import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os
from sebi_scraper import SEBIScraper
from groq_extractor import GroqComplianceExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousComplianceAgent:
    """Autonomous agent that monitors and processes compliance circulars"""
    
    def __init__(self, check_interval: int = 3600):
        """
        Initialize autonomous agent
        
        Args:
            check_interval: Seconds between checks for new circulars (default: 1 hour)
        """
        self.scraper = SEBIScraper()
        self.extractor = GroqComplianceExtractor()
        self.check_interval = check_interval
        self.processed_circulars = set()
        self.tasks = []
        self.reports = []
        
        # Load processed circulars from file if exists
        self._load_state()
        
        logger.info(f"Initialized autonomous agent (check interval: {check_interval}s)")
    
    def run_once(self) -> Dict:
        """
        Run one cycle of compliance check
        
        Returns:
            Report of processed circulars
        """
        logger.info("Starting compliance check cycle...")
        
        try:
            # Step 1: Fetch latest circulars
            circulars = self.scraper.fetch_latest_circulars(limit=10)
            
            # Step 2: Filter new circulars
            new_circulars = [
                c for c in circulars 
                if c['id'] not in self.processed_circulars
            ]
            
            logger.info(f"Found {len(new_circulars)} new circulars out of {len(circulars)}")
            
            # Step 3: Process each new circular
            processed = []
            for circular in new_circulars:
                try:
                    # CRITICAL FIX: Fetch actual circular text before AI analysis
                    logger.info(f"Fetching circular text from {circular['url']}...")
                    circular_text = self.scraper.fetch_circular_text(circular['url'])
                    
                    if not circular_text:
                        logger.warning(f"Could not fetch text for {circular['id']}, using title only")
                        circular_text = circular.get('description', '')
                    
                    # Extract requirements using AI (now with actual circular text)
                    requirement = self.extractor.extract_requirements(circular, circular_text)
                    
                    # Create tasks
                    tasks = self._create_tasks(requirement)
                    
                    # Store results
                    self.processed_circulars.add(circular['id'])
                    processed.append({
                        "circular": circular,
                        "requirement": requirement,
                        "tasks": tasks
                    })
                    
                    logger.info(f"✅ Processed: {circular['id']}")
                
                except Exception as e:
                    logger.error(f"Error processing {circular['id']}: {str(e)}")
                    continue
            
            # Step 4: Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "cycle_id": self._generate_cycle_id(),
                "new_circulars_found": len(new_circulars),
                "processed": len(processed),
                "processed_details": processed,
                "total_tasks_created": sum(len(p['tasks']) for p in processed)
            }
            
            self.reports.append(report)
            
            # Step 5: Save state
            self._save_state()
            
            logger.info(f"Compliance check cycle completed. Processed: {len(processed)}")
            return report
        
        except Exception as e:
            logger.error(f"Error in compliance check cycle: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "processed": 0
            }
    
    def run_continuous(self, duration_seconds: Optional[int] = None):
        """
        Run agent continuously
        
        Args:
            duration_seconds: Run for this many seconds (None = infinite)
        """
        logger.info(f"Starting continuous monitoring (interval: {self.check_interval}s)")
        
        start_time = time.time()
        cycle_count = 0
        
        try:
            while True:
                # Check if duration exceeded
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    logger.info(f"Duration limit reached. Stopping agent.")
                    break
                
                cycle_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"COMPLIANCE CHECK CYCLE #{cycle_count}")
                logger.info(f"{'='*60}")
                
                # Run one cycle
                report = self.run_once()
                
                # Log results
                if report.get('processed', 0) > 0:
                    logger.info(f"✅ Found and processed {report['processed']} new circulars")
                else:
                    logger.info("No new circulars found")
                
                # Wait for next cycle
                logger.info(f"Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
        finally:
            self._save_state()
            logger.info(f"Agent stopped after {cycle_count} cycles")
    
    def _create_tasks(self, requirement: Dict) -> List[Dict]:
        """Create actionable tasks from requirement"""
        tasks = []
        
        # Task 1: Review
        tasks.append({
            "id": f"{requirement['circular_id']}_review",
            "title": f"Review: {requirement['title']}",
            "type": "review",
            "description": f"Review and understand the compliance requirement",
            "priority": requirement['impact_level'],
            "deadline": requirement['deadline'],
            "assigned_to": "compliance_team",
            "status": "OPEN",
            "created_at": datetime.now().isoformat()
        })
        
        # Task 2: Impact Assessment
        tasks.append({
            "id": f"{requirement['circular_id']}_impact",
            "title": f"Impact Assessment: {requirement['title']}",
            "type": "assessment",
            "description": f"Assess impact on organization",
            "priority": requirement['impact_level'],
            "deadline": requirement['deadline'],
            "assigned_to": "legal_team",
            "status": "OPEN",
            "created_at": datetime.now().isoformat()
        })
        
        # Task 3: Implementation
        tasks.append({
            "id": f"{requirement['circular_id']}_implement",
            "title": f"Implementation Plan: {requirement['title']}",
            "type": "implementation",
            "description": f"Create implementation plan and timeline",
            "priority": requirement['impact_level'],
            "deadline": requirement['deadline'],
            "assigned_to": "operations_team",
            "status": "OPEN",
            "created_at": datetime.now().isoformat()
        })
        
        self.tasks.extend(tasks)
        return tasks
    
    def _generate_cycle_id(self) -> str:
        """Generate unique cycle ID"""
        return f"CYCLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _save_state(self):
        """Save agent state to file"""
        try:
            state = {
                "processed_circulars": list(self.processed_circulars),
                "last_save": datetime.now().isoformat(),
                "total_reports": len(self.reports),
                "total_tasks": len(self.tasks)
            }
            
            with open('.agent_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug("Agent state saved")
        except Exception as e:
            logger.warning(f"Could not save agent state: {str(e)}")
    
    def _load_state(self):
        """Load agent state from file"""
        try:
            if os.path.exists('.agent_state.json'):
                with open('.agent_state.json', 'r') as f:
                    state = json.load(f)
                    self.processed_circulars = set(state.get('processed_circulars', []))
                    logger.info(f"Loaded state: {len(self.processed_circulars)} previously processed circulars")
        except Exception as e:
            logger.warning(f"Could not load agent state: {str(e)}")
    
    def get_report(self, cycle_id: Optional[str] = None) -> Dict:
        """Get report from specific cycle or latest"""
        if cycle_id:
            for report in self.reports:
                if report.get('cycle_id') == cycle_id:
                    return report
            return None
        
        return self.reports[-1] if self.reports else None
    
    def get_all_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """Get tasks, optionally filtered by status"""
        if status:
            return [t for t in self.tasks if t.get('status') == status]
        return self.tasks
    
    def update_task_status(self, task_id: str, status: str):
        """Update task status"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now().isoformat()
                logger.info(f"Updated task {task_id} to {status}")
                self._save_state()
                return True
        return False
    
    def export_report(self, format: str = "json") -> str:
        """Export latest report"""
        report = self.get_report()
        
        if not report:
            return ""
        
        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "csv":
            return self._convert_to_csv(report)
        else:
            return json.dumps(report, indent=2)
    
    def _convert_to_csv(self, report: Dict) -> str:
        """Convert report to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Circular ID', 'Title', 'Impact Level', 'Deadline', 'Tasks Created'])
        
        # Data
        for item in report.get('processed_details', []):
            requirement = item.get('requirement', {})
            writer.writerow([
                requirement.get('circular_id', ''),
                requirement.get('title', '')[:50],
                requirement.get('impact_level', ''),
                requirement.get('deadline', ''),
                len(item.get('tasks', []))
            ])
        
        return output.getvalue()


if __name__ == "__main__":
    import sys
    
    # Check for API key
    if not st.secrets.get("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set")
        print("Get free key from: https://console.groq.com")
        print("Then set: export GROQ_API_KEY=your_key_here")
        sys.exit(1)
    
    # Run agent
    agent = AutonomousComplianceAgent(check_interval=10)  # Check every 10 seconds for demo
    
    # Run for 60 seconds (demo mode)
    print("\n🤖 Starting Autonomous Compliance Agent (demo mode - 60 seconds)")
    print("="*60)
    agent.run_continuous(duration_seconds=60)
    
    # Print summary
    print("\n" + "="*60)
    print("AGENT SUMMARY")
    print("="*60)
    print(f"Total cycles run: {len(agent.reports)}")
    print(f"Total tasks created: {len(agent.tasks)}")
    print(f"Processed circulars: {len(agent.processed_circulars)}")
    
    if agent.reports:
        latest = agent.reports[-1]
        print(f"\nLatest cycle: {latest.get('cycle_id')}")
        print(f"New circulars found: {latest.get('new_circulars_found')}")
        print(f"Processed: {latest.get('processed')}")
