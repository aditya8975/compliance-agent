
import streamlit as st
import json
from datetime import datetime
import pandas as pd
from autonomous_agent import AutonomousComplianceAgent
from sebi_scraper import SEBIScraper
from dotenv import load_dotenv
import os
load_dotenv()


st.set_page_config(
    page_title="🛡️ Compliance Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .circular-card {
        background: #f8f9fa;
        padding: 15px;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .high-priority {
        color: #d32f2f;
        font-weight: bold;
    }
    .medium-priority {
        color: #f57c00;
        font-weight: bold;
    }
    .low-priority {
        color: #388e3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = AutonomousComplianceAgent(check_interval=60)
    except Exception as e:
        st.error(f"⚠️ Error initializing agent: {str(e)}")
        st.info("Make sure GROQ_API_KEY is set. Get free key from https://console.groq.com")
        st.stop()

if 'scraper' not in st.session_state:
    st.session_state.scraper = SEBIScraper()

# Sidebar
with st.sidebar:
    st.title("🛡️ Compliance Agent")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Circulars", "Tasks", "Reports", "Settings"]
    )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Run Check", use_container_width=True):
            with st.spinner("Running compliance check..."):
                report = st.session_state.agent.run_once()
                st.success(f"✅ Check completed! Processed: {report.get('processed', 0)}")
    
    with col2:
        if st.button("📊 Export", use_container_width=True):
            st.info("Export feature coming soon")
    
    st.markdown("---")
    
    # Stats
    st.subheader("Statistics")
    st.metric("Total Tasks", len(st.session_state.agent.tasks))
    st.metric("Processed Circulars", len(st.session_state.agent.processed_circulars))
    st.metric("Reports Generated", len(st.session_state.agent.reports))


# Main content
if page == "Dashboard":
    st.title("📊 Compliance Dashboard")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Circulars",
            len(st.session_state.agent.processed_circulars),
            "This month"
        )
    
    with col2:
        high_priority = sum(1 for t in st.session_state.agent.tasks if t.get('priority') == 'HIGH')
        st.metric(
            "High Priority",
            high_priority,
            "Requires action"
        )
    
    with col3:
        open_tasks = sum(1 for t in st.session_state.agent.tasks if t.get('status') == 'OPEN')
        st.metric(
            "Open Tasks",
            open_tasks,
            "Pending"
        )
    
    with col4:
        st.metric(
            "Compliance Status",
            "IN PROGRESS",
            "Monitoring active"
        )
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    if st.session_state.agent.reports:
        latest_report = st.session_state.agent.reports[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Last Check:** {latest_report['timestamp']}")
        
        with col2:
            st.info(f"**New Circulars:** {latest_report.get('new_circulars_found', 0)}")
        
        with col3:
            st.info(f"**Tasks Created:** {latest_report.get('total_tasks_created', 0)}")
        
        # Recent circulars
        st.subheader("Recently Processed Circulars")
        
        for item in latest_report.get('processed_details', [])[:5]:
            requirement = item.get('requirement', {})
            
            with st.expander(f"📄 {requirement.get('title', 'N/A')[:60]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** {requirement.get('circular_id')}")
                    st.write(f"**Date:** {requirement.get('date')}")
                    st.write(f"**Category:** {requirement.get('category')}")
                    st.write(f"**Deadline:** {requirement.get('deadline')}")
                
                with col2:
                    priority = requirement.get('impact_level', 'MEDIUM')
                    if priority == 'HIGH':
                        st.error(f"🔴 {priority}")
                    elif priority == 'MEDIUM':
                        st.warning(f"🟡 {priority}")
                    else:
                        st.success(f"🟢 {priority}")
                
                st.write("**Key Obligations:**")
                for obligation in requirement.get('key_obligations', []):
                    st.write(f"• {obligation}")
                
                st.write("**Applicable To:**")
                for entity in requirement.get('applicable_to', []):
                    st.write(f"• {entity}")
    else:
        st.info("No compliance checks run yet. Click 'Run Check' to start.")


elif page == "Circulars":
    st.title("📄 SEBI Circulars")
    
    # Fetch latest circulars
    with st.spinner("Fetching latest SEBI circulars..."):
        circulars = st.session_state.scraper.fetch_latest_circulars(limit=10)
    
    if circulars:
        st.success(f"✅ Fetched {len(circulars)} circulars")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                options=list(set(c['category'] for c in circulars)),
                default=None
            )
        
        with col2:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Category"])
        
        # Filter and sort
        filtered_circulars = circulars
        
        if category_filter:
            filtered_circulars = [c for c in filtered_circulars if c['category'] in category_filter]
        
        if sort_by == "Date (Newest)":
            filtered_circulars = sorted(filtered_circulars, key=lambda x: x['date'], reverse=True)
        elif sort_by == "Date (Oldest)":
            filtered_circulars = sorted(filtered_circulars, key=lambda x: x['date'])
        else:
            filtered_circulars = sorted(filtered_circulars, key=lambda x: x['category'])
        
        # Display circulars
        for circular in filtered_circulars:
            with st.expander(f"📋 {circular['title'][:60]}... ({circular['date']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** `{circular['id']}`")
                    st.write(f"**Date:** {circular['date']}")
                    st.write(f"**Category:** {circular['category']}")
                    st.write(f"**URL:** {circular['url']}")
                
                with col2:
                    is_processed = circular['id'] in st.session_state.agent.processed_circulars
                    if is_processed:
                        st.success("✅ Processed")
                    else:
                        st.info("⏳ Pending")
                
                # Process button
                if not is_processed:
                    if st.button(f"Process: {circular['id']}", key=f"process_{circular['id']}"):
                        with st.spinner("Processing..."):
                            try:
                                requirement = st.session_state.agent.extractor.extract_requirements(circular)
                                tasks = st.session_state.agent._create_tasks(requirement)
                                st.session_state.agent.processed_circulars.add(circular['id'])
                                st.success(f"✅ Created {len(tasks)} tasks")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    else:
        st.warning("No circulars found")


elif page == "Tasks":
    st.title("✅ Compliance Tasks")
    
    if st.session_state.agent.tasks:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["OPEN", "IN PROGRESS", "COMPLETED"],
                default=["OPEN"]
            )
        
        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=["HIGH", "MEDIUM", "LOW"],
                default=None
            )
        
        with col3:
            task_type_filter = st.multiselect(
                "Filter by Type",
                options=list(set(t.get('type', 'other') for t in st.session_state.agent.tasks)),
                default=None
            )
        
        # Filter tasks
        tasks = st.session_state.agent.tasks
        
        if status_filter:
            tasks = [t for t in tasks if t.get('status') in status_filter]
        
        if priority_filter:
            tasks = [t for t in tasks if t.get('priority') in priority_filter]
        
        if task_type_filter:
            tasks = [t for t in tasks if t.get('type') in task_type_filter]
        
        st.info(f"Showing {len(tasks)} tasks")
        
        # Display tasks
        for task in tasks:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{task['title']}**")
                st.caption(f"ID: {task['id']}")
            
            with col2:
                priority = task.get('priority', 'MEDIUM')
                if priority == 'HIGH':
                    st.error(f"🔴 {priority}")
                elif priority == 'MEDIUM':
                    st.warning(f"🟡 {priority}")
                else:
                    st.success(f"🟢 {priority}")
            
            with col3:
                status = task.get('status', 'OPEN')
                if status == 'OPEN':
                    st.info(status)
                elif status == 'IN PROGRESS':
                    st.warning(status)
                else:
                    st.success(status)
            
            # Task details
            with st.expander("Details"):
                st.write(f"**Description:** {task.get('description')}")
                st.write(f"**Assigned to:** {task.get('assigned_to')}")
                st.write(f"**Deadline:** {task.get('deadline')}")
                st.write(f"**Created:** {task.get('created_at')}")
                
                # Update status
                new_status = st.selectbox(
                    "Update Status",
                    ["OPEN", "IN PROGRESS", "COMPLETED"],
                    index=["OPEN", "IN PROGRESS", "COMPLETED"].index(status),
                    key=f"status_{task['id']}"
                )
                
                if new_status != status:
                    if st.button("Save", key=f"save_{task['id']}"):
                        st.session_state.agent.update_task_status(task['id'], new_status)
                        st.success(f"✅ Updated to {new_status}")
                        st.rerun()
    else:
        st.info("No tasks yet. Run a compliance check to create tasks.")


elif page == "Reports":
    st.title("📊 Compliance Reports")
    
    if st.session_state.agent.reports:
        # Select report
        report_options = [f"{r['cycle_id']} - {r['timestamp']}" for r in st.session_state.agent.reports]
        selected_idx = st.selectbox("Select Report", range(len(report_options)), format_func=lambda x: report_options[x])
        
        report = st.session_state.agent.reports[selected_idx]
        
        # Report summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("New Circulars", report.get('new_circulars_found', 0))
        
        with col2:
            st.metric("Processed", report.get('processed', 0))
        
        with col3:
            st.metric("Tasks Created", report.get('total_tasks_created', 0))
        
        with col4:
            st.metric("Timestamp", report['timestamp'][:10])
        
        st.markdown("---")
        
        # Processed details
        st.subheader("Processed Circulars")
        
        for item in report.get('processed_details', []):
            requirement = item.get('requirement', {})
            
            with st.expander(f"📄 {requirement.get('title', 'N/A')[:60]}"):
                st.write(f"**ID:** {requirement.get('circular_id')}")
                st.write(f"**Impact Level:** {requirement.get('impact_level')}")
                st.write(f"**Deadline:** {requirement.get('deadline')}")
                
                st.write("**Key Obligations:**")
                for obligation in requirement.get('key_obligations', []):
                    st.write(f"• {obligation}")
                
                st.write(f"**Tasks Created:** {len(item.get('tasks', []))}")
        
        # Export options
        st.markdown("---")
        st.subheader("Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download JSON"):
                json_str = json.dumps(report, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"report_{report['cycle_id']}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Download CSV"):
                csv_str = st.session_state.agent._convert_to_csv(report)
                st.download_button(
                    label="Download CSV",
                    data=csv_str,
                    file_name=f"report_{report['cycle_id']}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No reports generated yet. Run a compliance check to generate reports.")


elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("API Configuration")
    groq_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    st.info(f"GROQ API Key: {'✅ Configured' if groq_key else '❌ Not configured'}")
    
    if not groq_key:
        st.warning("⚠️ GROQ_API_KEY not set")
        st.markdown("""
        1. Get free API key from https://console.groq.com
        2. Set environment variable:
           ```bash
           export GROQ_API_KEY=your_key_here
           ```
        3. Restart the app
        """)
    
    st.markdown("---")
    
    st.subheader("Agent Configuration")
    
    check_interval = st.number_input(
        "Check Interval (seconds)",
        min_value=60,
        max_value=86400,
        value=3600,
        step=60,
        help="How often to check for new circulars"
    )
    
    st.markdown("---")
    
    st.subheader("About")
    
    st.markdown("""
    ### 🛡️ Autonomous Compliance Agent
    
    An AI-powered agent that:
    - Monitors SEBI regulatory circulars in real-time
    - Extracts compliance requirements using Groq AI
    - Automatically assigns tasks to teams
    - Generates audit-ready reports
    
    **Tech Stack:**
    - Groq API (Free LLM)
    - Streamlit (UI)
    - BeautifulSoup (Web Scraping)
    - Python
    
    **Status:** Production Ready
    
    ---
    
    Built to compete with OnFinance AI and help Indian startups stay compliant.
    """)


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🛡️ Compliance Agent v1.0 
</div>
""", unsafe_allow_html=True)
