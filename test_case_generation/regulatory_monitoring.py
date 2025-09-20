"""
Continuous Regulatory Change Monitoring Module

Monitors regulatory changes from official sources and alerts users when
compliance rules may have changed, ensuring test cases remain current.
"""

import logging
import requests
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import feedparser
import schedule
import time
import threading
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


@dataclass
class RegulatoryChange:
    """Detected regulatory change."""
    change_id: str
    standard: str
    title: str
    description: str
    source_url: str
    publication_date: str
    change_type: str  # new, updated, deprecated, clarification
    severity: str  # low, medium, high, critical
    affected_requirements: List[str]
    confidence: float
    detected_at: str


@dataclass
class MonitoringAlert:
    """Alert generated for regulatory changes."""
    alert_id: str
    change_id: str
    alert_type: str  # new_change, requirement_impact, compliance_risk
    severity: str
    title: str
    message: str
    affected_test_cases: List[str]
    recommended_actions: List[str]
    created_at: str


class RegulatoryMonitor:
    """Continuous regulatory change monitoring system."""
    
    def __init__(self, config_path: str = "config/regulatory_monitoring.json"):
        """Initialize the regulatory monitor."""
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(exist_ok=True)
        self.config = self._load_config()
        
        # Data storage
        self.changes_db_path = Path("data/regulatory_changes.json")
        self.changes_db_path.parent.mkdir(exist_ok=True)
        self.regulatory_changes = self._load_changes()
        
        # Alert storage
        self.alerts_db_path = Path("data/regulatory_alerts.json")
        self.alerts_db_path.parent.mkdir(exist_ok=True)
        self.alerts = self._load_alerts()
        
        # Monitoring sources
        self.monitoring_sources = self._initialize_monitoring_sources()
        
        # Change detection patterns
        self.change_patterns = self._initialize_change_patterns()
        
        # Monitoring thread
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default monitoring configuration."""
        config = {
            'monitoring_interval_hours': 24,
            'alert_threshold_confidence': 0.7,
            'email_notifications': {
                'enabled': False,
                'smtp_server': '',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'webhook_notifications': {
                'enabled': False,
                'urls': []
            },
            'monitored_standards': [
                'FDA_21_CFR_820',
                'FDA_21_CFR_11',
                'ISO_13485',
                'IEC_62304',
                'GDPR',
                'HIPAA'
            ],
            'change_detection': {
                'enable_content_analysis': True,
                'enable_keyword_matching': True,
                'enable_semantic_analysis': True
            }
        }
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_changes(self) -> List[Dict[str, Any]]:
        """Load regulatory changes from database."""
        if not self.changes_db_path.exists():
            return []
        
        try:
            with open(self.changes_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading changes: {e}")
            return []
    
    def _save_changes(self):
        """Save regulatory changes to database."""
        try:
            with open(self.changes_db_path, 'w') as f:
                json.dump(self.regulatory_changes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving changes: {e}")
    
    def _load_alerts(self) -> List[Dict[str, Any]]:
        """Load alerts from database."""
        if not self.alerts_db_path.exists():
            return []
        
        try:
            with open(self.alerts_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return []
    
    def _save_alerts(self):
        """Save alerts to database."""
        try:
            with open(self.alerts_db_path, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def _initialize_monitoring_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize monitoring sources for different standards."""
        return {
            'FDA_21_CFR_820': {
                'name': 'FDA Quality System Regulation',
                'rss_feeds': [
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance/rss.xml',
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance/guidance-documents/rss.xml'
                ],
                'web_pages': [
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance',
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance/guidance-documents'
                ],
                'keywords': ['quality system', 'design controls', 'validation', 'verification', '21 CFR 820']
            },
            'FDA_21_CFR_11': {
                'name': 'FDA Electronic Records and Electronic Signatures',
                'rss_feeds': [
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance/rss.xml'
                ],
                'web_pages': [
                    'https://www.fda.gov/medical-devices/device-regulation-and-guidance/guidance-documents/electronic-records-and-electronic-signatures'
                ],
                'keywords': ['electronic records', 'electronic signatures', '21 CFR 11', 'e-signature']
            },
            'ISO_13485': {
                'name': 'ISO 13485 Medical Devices Quality Management',
                'rss_feeds': [
                    'https://www.iso.org/feeds/rss/iso/iso-13485.xml'
                ],
                'web_pages': [
                    'https://www.iso.org/standard/59747.html'
                ],
                'keywords': ['ISO 13485', 'medical devices', 'quality management', 'QMS']
            },
            'IEC_62304': {
                'name': 'IEC 62304 Medical Device Software Life Cycle',
                'rss_feeds': [
                    'https://www.iec.ch/rss/iec/iec-62304.xml'
                ],
                'web_pages': [
                    'https://www.iec.ch/standard/62304.html'
                ],
                'keywords': ['IEC 62304', 'medical device software', 'software life cycle', 'safety classification']
            },
            'GDPR': {
                'name': 'General Data Protection Regulation',
                'rss_feeds': [
                    'https://edpb.europa.eu/news/rss_en.xml'
                ],
                'web_pages': [
                    'https://edpb.europa.eu/our-work-tools/general-guidance/gdpr-guidelines-recommendations-best-practices_en'
                ],
                'keywords': ['GDPR', 'data protection', 'privacy', 'personal data', 'consent']
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act',
                'rss_feeds': [
                    'https://www.hhs.gov/hipaa/news-and-events/rss.xml'
                ],
                'web_pages': [
                    'https://www.hhs.gov/hipaa/for-professionals/privacy/guidance'
                ],
                'keywords': ['HIPAA', 'health information', 'privacy', 'security', 'breach notification']
            }
        }
    
    def _initialize_change_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting regulatory changes."""
        return {
            'new_regulation': [
                r'new\s+(regulation|guidance|standard)',
                r'issued\s+(new|updated)\s+(regulation|guidance)',
                r'effective\s+(date|immediately)'
            ],
            'updated_regulation': [
                r'updated\s+(regulation|guidance|standard)',
                r'revised\s+(regulation|guidance)',
                r'amendment\s+to',
                r'changes\s+to\s+(regulation|guidance)'
            ],
            'deprecated_regulation': [
                r'deprecated\s+(regulation|guidance)',
                r'withdrawn\s+(regulation|guidance)',
                r'no\s+longer\s+applicable',
                r'superseded\s+by'
            ],
            'clarification': [
                r'clarification\s+of',
                r'guidance\s+on',
                r'interpretation\s+of',
                r'frequently\s+asked\s+questions'
            ]
        }
    
    def start_monitoring(self):
        """Start continuous monitoring."""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Regulatory monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        logger.info("Regulatory monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                self._check_all_sources()
                self._analyze_changes()
                self._generate_alerts()
                
                # Wait for next check
                interval_hours = self.config.get('monitoring_interval_hours', 24)
                time.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _check_all_sources(self):
        """Check all monitoring sources for changes."""
        monitored_standards = self.config.get('monitored_standards', [])
        
        for standard in monitored_standards:
            if standard in self.monitoring_sources:
                try:
                    self._check_standard_sources(standard)
                except Exception as e:
                    logger.error(f"Error checking sources for {standard}: {e}")
    
    def _check_standard_sources(self, standard: str):
        """Check sources for a specific standard."""
        source_info = self.monitoring_sources[standard]
        
        # Check RSS feeds
        for rss_url in source_info.get('rss_feeds', []):
            try:
                self._check_rss_feed(standard, rss_url)
            except Exception as e:
                logger.error(f"Error checking RSS feed {rss_url}: {e}")
        
        # Check web pages
        for web_url in source_info.get('web_pages', []):
            try:
                self._check_web_page(standard, web_url)
            except Exception as e:
                logger.error(f"Error checking web page {web_url}: {e}")
    
    def _check_rss_feed(self, standard: str, rss_url: str):
        """Check RSS feed for changes."""
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                # Check if this is a new entry
                entry_id = self._generate_entry_id(entry)
                if not self._is_known_change(entry_id):
                    # Analyze entry for regulatory changes
                    change = self._analyze_rss_entry(standard, entry, rss_url)
                    if change:
                        self.regulatory_changes.append({
                            'change_id': change.change_id,
                            'standard': change.standard,
                            'title': change.title,
                            'description': change.description,
                            'source_url': change.source_url,
                            'publication_date': change.publication_date,
                            'change_type': change.change_type,
                            'severity': change.severity,
                            'affected_requirements': change.affected_requirements,
                            'confidence': change.confidence,
                            'detected_at': change.detected_at
                        })
                        self._save_changes()
                        
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {e}")
    
    def _check_web_page(self, standard: str, web_url: str):
        """Check web page for changes."""
        try:
            response = requests.get(web_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for recent updates or announcements
            update_elements = soup.find_all(['div', 'section', 'article'], 
                                          class_=re.compile(r'update|announcement|news|change'))
            
            for element in update_elements:
                # Extract text content
                text_content = element.get_text(strip=True)
                
                # Check if this looks like a regulatory change
                if self._is_regulatory_change(text_content, standard):
                    change = self._analyze_web_content(standard, text_content, web_url)
                    if change:
                        self.regulatory_changes.append({
                            'change_id': change.change_id,
                            'standard': change.standard,
                            'title': change.title,
                            'description': change.description,
                            'source_url': change.source_url,
                            'publication_date': change.publication_date,
                            'change_type': change.change_type,
                            'severity': change.severity,
                            'affected_requirements': change.affected_requirements,
                            'confidence': change.confidence,
                            'detected_at': change.detected_at
                        })
                        self._save_changes()
                        
        except Exception as e:
            logger.error(f"Error checking web page {web_url}: {e}")
    
    def _analyze_rss_entry(self, standard: str, entry: Any, source_url: str) -> Optional[RegulatoryChange]:
        """Analyze RSS entry for regulatory changes."""
        title = getattr(entry, 'title', '')
        description = getattr(entry, 'description', '')
        link = getattr(entry, 'link', source_url)
        published = getattr(entry, 'published', datetime.now().isoformat())
        
        # Combine title and description for analysis
        content = f"{title} {description}"
        
        if not self._is_regulatory_change(content, standard):
            return None
        
        # Determine change type
        change_type = self._classify_change_type(content)
        
        # Determine severity
        severity = self._classify_severity(content, change_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(content, standard, change_type)
        
        # Generate change ID
        change_id = self._generate_change_id(standard, title, published)
        
        return RegulatoryChange(
            change_id=change_id,
            standard=standard,
            title=title,
            description=description,
            source_url=link,
            publication_date=published,
            change_type=change_type,
            severity=severity,
            affected_requirements=[],  # Will be populated later
            confidence=confidence,
            detected_at=datetime.now().isoformat()
        )
    
    def _analyze_web_content(self, standard: str, content: str, source_url: str) -> Optional[RegulatoryChange]:
        """Analyze web content for regulatory changes."""
        if not self._is_regulatory_change(content, standard):
            return None
        
        # Extract title (first line or sentence)
        lines = content.split('\n')
        title = lines[0][:100] if lines else "Regulatory Change"
        
        # Determine change type
        change_type = self._classify_change_type(content)
        
        # Determine severity
        severity = self._classify_severity(content, change_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(content, standard, change_type)
        
        # Generate change ID
        change_id = self._generate_change_id(standard, title, datetime.now().isoformat())
        
        return RegulatoryChange(
            change_id=change_id,
            standard=standard,
            title=title,
            description=content[:500],  # Truncate for storage
            source_url=source_url,
            publication_date=datetime.now().isoformat(),
            change_type=change_type,
            severity=severity,
            affected_requirements=[],
            confidence=confidence,
            detected_at=datetime.now().isoformat()
        )
    
    def _is_regulatory_change(self, content: str, standard: str) -> bool:
        """Check if content represents a regulatory change."""
        content_lower = content.lower()
        
        # Check for standard-specific keywords
        if standard in self.monitoring_sources:
            keywords = self.monitoring_sources[standard]['keywords']
            if not any(keyword.lower() in content_lower for keyword in keywords):
                return False
        
        # Check for change indicators
        change_indicators = [
            'new', 'updated', 'revised', 'amended', 'changed',
            'effective', 'issued', 'published', 'announced'
        ]
        
        if not any(indicator in content_lower for indicator in change_indicators):
            return False
        
        # Check for regulatory context
        regulatory_context = [
            'regulation', 'guidance', 'standard', 'requirement',
            'compliance', 'regulatory', 'policy', 'procedure'
        ]
        
        return any(context in content_lower for context in regulatory_context)
    
    def _classify_change_type(self, content: str) -> str:
        """Classify the type of regulatory change."""
        content_lower = content.lower()
        
        for change_type, patterns in self.change_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return change_type.replace('_', ' ')
        
        return 'general'
    
    def _classify_severity(self, content: str, change_type: str) -> str:
        """Classify the severity of the regulatory change."""
        content_lower = content.lower()
        
        # High severity indicators
        high_severity = [
            'immediate', 'urgent', 'critical', 'mandatory',
            'required', 'effective immediately', 'compliance required'
        ]
        
        if any(indicator in content_lower for indicator in high_severity):
            return 'critical'
        
        # Medium severity indicators
        medium_severity = [
            'important', 'significant', 'major', 'updated',
            'revised', 'amended', 'changes to'
        ]
        
        if any(indicator in content_lower for indicator in medium_severity):
            return 'high'
        
        # Low severity indicators
        low_severity = [
            'clarification', 'guidance', 'frequently asked',
            'interpretation', 'best practice'
        ]
        
        if any(indicator in content_lower for indicator in low_severity):
            return 'medium'
        
        return 'low'
    
    def _calculate_confidence(self, content: str, standard: str, change_type: str) -> float:
        """Calculate confidence score for the detected change."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on standard-specific keywords
        if standard in self.monitoring_sources:
            keywords = self.monitoring_sources[standard]['keywords']
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in content.lower())
            confidence += min(keyword_matches * 0.1, 0.3)
        
        # Increase confidence based on change type specificity
        if change_type in ['new regulation', 'updated regulation']:
            confidence += 0.2
        elif change_type in ['deprecated regulation']:
            confidence += 0.3
        
        # Increase confidence based on content length and detail
        if len(content) > 200:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_change_id(self, standard: str, title: str, date: str) -> str:
        """Generate unique change ID."""
        content = f"{standard}_{title}_{date}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_entry_id(self, entry: Any) -> str:
        """Generate unique entry ID."""
        title = getattr(entry, 'title', '')
        link = getattr(entry, 'link', '')
        published = getattr(entry, 'published', '')
        content = f"{title}_{link}_{published}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _is_known_change(self, change_id: str) -> bool:
        """Check if change is already known."""
        return any(change['change_id'] == change_id for change in self.regulatory_changes)
    
    def _analyze_changes(self):
        """Analyze detected changes for impact on requirements."""
        for change in self.regulatory_changes:
            if not change.get('affected_requirements'):
                # Analyze change for requirement impact
                affected_requirements = self._analyze_requirement_impact(change)
                change['affected_requirements'] = affected_requirements
                self._save_changes()
    
    def _analyze_requirement_impact(self, change: Dict[str, Any]) -> List[str]:
        """Analyze which requirements might be affected by the change."""
        # This would require integration with the requirements database
        # For now, return empty list
        return []
    
    def _generate_alerts(self):
        """Generate alerts for significant changes."""
        threshold_confidence = self.config.get('alert_threshold_confidence', 0.7)
        
        for change in self.regulatory_changes:
            if change['confidence'] >= threshold_confidence:
                alert = self._create_alert(change)
                if alert:
                    self.alerts.append({
                        'alert_id': alert.alert_id,
                        'change_id': alert.change_id,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'title': alert.title,
                        'message': alert.message,
                        'affected_test_cases': alert.affected_test_cases,
                        'recommended_actions': alert.recommended_actions,
                        'created_at': alert.created_at
                    })
                    self._save_alerts()
                    
                    # Send notifications
                    self._send_notifications(alert)
    
    def _create_alert(self, change: Dict[str, Any]) -> Optional[MonitoringAlert]:
        """Create alert for regulatory change."""
        alert_id = f"alert_{change['change_id']}"
        
        # Determine alert type
        if change['change_type'] == 'new regulation':
            alert_type = 'new_change'
        elif change['affected_requirements']:
            alert_type = 'requirement_impact'
        else:
            alert_type = 'compliance_risk'
        
        # Generate alert content
        title = f"Regulatory Change Alert: {change['standard']}"
        message = f"""
        A {change['change_type']} has been detected for {change['standard']}.
        
        Title: {change['title']}
        Description: {change['description']}
        Severity: {change['severity']}
        Confidence: {change['confidence']:.1%}
        
        Source: {change['source_url']}
        """
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(change)
        
        return MonitoringAlert(
            alert_id=alert_id,
            change_id=change['change_id'],
            alert_type=alert_type,
            severity=change['severity'],
            title=title,
            message=message,
            affected_test_cases=change['affected_requirements'],
            recommended_actions=recommended_actions,
            created_at=datetime.now().isoformat()
        )
    
    def _generate_recommended_actions(self, change: Dict[str, Any]) -> List[str]:
        """Generate recommended actions for regulatory change."""
        actions = []
        
        if change['change_type'] == 'new regulation':
            actions.append("Review new regulation requirements")
            actions.append("Update compliance mapping")
            actions.append("Generate new test cases if needed")
        elif change['change_type'] == 'updated regulation':
            actions.append("Review updated regulation")
            actions.append("Update existing test cases")
            actions.append("Verify compliance coverage")
        elif change['change_type'] == 'deprecated regulation':
            actions.append("Identify deprecated requirements")
            actions.append("Update or remove related test cases")
            actions.append("Update compliance documentation")
        
        if change['severity'] in ['critical', 'high']:
            actions.append("Prioritize immediate review")
            actions.append("Notify stakeholders")
        
        return actions
    
    def _send_notifications(self, alert: MonitoringAlert):
        """Send notifications for alerts."""
        # Email notifications
        if self.config.get('email_notifications', {}).get('enabled', False):
            self._send_email_notification(alert)
        
        # Webhook notifications
        if self.config.get('webhook_notifications', {}).get('enabled', False):
            self._send_webhook_notification(alert)
    
    def _send_email_notification(self, alert: MonitoringAlert):
        """Send email notification."""
        try:
            email_config = self.config['email_notifications']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = alert.title
            
            msg.attach(MIMEText(alert.message, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def _send_webhook_notification(self, alert: MonitoringAlert):
        """Send webhook notification."""
        try:
            webhook_config = self.config['webhook_notifications']
            
            payload = {
                'alert_id': alert.alert_id,
                'change_id': alert.change_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'affected_test_cases': alert.affected_test_cases,
                'recommended_actions': alert.recommended_actions,
                'created_at': alert.created_at
            }
            
            for webhook_url in webhook_config['urls']:
                response = requests.post(webhook_url, json=payload, timeout=30)
                response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    def get_recent_changes(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent regulatory changes."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_changes = []
        for change in self.regulatory_changes:
            change_date = datetime.fromisoformat(change['detected_at'].replace('Z', '+00:00'))
            if change_date >= cutoff_date:
                recent_changes.append(change)
        
        return sorted(recent_changes, key=lambda x: x['detected_at'], reverse=True)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        return [alert for alert in self.alerts if alert['severity'] in ['critical', 'high']]
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        total_changes = len(self.regulatory_changes)
        total_alerts = len(self.alerts)
        
        # Count by standard
        changes_by_standard = {}
        for change in self.regulatory_changes:
            standard = change['standard']
            changes_by_standard[standard] = changes_by_standard.get(standard, 0) + 1
        
        # Count by severity
        alerts_by_severity = {}
        for alert in self.alerts:
            severity = alert['severity']
            alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
        
        return {
            'total_changes': total_changes,
            'total_alerts': total_alerts,
            'changes_by_standard': changes_by_standard,
            'alerts_by_severity': alerts_by_severity,
            'monitoring_active': self.is_monitoring,
            'last_check': datetime.now().isoformat()
        }
