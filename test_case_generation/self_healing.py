"""
Self-Healing Test Cases Module

Implements logic to detect UI/API changes using historical execution results
and automatically adjust test case steps or selectors.
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import re
import difflib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ChangeDetection:
    """Detected change in UI/API."""
    change_type: str  # ui_element, api_endpoint, response_structure
    element_path: str
    old_value: str
    new_value: str
    confidence: float
    change_description: str
    detected_at: str


@dataclass
class HealAction:
    """Action taken to heal a test case."""
    test_case_id: str
    step_number: int
    action_type: str  # update_selector, update_endpoint, update_assertion
    old_content: str
    new_content: str
    confidence: float
    reason: str
    healed_at: str


@dataclass
class ExecutionResult:
    """Test case execution result."""
    test_case_id: str
    step_number: int
    action: str
    expected_result: str
    actual_result: str
    status: str  # pass, fail, error
    execution_time: str
    screenshot_path: Optional[str] = None
    error_message: Optional[str] = None


class SelfHealingEngine:
    """Self-healing test case engine."""
    
    def __init__(self, history_path: str = "data/execution_history.json"):
        """Initialize the self-healing engine."""
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(exist_ok=True)
        self.execution_history = self._load_execution_history()
        self.change_patterns = self._initialize_change_patterns()
        self.healing_rules = self._initialize_healing_rules()
        
    def _load_execution_history(self) -> List[ExecutionResult]:
        """Load execution history from file."""
        if not self.history_path.exists():
            return []
        
        try:
            with open(self.history_path, 'r') as f:
                data = json.load(f)
            
            return [
                ExecutionResult(**item) for item in data
            ]
        except Exception as e:
            logger.error(f"Error loading execution history: {e}")
            return []
    
    def _save_execution_history(self):
        """Save execution history to file."""
        try:
            data = [
                {
                    'test_case_id': result.test_case_id,
                    'step_number': result.step_number,
                    'action': result.action,
                    'expected_result': result.expected_result,
                    'actual_result': result.actual_result,
                    'status': result.status,
                    'execution_time': result.execution_time,
                    'screenshot_path': result.screenshot_path,
                    'error_message': result.error_message
                }
                for result in self.execution_history
            ]
            
            with open(self.history_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving execution history: {e}")
    
    def _initialize_change_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting changes."""
        return {
            'ui_element_changes': [
                r'element.*not.*found',
                r'selector.*invalid',
                r'element.*not.*clickable',
                r'element.*not.*visible',
                r'stale.*element'
            ],
            'api_endpoint_changes': [
                r'404.*not.*found',
                r'endpoint.*not.*found',
                r'url.*not.*found',
                r'invalid.*endpoint'
            ],
            'response_structure_changes': [
                r'key.*not.*found',
                r'field.*missing',
                r'response.*format.*changed',
                r'json.*parsing.*error'
            ]
        }
    
    def _initialize_healing_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize healing rules for different change types."""
        return {
            'ui_element_changes': {
                'strategies': [
                    'update_selector',
                    'find_alternative_selector',
                    'update_wait_conditions'
                ],
                'confidence_threshold': 0.7
            },
            'api_endpoint_changes': {
                'strategies': [
                    'update_endpoint_url',
                    'find_alternative_endpoint',
                    'update_headers'
                ],
                'confidence_threshold': 0.8
            },
            'response_structure_changes': {
                'strategies': [
                    'update_json_path',
                    'update_assertion',
                    'add_missing_fields'
                ],
                'confidence_threshold': 0.6
            }
        }
    
    def record_execution_result(self, result: ExecutionResult):
        """Record test execution result for analysis."""
        self.execution_history.append(result)
        self._save_execution_history()
        
        # Analyze for potential changes
        if result.status == 'fail':
            self._analyze_failure(result)
    
    def _analyze_failure(self, result: ExecutionResult):
        """Analyze test failure for potential changes."""
        error_message = result.error_message or result.actual_result
        
        for change_type, patterns in self.change_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    change = self._detect_change(change_type, result, pattern)
                    if change:
                        self._attempt_healing(change, result)
                    break
    
    def _detect_change(self, change_type: str, result: ExecutionResult, pattern: str) -> Optional[ChangeDetection]:
        """Detect specific change based on error pattern."""
        try:
            if change_type == 'ui_element_changes':
                return self._detect_ui_element_change(result, pattern)
            elif change_type == 'api_endpoint_changes':
                return self._detect_api_endpoint_change(result, pattern)
            elif change_type == 'response_structure_changes':
                return self._detect_response_structure_change(result, pattern)
        except Exception as e:
            logger.error(f"Error detecting change: {e}")
        
        return None
    
    def _detect_ui_element_change(self, result: ExecutionResult, pattern: str) -> Optional[ChangeDetection]:
        """Detect UI element changes."""
        # Extract selector from action
        action = result.action
        selector_match = re.search(r'selector[:\s]+([^\s]+)', action, re.IGNORECASE)
        
        if not selector_match:
            return None
        
        old_selector = selector_match.group(1)
        
        # Try to find alternative selector
        new_selector = self._find_alternative_selector(old_selector, result)
        
        if new_selector and new_selector != old_selector:
            return ChangeDetection(
                change_type='ui_element',
                element_path=old_selector,
                old_value=old_selector,
                new_value=new_selector,
                confidence=0.8,
                change_description=f"Element selector changed from {old_selector} to {new_selector}",
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_api_endpoint_change(self, result: ExecutionResult, pattern: str) -> Optional[ChangeDetection]:
        """Detect API endpoint changes."""
        # Extract URL from action
        url_match = re.search(r'https?://[^\s]+', result.action)
        
        if not url_match:
            return None
        
        old_url = url_match.group(0)
        
        # Try to find alternative endpoint
        new_url = self._find_alternative_endpoint(old_url, result)
        
        if new_url and new_url != old_url:
            return ChangeDetection(
                change_type='api_endpoint',
                element_path=old_url,
                old_value=old_url,
                new_value=new_url,
                confidence=0.9,
                change_description=f"API endpoint changed from {old_url} to {new_url}",
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_response_structure_change(self, result: ExecutionResult, pattern: str) -> Optional[ChangeDetection]:
        """Detect response structure changes."""
        # This would require more sophisticated analysis
        # For now, return a generic change detection
        return ChangeDetection(
            change_type='response_structure',
            element_path='response',
            old_value='unknown',
            new_value='modified',
            confidence=0.6,
            change_description="Response structure may have changed",
            detected_at=datetime.now().isoformat()
        )
    
    def _find_alternative_selector(self, old_selector: str, result: ExecutionResult) -> Optional[str]:
        """Find alternative selector for UI element."""
        try:
            # This would require actual browser interaction
            # For demo purposes, return a modified selector
            if 'id=' in old_selector:
                # Try class-based selector
                return old_selector.replace('id=', 'class=')
            elif 'class=' in old_selector:
                # Try xpath
                return f"//*[@class='{old_selector.split('=')[1]}']"
            else:
                # Try different approach
                return f"//*[contains(text(), '{old_selector}')]"
        except Exception as e:
            logger.error(f"Error finding alternative selector: {e}")
            return None
    
    def _find_alternative_endpoint(self, old_url: str, result: ExecutionResult) -> Optional[str]:
        """Find alternative API endpoint."""
        try:
            # Try common endpoint variations
            variations = [
                old_url.replace('/api/v1/', '/api/v2/'),
                old_url.replace('/api/v2/', '/api/v1/'),
                old_url.replace('/api/', '/api/v1/'),
                old_url.replace('/v1/', '/v2/'),
                old_url.replace('/v2/', '/v1/')
            ]
            
            for variation in variations:
                if self._test_endpoint(variation):
                    return variation
            
            return None
        except Exception as e:
            logger.error(f"Error finding alternative endpoint: {e}")
            return None
    
    def _test_endpoint(self, url: str) -> bool:
        """Test if an endpoint is accessible."""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    def _attempt_healing(self, change: ChangeDetection, result: ExecutionResult):
        """Attempt to heal test case based on detected change."""
        healing_rules = self.healing_rules.get(change.change_type, {})
        confidence_threshold = healing_rules.get('confidence_threshold', 0.5)
        
        if change.confidence < confidence_threshold:
            logger.info(f"Change confidence {change.confidence} below threshold {confidence_threshold}")
            return
        
        strategies = healing_rules.get('strategies', [])
        
        for strategy in strategies:
            heal_action = self._apply_healing_strategy(strategy, change, result)
            if heal_action:
                self._record_heal_action(heal_action)
                self._notify_healing(heal_action)
                break
    
    def _apply_healing_strategy(self, strategy: str, change: ChangeDetection, result: ExecutionResult) -> Optional[HealAction]:
        """Apply specific healing strategy."""
        try:
            if strategy == 'update_selector':
                return self._update_selector(change, result)
            elif strategy == 'update_endpoint_url':
                return self._update_endpoint_url(change, result)
            elif strategy == 'update_json_path':
                return self._update_json_path(change, result)
            elif strategy == 'update_assertion':
                return self._update_assertion(change, result)
        except Exception as e:
            logger.error(f"Error applying healing strategy {strategy}: {e}")
        
        return None
    
    def _update_selector(self, change: ChangeDetection, result: ExecutionResult) -> Optional[HealAction]:
        """Update element selector in test case."""
        old_action = result.action
        new_action = old_action.replace(change.old_value, change.new_value)
        
        return HealAction(
            test_case_id=result.test_case_id,
            step_number=result.step_number,
            action_type='update_selector',
            old_content=old_action,
            new_content=new_action,
            confidence=change.confidence,
            reason=f"Updated selector from {change.old_value} to {change.new_value}",
            healed_at=datetime.now().isoformat()
        )
    
    def _update_endpoint_url(self, change: ChangeDetection, result: ExecutionResult) -> Optional[HealAction]:
        """Update API endpoint URL in test case."""
        old_action = result.action
        new_action = old_action.replace(change.old_value, change.new_value)
        
        return HealAction(
            test_case_id=result.test_case_id,
            step_number=result.step_number,
            action_type='update_endpoint',
            old_content=old_action,
            new_content=new_action,
            confidence=change.confidence,
            reason=f"Updated endpoint from {change.old_value} to {change.new_value}",
            healed_at=datetime.now().isoformat()
        )
    
    def _update_json_path(self, change: ChangeDetection, result: ExecutionResult) -> Optional[HealAction]:
        """Update JSON path in test case."""
        # This would require more sophisticated JSON path analysis
        return HealAction(
            test_case_id=result.test_case_id,
            step_number=result.step_number,
            action_type='update_json_path',
            old_content=result.expected_result,
            new_content=result.expected_result + " (updated for structure change)",
            confidence=change.confidence,
            reason="Updated JSON path for response structure change",
            healed_at=datetime.now().isoformat()
        )
    
    def _update_assertion(self, change: ChangeDetection, result: ExecutionResult) -> Optional[HealAction]:
        """Update assertion in test case."""
        old_assertion = result.expected_result
        new_assertion = self._generate_new_assertion(old_assertion, result.actual_result)
        
        return HealAction(
            test_case_id=result.test_case_id,
            step_number=result.step_number,
            action_type='update_assertion',
            old_content=old_assertion,
            new_content=new_assertion,
            confidence=change.confidence,
            reason="Updated assertion based on actual result",
            healed_at=datetime.now().isoformat()
        )
    
    def _generate_new_assertion(self, old_assertion: str, actual_result: str) -> str:
        """Generate new assertion based on actual result."""
        # Simple assertion update logic
        if "contains" in old_assertion.lower():
            return f"Response contains: {actual_result[:100]}..."
        elif "equals" in old_assertion.lower():
            return f"Response equals: {actual_result}"
        else:
            return f"Response matches: {actual_result[:100]}..."
    
    def _record_heal_action(self, heal_action: HealAction):
        """Record healing action for tracking."""
        heal_log_path = self.history_path.parent / "heal_actions.json"
        
        try:
            if heal_log_path.exists():
                with open(heal_log_path, 'r') as f:
                    heal_actions = json.load(f)
            else:
                heal_actions = []
            
            heal_actions.append({
                'test_case_id': heal_action.test_case_id,
                'step_number': heal_action.step_number,
                'action_type': heal_action.action_type,
                'old_content': heal_action.old_content,
                'new_content': heal_action.new_content,
                'confidence': heal_action.confidence,
                'reason': heal_action.reason,
                'healed_at': heal_action.healed_at
            })
            
            with open(heal_log_path, 'w') as f:
                json.dump(heal_actions, f, indent=2)
                
            logger.info(f"Heal action recorded: {heal_action.action_type} for {heal_action.test_case_id}")
        except Exception as e:
            logger.error(f"Error recording heal action: {e}")
    
    def _notify_healing(self, heal_action: HealAction):
        """Notify users about healing action."""
        notification = {
            'type': 'test_case_healed',
            'test_case_id': heal_action.test_case_id,
            'action_type': heal_action.action_type,
            'confidence': heal_action.confidence,
            'reason': heal_action.reason,
            'timestamp': heal_action.healed_at
        }
        
        # In a real implementation, this would send notifications
        # via email, Slack, or other notification systems
        logger.info(f"HEALING NOTIFICATION: {notification}")
    
    def get_healing_statistics(self) -> Dict[str, Any]:
        """Get statistics about healing actions."""
        heal_log_path = self.history_path.parent / "heal_actions.json"
        
        if not heal_log_path.exists():
            return {'total_heals': 0, 'heal_types': {}, 'success_rate': 0.0}
        
        try:
            with open(heal_log_path, 'r') as f:
                heal_actions = json.load(f)
            
            total_heals = len(heal_actions)
            heal_types = {}
            
            for action in heal_actions:
                action_type = action['action_type']
                heal_types[action_type] = heal_types.get(action_type, 0) + 1
            
            # Calculate success rate based on confidence
            high_confidence_heals = sum(1 for action in heal_actions if action['confidence'] > 0.7)
            success_rate = high_confidence_heals / total_heals if total_heals > 0 else 0.0
            
            return {
                'total_heals': total_heals,
                'heal_types': heal_types,
                'success_rate': success_rate,
                'recent_heals': heal_actions[-5:] if heal_actions else []
            }
        except Exception as e:
            logger.error(f"Error getting healing statistics: {e}")
            return {'error': str(e)}
    
    def suggest_healing_improvements(self) -> List[str]:
        """Suggest improvements to healing capabilities."""
        suggestions = []
        
        # Analyze failure patterns
        recent_failures = [r for r in self.execution_history if r.status == 'fail']
        
        if len(recent_failures) > 10:
            # Check for common failure patterns
            error_patterns = {}
            for failure in recent_failures:
                error_msg = failure.error_message or failure.actual_result
                for pattern in self.change_patterns['ui_element_changes']:
                    if re.search(pattern, error_msg, re.IGNORECASE):
                        error_patterns[pattern] = error_patterns.get(pattern, 0) + 1
            
            # Suggest improvements for common patterns
            for pattern, count in error_patterns.items():
                if count > 3:
                    suggestions.append(f"Consider improving selector strategy for pattern: {pattern}")
        
        # Check healing success rate
        stats = self.get_healing_statistics()
        if stats.get('success_rate', 0) < 0.7:
            suggestions.append("Consider improving healing confidence thresholds")
        
        return suggestions
