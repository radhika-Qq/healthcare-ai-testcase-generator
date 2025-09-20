"""
AI-Driven Visual Regression Testing Module

Integrates screenshot capture and AI-powered visual comparison to detect
UI changes and generate/regenerate related visual test cases.
"""

import logging
import cv2
import numpy as np
import base64
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
from PIL import Image, ImageChops
import io
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


@dataclass
class VisualDifference:
    """Detected visual difference between screenshots."""
    difference_type: str  # layout, color, content, element
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    description: str
    severity: str  # low, medium, high, critical
    suggested_action: str


@dataclass
class VisualTestResult:
    """Result of visual regression test."""
    test_case_id: str
    baseline_image_path: str
    current_image_path: str
    difference_score: float
    differences: List[VisualDifference]
    status: str  # pass, fail, warning
    generated_at: str


@dataclass
class VisualTestCase:
    """Visual test case for UI elements."""
    test_case_id: str
    element_selector: str
    element_type: str
    baseline_image_path: str
    tolerance: float
    description: str
    created_at: str


class VisualRegressionEngine:
    """AI-driven visual regression testing engine."""
    
    def __init__(self, baseline_dir: str = "data/visual_baselines", 
                 model_path: str = "models/visual_model.h5"):
        """Initialize the visual regression engine."""
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(exist_ok=True)
        
        self.difference_model = None
        self.element_detector = None
        self.tolerance_thresholds = {
            'layout': 0.1,
            'color': 0.05,
            'content': 0.15,
            'element': 0.2
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models for visual analysis."""
        try:
            # Load or create difference detection model
            if self.model_path.exists():
                self.difference_model = keras.models.load_model(self.model_path)
                logger.info("Loaded existing visual difference model")
            else:
                self.difference_model = self._create_difference_model()
                logger.info("Created new visual difference model")
            
            # Initialize element detector (simplified version)
            self.element_detector = self._create_element_detector()
            
        except Exception as e:
            logger.error(f"Error initializing visual models: {e}")
            self.difference_model = None
            self.element_detector = None
    
    def _create_difference_model(self) -> keras.Model:
        """Create CNN model for visual difference detection."""
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(4, activation='softmax')  # layout, color, content, element
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_element_detector(self):
        """Create element detection model (simplified)."""
        # In a real implementation, this would use a pre-trained object detection model
        # like YOLO or R-CNN for detecting UI elements
        return None
    
    def capture_screenshot(self, driver: webdriver, element_selector: str = None) -> str:
        """Capture screenshot of page or specific element."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if element_selector:
                # Capture specific element
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
                )
                screenshot_path = self.baseline_dir / f"element_{timestamp}.png"
                element.screenshot(str(screenshot_path))
            else:
                # Capture full page
                screenshot_path = self.baseline_dir / f"fullpage_{timestamp}.png"
                driver.save_screenshot(str(screenshot_path))
            
            logger.info(f"Screenshot captured: {screenshot_path}")
            return str(screenshot_path)
            
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {element_selector}")
            return None
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def create_visual_test_case(self, test_case_id: str, element_selector: str, 
                              element_type: str, description: str, 
                              driver: webdriver) -> VisualTestCase:
        """Create a new visual test case."""
        try:
            # Capture baseline screenshot
            baseline_path = self.capture_screenshot(driver, element_selector)
            
            if not baseline_path:
                raise Exception("Failed to capture baseline screenshot")
            
            visual_test_case = VisualTestCase(
                test_case_id=test_case_id,
                element_selector=element_selector,
                element_type=element_type,
                baseline_image_path=baseline_path,
                tolerance=0.1,  # Default tolerance
                description=description,
                created_at=datetime.now().isoformat()
            )
            
            # Save test case metadata
            self._save_visual_test_case(visual_test_case)
            
            logger.info(f"Visual test case created: {test_case_id}")
            return visual_test_case
            
        except Exception as e:
            logger.error(f"Error creating visual test case: {e}")
            raise
    
    def run_visual_test(self, visual_test_case: VisualTestCase, 
                       driver: webdriver) -> VisualTestResult:
        """Run visual regression test."""
        try:
            # Capture current screenshot
            current_path = self.capture_screenshot(driver, visual_test_case.element_selector)
            
            if not current_path:
                raise Exception("Failed to capture current screenshot")
            
            # Compare images
            difference_score, differences = self._compare_images(
                visual_test_case.baseline_image_path,
                current_path,
                visual_test_case.tolerance
            )
            
            # Determine status
            status = self._determine_test_status(difference_score, differences)
            
            result = VisualTestResult(
                test_case_id=visual_test_case.test_case_id,
                baseline_image_path=visual_test_case.baseline_image_path,
                current_image_path=current_path,
                difference_score=difference_score,
                differences=differences,
                status=status,
                generated_at=datetime.now().isoformat()
            )
            
            # Save result
            self._save_visual_test_result(result)
            
            logger.info(f"Visual test completed: {visual_test_case.test_case_id} - {status}")
            return result
            
        except Exception as e:
            logger.error(f"Error running visual test: {e}")
            raise
    
    def _compare_images(self, baseline_path: str, current_path: str, 
                       tolerance: float) -> Tuple[float, List[VisualDifference]]:
        """Compare two images and detect differences."""
        try:
            # Load images
            baseline_img = cv2.imread(baseline_path)
            current_img = cv2.imread(current_path)
            
            if baseline_img is None or current_img is None:
                raise Exception("Failed to load images")
            
            # Resize images to same dimensions
            baseline_img = cv2.resize(baseline_img, (224, 224))
            current_img = cv2.resize(current_img, (224, 224))
            
            # Calculate basic difference
            diff = cv2.absdiff(baseline_img, current_img)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Calculate difference score
            difference_score = np.mean(diff_gray) / 255.0
            
            # Detect specific differences
            differences = self._detect_differences(baseline_img, current_img, diff)
            
            return difference_score, differences
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return 1.0, []
    
    def _detect_differences(self, baseline_img: np.ndarray, current_img: np.ndarray, 
                           diff_img: np.ndarray) -> List[VisualDifference]:
        """Detect specific types of differences."""
        differences = []
        
        try:
            # Convert to RGB for processing
            baseline_rgb = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2RGB)
            current_rgb = cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB)
            
            # Detect layout changes
            layout_diff = self._detect_layout_changes(baseline_rgb, current_rgb)
            if layout_diff:
                differences.append(layout_diff)
            
            # Detect color changes
            color_diff = self._detect_color_changes(baseline_rgb, current_rgb)
            if color_diff:
                differences.append(color_diff)
            
            # Detect content changes
            content_diff = self._detect_content_changes(baseline_rgb, current_rgb)
            if content_diff:
                differences.append(content_diff)
            
            # Detect element changes
            element_diff = self._detect_element_changes(baseline_rgb, current_rgb)
            if element_diff:
                differences.append(element_diff)
            
        except Exception as e:
            logger.error(f"Error detecting differences: {e}")
        
        return differences
    
    def _detect_layout_changes(self, baseline: np.ndarray, current: np.ndarray) -> Optional[VisualDifference]:
        """Detect layout changes using edge detection."""
        try:
            # Convert to grayscale
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_RGB2GRAY)
            current_gray = cv2.cvtColor(current, cv2.COLOR_RGB2GRAY)
            
            # Detect edges
            baseline_edges = cv2.Canny(baseline_gray, 50, 150)
            current_edges = cv2.Canny(current_gray, 50, 150)
            
            # Calculate edge difference
            edge_diff = cv2.absdiff(baseline_edges, current_edges)
            edge_score = np.mean(edge_diff) / 255.0
            
            if edge_score > self.tolerance_thresholds['layout']:
                return VisualDifference(
                    difference_type='layout',
                    confidence=edge_score,
                    bounding_box=(0, 0, baseline.shape[1], baseline.shape[0]),
                    description=f"Layout changes detected (score: {edge_score:.3f})",
                    severity='high' if edge_score > 0.3 else 'medium',
                    suggested_action="Review layout changes and update baseline if intentional"
                )
            
        except Exception as e:
            logger.error(f"Error detecting layout changes: {e}")
        
        return None
    
    def _detect_color_changes(self, baseline: np.ndarray, current: np.ndarray) -> Optional[VisualDifference]:
        """Detect color changes using histogram comparison."""
        try:
            # Calculate color histograms
            baseline_hist = cv2.calcHist([baseline], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            current_hist = cv2.calcHist([current], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            # Compare histograms
            color_score = cv2.compareHist(baseline_hist, current_hist, cv2.HISTCMP_CORREL)
            color_diff = 1 - color_score
            
            if color_diff > self.tolerance_thresholds['color']:
                return VisualDifference(
                    difference_type='color',
                    confidence=color_diff,
                    bounding_box=(0, 0, baseline.shape[1], baseline.shape[0]),
                    description=f"Color changes detected (score: {color_diff:.3f})",
                    severity='medium' if color_diff > 0.1 else 'low',
                    suggested_action="Review color scheme changes and update baseline if intentional"
                )
            
        except Exception as e:
            logger.error(f"Error detecting color changes: {e}")
        
        return None
    
    def _detect_content_changes(self, baseline: np.ndarray, current: np.ndarray) -> Optional[VisualDifference]:
        """Detect content changes using template matching."""
        try:
            # Convert to grayscale
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_RGB2GRAY)
            current_gray = cv2.cvtColor(current, cv2.COLOR_RGB2GRAY)
            
            # Use template matching to find differences
            diff = cv2.absdiff(baseline_gray, current_gray)
            content_score = np.mean(diff) / 255.0
            
            if content_score > self.tolerance_thresholds['content']:
                # Find bounding box of differences
                contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                    bounding_box = (x, y, w, h)
                else:
                    bounding_box = (0, 0, baseline.shape[1], baseline.shape[0])
                
                return VisualDifference(
                    difference_type='content',
                    confidence=content_score,
                    bounding_box=bounding_box,
                    description=f"Content changes detected (score: {content_score:.3f})",
                    severity='high' if content_score > 0.3 else 'medium',
                    suggested_action="Review content changes and update baseline if intentional"
                )
            
        except Exception as e:
            logger.error(f"Error detecting content changes: {e}")
        
        return None
    
    def _detect_element_changes(self, baseline: np.ndarray, current: np.ndarray) -> Optional[VisualDifference]:
        """Detect element changes using feature matching."""
        try:
            # Convert to grayscale
            baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_RGB2GRAY)
            current_gray = cv2.cvtColor(current, cv2.COLOR_RGB2GRAY)
            
            # Use ORB feature detector
            orb = cv2.ORB_create()
            kp1, des1 = orb.detectAndCompute(baseline_gray, None)
            kp2, des2 = orb.detectAndCompute(current_gray, None)
            
            if des1 is not None and des2 is not None:
                # Match features
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(des1, des2)
                matches = sorted(matches, key=lambda x: x.distance)
                
                # Calculate match ratio
                good_matches = [m for m in matches if m.distance < 50]
                match_ratio = len(good_matches) / len(matches) if matches else 0
                element_score = 1 - match_ratio
                
                if element_score > self.tolerance_thresholds['element']:
                    return VisualDifference(
                        difference_type='element',
                        confidence=element_score,
                        bounding_box=(0, 0, baseline.shape[1], baseline.shape[0]),
                        description=f"Element changes detected (score: {element_score:.3f})",
                        severity='high' if element_score > 0.4 else 'medium',
                        suggested_action="Review element changes and update baseline if intentional"
                    )
            
        except Exception as e:
            logger.error(f"Error detecting element changes: {e}")
        
        return None
    
    def _determine_test_status(self, difference_score: float, 
                              differences: List[VisualDifference]) -> str:
        """Determine test status based on differences."""
        if difference_score < 0.05:
            return 'pass'
        elif difference_score < 0.15:
            # Check if differences are acceptable
            critical_diffs = [d for d in differences if d.severity == 'critical']
            if critical_diffs:
                return 'fail'
            else:
                return 'warning'
        else:
            return 'fail'
    
    def generate_visual_test_cases(self, page_elements: List[Dict[str, Any]], 
                                 driver: webdriver) -> List[VisualTestCase]:
        """Generate visual test cases for page elements."""
        visual_test_cases = []
        
        for element in page_elements:
            try:
                test_case = self.create_visual_test_case(
                    test_case_id=element.get('id', f"visual_{len(visual_test_cases)}"),
                    element_selector=element.get('selector'),
                    element_type=element.get('type', 'generic'),
                    description=element.get('description', 'Visual test case'),
                    driver=driver
                )
                visual_test_cases.append(test_case)
                
            except Exception as e:
                logger.error(f"Error creating visual test case for {element}: {e}")
        
        return visual_test_cases
    
    def update_baseline(self, visual_test_case: VisualTestCase, 
                       new_baseline_path: str):
        """Update baseline image for a visual test case."""
        try:
            # Copy new baseline
            baseline_path = Path(visual_test_case.baseline_image_path)
            new_path = Path(new_baseline_path)
            
            if new_path.exists():
                baseline_path.parent.mkdir(exist_ok=True)
                baseline_path.write_bytes(new_path.read_bytes())
                
                # Update test case
                visual_test_case.baseline_image_path = str(baseline_path)
                self._save_visual_test_case(visual_test_case)
                
                logger.info(f"Baseline updated for {visual_test_case.test_case_id}")
            else:
                raise Exception(f"New baseline image not found: {new_baseline_path}")
                
        except Exception as e:
            logger.error(f"Error updating baseline: {e}")
            raise
    
    def _save_visual_test_case(self, visual_test_case: VisualTestCase):
        """Save visual test case metadata."""
        test_case_path = self.baseline_dir / f"{visual_test_case.test_case_id}.json"
        
        data = {
            'test_case_id': visual_test_case.test_case_id,
            'element_selector': visual_test_case.element_selector,
            'element_type': visual_test_case.element_type,
            'baseline_image_path': visual_test_case.baseline_image_path,
            'tolerance': visual_test_case.tolerance,
            'description': visual_test_case.description,
            'created_at': visual_test_case.created_at
        }
        
        with open(test_case_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_visual_test_result(self, result: VisualTestResult):
        """Save visual test result."""
        result_path = self.baseline_dir / f"{result.test_case_id}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'test_case_id': result.test_case_id,
            'baseline_image_path': result.baseline_image_path,
            'current_image_path': result.current_image_path,
            'difference_score': result.difference_score,
            'differences': [
                {
                    'difference_type': diff.difference_type,
                    'confidence': diff.confidence,
                    'bounding_box': diff.bounding_box,
                    'description': diff.description,
                    'severity': diff.severity,
                    'suggested_action': diff.suggested_action
                }
                for diff in result.differences
            ],
            'status': result.status,
            'generated_at': result.generated_at
        }
        
        with open(result_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_visual_test_statistics(self) -> Dict[str, Any]:
        """Get statistics about visual tests."""
        try:
            # Count test cases
            test_case_files = list(self.baseline_dir.glob("*.json"))
            test_cases = [f for f in test_case_files if not f.name.endswith('_result_')]
            result_files = [f for f in test_case_files if f.name.endswith('_result_')]
            
            # Analyze results
            pass_count = 0
            fail_count = 0
            warning_count = 0
            
            for result_file in result_files:
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                    
                    status = data.get('status', 'unknown')
                    if status == 'pass':
                        pass_count += 1
                    elif status == 'fail':
                        fail_count += 1
                    elif status == 'warning':
                        warning_count += 1
                        
                except Exception as e:
                    logger.error(f"Error reading result file {result_file}: {e}")
            
            total_tests = pass_count + fail_count + warning_count
            pass_rate = pass_count / total_tests if total_tests > 0 else 0
            
            return {
                'total_test_cases': len(test_cases),
                'total_results': total_tests,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'warning_count': warning_count,
                'pass_rate': pass_rate,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting visual test statistics: {e}")
            return {'error': str(e)}
