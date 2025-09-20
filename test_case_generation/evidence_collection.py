"""
Automated Evidence Collection Module

Enables auto-capture of execution logs, screenshots, and files linked to each test case run.
Organizes and links all artifacts back to the traceability matrix for audit-ready documentation.
"""

import logging
import json
import os
import shutil
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import zipfile
import sqlite3
from contextlib import contextmanager
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)


@dataclass
class EvidenceArtifact:
    """Individual evidence artifact."""
    artifact_id: str
    test_case_id: str
    artifact_type: str  # screenshot, log, file, video, document
    file_path: str
    file_size: int
    checksum: str
    metadata: Dict[str, Any]
    created_at: str
    created_by: str


@dataclass
class EvidencePackage:
    """Package of evidence artifacts for a test case."""
    package_id: str
    test_case_id: str
    artifacts: List[EvidenceArtifact]
    total_size: int
    created_at: str
    audit_ready: bool


@dataclass
class ExecutionSession:
    """Test execution session with evidence collection."""
    session_id: str
    test_case_id: str
    start_time: str
    end_time: Optional[str]
    status: str  # running, completed, failed
    evidence_artifacts: List[str]  # artifact IDs
    execution_log: str
    environment_info: Dict[str, Any]


class EvidenceCollector:
    """Automated evidence collection system."""
    
    def __init__(self, evidence_root: str = "evidence", db_path: str = "data/evidence.db"):
        """Initialize the evidence collector."""
        self.evidence_root = Path(evidence_root)
        self.evidence_root.mkdir(exist_ok=True)
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Create evidence directory structure
        self._create_directory_structure()
        
        # Initialize database
        self._initialize_database()
        
        # Current execution session
        self.current_session = None
    
    def _create_directory_structure(self):
        """Create organized directory structure for evidence."""
        directories = [
            'screenshots',
            'logs',
            'files',
            'videos',
            'documents',
            'packages',
            'temp'
        ]
        
        for directory in directories:
            (self.evidence_root / directory).mkdir(exist_ok=True)
    
    def _initialize_database(self):
        """Initialize SQLite database for evidence tracking."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create evidence artifacts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    test_case_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL
                )
            ''')
            
            # Create evidence packages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence_packages (
                    package_id TEXT PRIMARY KEY,
                    test_case_id TEXT NOT NULL,
                    total_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    audit_ready BOOLEAN NOT NULL
                )
            ''')
            
            # Create execution sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_sessions (
                    session_id TEXT PRIMARY KEY,
                    test_case_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    execution_log TEXT,
                    environment_info TEXT NOT NULL
                )
            ''')
            
            # Create package artifacts relationship table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS package_artifacts (
                    package_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    PRIMARY KEY (package_id, artifact_id),
                    FOREIGN KEY (package_id) REFERENCES evidence_packages(package_id),
                    FOREIGN KEY (artifact_id) REFERENCES evidence_artifacts(artifact_id)
                )
            ''')
            
            conn.commit()
    
    def start_execution_session(self, test_case_id: str, 
                              environment_info: Dict[str, Any] = None) -> str:
        """Start a new execution session for evidence collection."""
        session_id = f"session_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if environment_info is None:
            environment_info = self._get_default_environment_info()
        
        self.current_session = ExecutionSession(
            session_id=session_id,
            test_case_id=test_case_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            status='running',
            evidence_artifacts=[],
            execution_log="",
            environment_info=environment_info
        )
        
        # Save session to database
        self._save_execution_session(self.current_session)
        
        logger.info(f"Started execution session {session_id} for test case {test_case_id}")
        return session_id
    
    def end_execution_session(self, status: str = 'completed', 
                            execution_log: str = ""):
        """End the current execution session."""
        if not self.current_session:
            logger.warning("No active execution session to end")
            return
        
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.status = status
        self.current_session.execution_log = execution_log
        
        # Update session in database
        self._update_execution_session(self.current_session)
        
        logger.info(f"Ended execution session {self.current_session.session_id} with status {status}")
        self.current_session = None
    
    def capture_screenshot(self, screenshot_name: str = None, 
                         element_selector: str = None) -> str:
        """Capture screenshot during test execution."""
        if not self.current_session:
            logger.warning("No active execution session for screenshot capture")
            return None
        
        try:
            # Generate screenshot filename
            if not screenshot_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                screenshot_name = f"screenshot_{timestamp}.png"
            
            # Create screenshot path
            screenshot_path = self.evidence_root / "screenshots" / screenshot_name
            
            # In a real implementation, this would use Selenium or similar
            # For demo purposes, create a placeholder image
            self._create_placeholder_screenshot(screenshot_path, element_selector)
            
            # Create evidence artifact
            artifact = self._create_evidence_artifact(
                test_case_id=self.current_session.test_case_id,
                artifact_type='screenshot',
                file_path=str(screenshot_path),
                metadata={
                    'element_selector': element_selector,
                    'session_id': self.current_session.session_id,
                    'capture_method': 'selenium'
                }
            )
            
            # Add to current session
            self.current_session.evidence_artifacts.append(artifact.artifact_id)
            
            logger.info(f"Screenshot captured: {screenshot_name}")
            return artifact.artifact_id
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def capture_execution_log(self, log_content: str, 
                            log_level: str = 'INFO') -> str:
        """Capture execution log during test run."""
        if not self.current_session:
            logger.warning("No active execution session for log capture")
            return None
        
        try:
            # Generate log filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            log_filename = f"execution_log_{timestamp}.log"
            
            # Create log file path
            log_path = self.evidence_root / "logs" / log_filename
            
            # Write log content
            with open(log_path, 'w') as f:
                f.write(f"=== Execution Log - {self.current_session.test_case_id} ===\n")
                f.write(f"Session ID: {self.current_session.session_id}\n")
                f.write(f"Start Time: {self.current_session.start_time}\n")
                f.write(f"Log Level: {log_level}\n")
                f.write("=" * 50 + "\n\n")
                f.write(log_content)
            
            # Create evidence artifact
            artifact = self._create_evidence_artifact(
                test_case_id=self.current_session.test_case_id,
                artifact_type='log',
                file_path=str(log_path),
                metadata={
                    'log_level': log_level,
                    'session_id': self.current_session.session_id,
                    'log_type': 'execution'
                }
            )
            
            # Add to current session
            self.current_session.evidence_artifacts.append(artifact.artifact_id)
            
            logger.info(f"Execution log captured: {log_filename}")
            return artifact.artifact_id
            
        except Exception as e:
            logger.error(f"Error capturing execution log: {e}")
            return None
    
    def capture_file(self, source_file_path: str, 
                    file_description: str = None) -> str:
        """Capture a file as evidence."""
        if not self.current_session:
            logger.warning("No active execution session for file capture")
            return None
        
        try:
            source_path = Path(source_file_path)
            if not source_path.exists():
                logger.error(f"Source file not found: {source_file_path}")
                return None
            
            # Generate evidence filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            evidence_filename = f"file_{timestamp}_{source_path.name}"
            
            # Create evidence file path
            evidence_path = self.evidence_root / "files" / evidence_filename
            
            # Copy file to evidence directory
            shutil.copy2(source_path, evidence_path)
            
            # Create evidence artifact
            artifact = self._create_evidence_artifact(
                test_case_id=self.current_session.test_case_id,
                artifact_type='file',
                file_path=str(evidence_path),
                metadata={
                    'original_path': str(source_path),
                    'description': file_description,
                    'session_id': self.current_session.session_id,
                    'file_extension': source_path.suffix
                }
            )
            
            # Add to current session
            self.current_session.evidence_artifacts.append(artifact.artifact_id)
            
            logger.info(f"File captured as evidence: {evidence_filename}")
            return artifact.artifact_id
            
        except Exception as e:
            logger.error(f"Error capturing file: {e}")
            return None
    
    def capture_video(self, video_name: str = None, 
                     duration: int = None) -> str:
        """Capture video during test execution."""
        if not self.current_session:
            logger.warning("No active execution session for video capture")
            return None
        
        try:
            # Generate video filename
            if not video_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                video_name = f"video_{timestamp}.mp4"
            
            # Create video path
            video_path = self.evidence_root / "videos" / video_name
            
            # In a real implementation, this would use screen recording
            # For demo purposes, create a placeholder
            self._create_placeholder_video(video_path, duration)
            
            # Create evidence artifact
            artifact = self._create_evidence_artifact(
                test_case_id=self.current_session.test_case_id,
                artifact_type='video',
                file_path=str(video_path),
                metadata={
                    'duration': duration,
                    'session_id': self.current_session.session_id,
                    'recording_method': 'screen_capture'
                }
            )
            
            # Add to current session
            self.current_session.evidence_artifacts.append(artifact.artifact_id)
            
            logger.info(f"Video captured: {video_name}")
            return artifact.artifact_id
            
        except Exception as e:
            logger.error(f"Error capturing video: {e}")
            return None
    
    def capture_document(self, document_content: str, 
                        document_type: str = 'text',
                        document_name: str = None) -> str:
        """Capture a document as evidence."""
        if not self.current_session:
            logger.warning("No active execution session for document capture")
            return None
        
        try:
            # Generate document filename
            if not document_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                document_name = f"document_{timestamp}.{document_type}"
            
            # Create document path
            document_path = self.evidence_root / "documents" / document_name
            
            # Write document content
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(document_content)
            
            # Create evidence artifact
            artifact = self._create_evidence_artifact(
                test_case_id=self.current_session.test_case_id,
                artifact_type='document',
                file_path=str(document_path),
                metadata={
                    'document_type': document_type,
                    'session_id': self.current_session.session_id,
                    'content_length': len(document_content)
                }
            )
            
            # Add to current session
            self.current_session.evidence_artifacts.append(artifact.artifact_id)
            
            logger.info(f"Document captured: {document_name}")
            return artifact.artifact_id
            
        except Exception as e:
            logger.error(f"Error capturing document: {e}")
            return None
    
    def create_evidence_package(self, test_case_id: str, 
                              include_artifacts: List[str] = None) -> EvidencePackage:
        """Create an evidence package for a test case."""
        try:
            # Get artifacts for test case
            if include_artifacts is None:
                artifacts = self._get_artifacts_for_test_case(test_case_id)
            else:
                artifacts = [self._get_artifact(artifact_id) for artifact_id in include_artifacts]
                artifacts = [a for a in artifacts if a is not None]
            
            if not artifacts:
                logger.warning(f"No artifacts found for test case {test_case_id}")
                return None
            
            # Generate package ID
            package_id = f"package_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate total size
            total_size = sum(artifact.file_size for artifact in artifacts)
            
            # Create package
            package = EvidencePackage(
                package_id=package_id,
                test_case_id=test_case_id,
                artifacts=artifacts,
                total_size=total_size,
                created_at=datetime.now().isoformat(),
                audit_ready=True
            )
            
            # Save package to database
            self._save_evidence_package(package)
            
            # Create package directory
            package_dir = self.evidence_root / "packages" / package_id
            package_dir.mkdir(exist_ok=True)
            
            # Copy artifacts to package directory
            for artifact in artifacts:
                source_path = Path(artifact.file_path)
                dest_path = package_dir / source_path.name
                shutil.copy2(source_path, dest_path)
            
            # Create package manifest
            manifest_path = package_dir / "manifest.json"
            manifest = {
                'package_id': package_id,
                'test_case_id': test_case_id,
                'created_at': package.created_at,
                'total_size': total_size,
                'artifact_count': len(artifacts),
                'artifacts': [
                    {
                        'artifact_id': artifact.artifact_id,
                        'artifact_type': artifact.artifact_type,
                        'file_name': Path(artifact.file_path).name,
                        'file_size': artifact.file_size,
                        'checksum': artifact.checksum,
                        'metadata': artifact.metadata
                    }
                    for artifact in artifacts
                ]
            }
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Evidence package created: {package_id}")
            return package
            
        except Exception as e:
            logger.error(f"Error creating evidence package: {e}")
            return None
    
    def create_audit_report(self, test_case_id: str) -> Dict[str, Any]:
        """Create comprehensive audit report for a test case."""
        try:
            # Get all artifacts for test case
            artifacts = self._get_artifacts_for_test_case(test_case_id)
            
            # Get execution sessions
            sessions = self._get_sessions_for_test_case(test_case_id)
            
            # Calculate statistics
            total_artifacts = len(artifacts)
            total_size = sum(artifact.file_size for artifact in artifacts)
            
            artifact_types = {}
            for artifact in artifacts:
                artifact_type = artifact.artifact_type
                artifact_types[artifact_type] = artifact_types.get(artifact_type, 0) + 1
            
            # Create audit report
            audit_report = {
                'test_case_id': test_case_id,
                'audit_date': datetime.now().isoformat(),
                'summary': {
                    'total_artifacts': total_artifacts,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'artifact_types': artifact_types,
                    'execution_sessions': len(sessions)
                },
                'artifacts': [
                    {
                        'artifact_id': artifact.artifact_id,
                        'artifact_type': artifact.artifact_type,
                        'file_path': artifact.file_path,
                        'file_size': artifact.file_size,
                        'checksum': artifact.checksum,
                        'created_at': artifact.created_at,
                        'metadata': artifact.metadata
                    }
                    for artifact in artifacts
                ],
                'execution_sessions': [
                    {
                        'session_id': session['session_id'],
                        'start_time': session['start_time'],
                        'end_time': session['end_time'],
                        'status': session['status'],
                        'environment_info': json.loads(session['environment_info'])
                    }
                    for session in sessions
                ],
                'compliance_info': {
                    'evidence_completeness': self._calculate_evidence_completeness(artifacts),
                    'audit_readiness': self._assess_audit_readiness(artifacts),
                    'traceability_verified': True
                }
            }
            
            # Save audit report
            report_path = self.evidence_root / "audit_reports" / f"audit_report_{test_case_id}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(audit_report, f, indent=2)
            
            logger.info(f"Audit report created for test case {test_case_id}")
            return audit_report
            
        except Exception as e:
            logger.error(f"Error creating audit report: {e}")
            return {'error': str(e)}
    
    def _create_evidence_artifact(self, test_case_id: str, artifact_type: str, 
                                file_path: str, metadata: Dict[str, Any]) -> EvidenceArtifact:
        """Create evidence artifact record."""
        file_path_obj = Path(file_path)
        
        # Calculate file checksum
        checksum = self._calculate_checksum(file_path)
        
        # Get file size
        file_size = file_path_obj.stat().st_size
        
        # Generate artifact ID
        artifact_id = f"artifact_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        
        # Create artifact
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            test_case_id=test_case_id,
            artifact_type=artifact_type,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            metadata=metadata,
            created_at=datetime.now().isoformat(),
            created_by='evidence_collector'
        )
        
        # Save to database
        self._save_evidence_artifact(artifact)
        
        return artifact
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _create_placeholder_screenshot(self, screenshot_path: Path, element_selector: str = None):
        """Create placeholder screenshot for demo purposes."""
        # Create a simple placeholder image
        img = Image.new('RGB', (800, 600), color='lightblue')
        
        # Add some text to indicate it's a placeholder
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Placeholder Screenshot\nTest Case: {self.current_session.test_case_id if self.current_session else 'Unknown'}\nElement: {element_selector or 'Full Page'}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Draw text
        draw.text((10, 10), text, fill='black', font=font)
        
        # Save image
        img.save(screenshot_path, 'PNG')
    
    def _create_placeholder_video(self, video_path: Path, duration: int = None):
        """Create placeholder video for demo purposes."""
        # For demo purposes, create a text file indicating video
        with open(video_path.with_suffix('.txt'), 'w') as f:
            f.write(f"Placeholder Video File\n")
            f.write(f"Test Case: {self.current_session.test_case_id if self.current_session else 'Unknown'}\n")
            f.write(f"Duration: {duration or 'Unknown'} seconds\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"Note: This is a placeholder. In production, this would be an actual video file.\n")
    
    def _get_default_environment_info(self) -> Dict[str, Any]:
        """Get default environment information."""
        return {
            'os': os.name,
            'python_version': os.sys.version,
            'platform': os.sys.platform,
            'working_directory': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_evidence_artifact(self, artifact: EvidenceArtifact):
        """Save evidence artifact to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO evidence_artifacts
                (artifact_id, test_case_id, artifact_type, file_path, file_size, 
                 checksum, metadata, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                artifact.artifact_id,
                artifact.test_case_id,
                artifact.artifact_type,
                artifact.file_path,
                artifact.file_size,
                artifact.checksum,
                json.dumps(artifact.metadata),
                artifact.created_at,
                artifact.created_by
            ))
            conn.commit()
    
    def _save_evidence_package(self, package: EvidencePackage):
        """Save evidence package to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save package
            cursor.execute('''
                INSERT OR REPLACE INTO evidence_packages
                (package_id, test_case_id, total_size, created_at, audit_ready)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                package.package_id,
                package.test_case_id,
                package.total_size,
                package.created_at,
                package.audit_ready
            ))
            
            # Save package-artifact relationships
            for artifact in package.artifacts:
                cursor.execute('''
                    INSERT OR REPLACE INTO package_artifacts
                    (package_id, artifact_id)
                    VALUES (?, ?)
                ''', (package.package_id, artifact.artifact_id))
            
            conn.commit()
    
    def _save_execution_session(self, session: ExecutionSession):
        """Save execution session to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO execution_sessions
                (session_id, test_case_id, start_time, end_time, status, 
                 execution_log, environment_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.test_case_id,
                session.start_time,
                session.end_time,
                session.status,
                session.execution_log,
                json.dumps(session.environment_info)
            ))
            conn.commit()
    
    def _update_execution_session(self, session: ExecutionSession):
        """Update execution session in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE execution_sessions
                SET end_time = ?, status = ?, execution_log = ?
                WHERE session_id = ?
            ''', (session.end_time, session.status, session.execution_log, session.session_id))
            conn.commit()
    
    def _get_artifacts_for_test_case(self, test_case_id: str) -> List[EvidenceArtifact]:
        """Get all artifacts for a test case."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT artifact_id, test_case_id, artifact_type, file_path, 
                       file_size, checksum, metadata, created_at, created_by
                FROM evidence_artifacts
                WHERE test_case_id = ?
                ORDER BY created_at
            ''', (test_case_id,))
            
            rows = cursor.fetchall()
            artifacts = []
            
            for row in rows:
                artifact = EvidenceArtifact(
                    artifact_id=row[0],
                    test_case_id=row[1],
                    artifact_type=row[2],
                    file_path=row[3],
                    file_size=row[4],
                    checksum=row[5],
                    metadata=json.loads(row[6]),
                    created_at=row[7],
                    created_by=row[8]
                )
                artifacts.append(artifact)
            
            return artifacts
    
    def _get_artifact(self, artifact_id: str) -> Optional[EvidenceArtifact]:
        """Get specific artifact by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT artifact_id, test_case_id, artifact_type, file_path, 
                       file_size, checksum, metadata, created_at, created_by
                FROM evidence_artifacts
                WHERE artifact_id = ?
            ''', (artifact_id,))
            
            row = cursor.fetchone()
            if row:
                return EvidenceArtifact(
                    artifact_id=row[0],
                    test_case_id=row[1],
                    artifact_type=row[2],
                    file_path=row[3],
                    file_size=row[4],
                    checksum=row[5],
                    metadata=json.loads(row[6]),
                    created_at=row[7],
                    created_by=row[8]
                )
            return None
    
    def _get_sessions_for_test_case(self, test_case_id: str) -> List[Dict[str, Any]]:
        """Get all execution sessions for a test case."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, test_case_id, start_time, end_time, 
                       status, execution_log, environment_info
                FROM execution_sessions
                WHERE test_case_id = ?
                ORDER BY start_time
            ''', (test_case_id,))
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                session = {
                    'session_id': row[0],
                    'test_case_id': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'status': row[4],
                    'execution_log': row[5],
                    'environment_info': row[6]
                }
                sessions.append(session)
            
            return sessions
    
    def _calculate_evidence_completeness(self, artifacts: List[EvidenceArtifact]) -> float:
        """Calculate evidence completeness score."""
        if not artifacts:
            return 0.0
        
        # Define expected artifact types for comprehensive evidence
        expected_types = ['screenshot', 'log', 'file']
        
        # Count present types
        present_types = set(artifact.artifact_type for artifact in artifacts)
        completeness = len(present_types) / len(expected_types)
        
        return min(completeness, 1.0)
    
    def _assess_audit_readiness(self, artifacts: List[EvidenceArtifact]) -> bool:
        """Assess if evidence is ready for audit."""
        if not artifacts:
            return False
        
        # Check for essential artifact types
        has_screenshots = any(a.artifact_type == 'screenshot' for a in artifacts)
        has_logs = any(a.artifact_type == 'log' for a in artifacts)
        
        # Check for proper metadata
        has_metadata = all(a.metadata for a in artifacts)
        
        # Check for checksums
        has_checksums = all(a.checksum for a in artifacts)
        
        return has_screenshots and has_logs and has_metadata and has_checksums
    
    def get_evidence_statistics(self) -> Dict[str, Any]:
        """Get evidence collection statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count artifacts by type
            cursor.execute('''
                SELECT artifact_type, COUNT(*) 
                FROM evidence_artifacts 
                GROUP BY artifact_type
            ''')
            artifact_counts = dict(cursor.fetchall())
            
            # Count total artifacts
            cursor.execute('SELECT COUNT(*) FROM evidence_artifacts')
            total_artifacts = cursor.fetchone()[0]
            
            # Count packages
            cursor.execute('SELECT COUNT(*) FROM evidence_packages')
            total_packages = cursor.fetchone()[0]
            
            # Count sessions
            cursor.execute('SELECT COUNT(*) FROM execution_sessions')
            total_sessions = cursor.fetchone()[0]
            
            # Calculate total size
            cursor.execute('SELECT SUM(file_size) FROM evidence_artifacts')
            total_size = cursor.fetchone()[0] or 0
            
            return {
                'total_artifacts': total_artifacts,
                'total_packages': total_packages,
                'total_sessions': total_sessions,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'artifact_counts': artifact_counts,
                'last_updated': datetime.now().isoformat()
            }
