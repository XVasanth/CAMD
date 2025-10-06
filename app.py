"""
CAD Educational Assessment System
Complete Streamlit application for CAD model evaluation and plagiarism detection
Run locally with: streamlit run app.py
"""

import streamlit as st
import os
import numpy as np
import trimesh
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.neighbors import NearestNeighbors
import warnings
import tempfile
import re
from collections import defaultdict
import json
import base64
from io import BytesIO
import zipfile

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="CAD Educational Assessment System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        margin: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = {}
if 'plagiarism_results' not in st.session_state:
    st.session_state.plagiarism_results = None
if 'teacher_model' not in st.session_state:
    st.session_state.teacher_model = None
if 'student_models' not in st.session_state:
    st.session_state.student_models = {}

class CADEvaluationSystem:
    """Educational CAD model evaluation system using geometric analysis"""
    
    def __init__(self):
        self.supported_formats = ['.obj', '.stl', '.ply', '.off']
        
        # Grading thresholds (in model units)
        self.grading_thresholds = {
            'A': 0.1,   # ≤0.1mm deviation = A (95-100%)
            'B': 0.5,   # ≤0.5mm deviation = B (85-94%)  
            'C': 1.0,   # ≤1.0mm deviation = C (75-84%)
            'D': 2.0,   # ≤2.0mm deviation = D (65-74%)
            'F': float('inf')  # >2.0mm deviation = F (<65%)
        }
        
        # Detailed scoring within grades
        self.detailed_scoring = {
            'A': (95, 100),
            'B': (85, 94),
            'C': (75, 84), 
            'D': (65, 74),
            'F': (0, 64)
        }
    
    def load_mesh(self, file_data, file_name):
        """Load mesh from uploaded file data"""
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp:
                tmp.write(file_data.getbuffer())
                tmp_path = tmp.name
            
            # Load with trimesh
            loaded = trimesh.load(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Handle Scene objects
            if isinstance(loaded, trimesh.Scene):
                if len(loaded.geometry) == 0:
                    raise Exception("No geometry found")
                elif len(loaded.geometry) == 1:
                    return list(loaded.geometry.values())[0]
                else:
                    return loaded.dump(concatenate=True)
            return loaded
            
        except Exception as e:
            st.error(f"Error loading {file_name}: {str(e)}")
            return None
    
    def extract_point_cloud(self, mesh: trimesh.Trimesh, num_points: int = 2048) -> np.ndarray:
        """Extract point cloud from mesh"""
        if mesh.is_watertight:
            points, _ = trimesh.sample.sample_surface(mesh, num_points)
        else:
            if len(mesh.vertices) >= num_points:
                indices = np.random.choice(len(mesh.vertices), num_points, replace=False)
                points = mesh.vertices[indices]
            else:
                indices = np.random.choice(len(mesh.vertices), num_points, replace=True)
                points = mesh.vertices[indices]
        
        # Normalize to unit sphere
        points = points - np.mean(points, axis=0)
        scale = np.max(np.sqrt(np.sum(points**2, axis=1)))
        if scale > 0:
            points = points / scale
        
        return points.astype(np.float32)
    
    def compute_geometric_differences(self, teacher_points: np.ndarray, 
                                     student_points: np.ndarray) -> Dict[str, Any]:
        """Compute detailed geometric differences"""
        
        # Find nearest neighbors
        nn_teacher_to_student = NearestNeighbors(n_neighbors=1)
        nn_teacher_to_student.fit(student_points)
        distances_t_to_s, _ = nn_teacher_to_student.kneighbors(teacher_points)
        
        nn_student_to_teacher = NearestNeighbors(n_neighbors=1)
        nn_student_to_teacher.fit(teacher_points)
        distances_s_to_t, _ = nn_student_to_teacher.kneighbors(student_points)
        
        distances_t_to_s = distances_t_to_s.flatten()
        distances_s_to_t = distances_s_to_t.flatten()
        
        return {
            'teacher_to_student_distances': distances_t_to_s,
            'student_to_teacher_distances': distances_s_to_t,
            'mean_deviation': np.mean(distances_t_to_s),
            'max_deviation': np.max(distances_t_to_s),
            'std_deviation': np.std(distances_t_to_s),
            'median_deviation': np.median(distances_t_to_s),
            'percentile_95': np.percentile(distances_t_to_s, 95),
            'percentile_99': np.percentile(distances_t_to_s, 99),
            'hausdorff_distance': max(np.max(distances_t_to_s), np.max(distances_s_to_t))
        }
    
    def calculate_grade(self, geometric_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate letter grade and numerical score"""
        
        mean_dev = geometric_results['mean_deviation']
        max_dev = geometric_results['max_deviation']
        
        # Determine letter grade
        letter_grade = 'F'
        for grade, threshold in self.grading_thresholds.items():
            if mean_dev <= threshold:
                letter_grade = grade
                break
        
        # Calculate numerical score
        min_score, max_score = self.detailed_scoring[letter_grade]
        
        if letter_grade == 'A':
            score_factor = max(0, 1 - (mean_dev / self.grading_thresholds['A']))
            numerical_score = min_score + (max_score - min_score) * score_factor
        elif letter_grade == 'F':
            numerical_score = max(0, min_score - (mean_dev * 10))
        else:
            prev_grade = list(self.grading_thresholds.keys())[
                list(self.grading_thresholds.keys()).index(letter_grade) - 1]
            prev_threshold = self.grading_thresholds[prev_grade]
            curr_threshold = self.grading_thresholds[letter_grade]
            
            score_factor = (curr_threshold - mean_dev) / (curr_threshold - prev_threshold)
            numerical_score = min_score + (max_score - min_score) * score_factor
        
        # Penalties for outliers
        if max_dev > 5.0:
            numerical_score -= 10
        elif max_dev > 3.0:
            numerical_score -= 5
        
        numerical_score = max(0, min(100, numerical_score))
        
        return {
            'letter_grade': letter_grade,
            'numerical_score': round(numerical_score, 1),
            'mean_deviation': mean_dev,
            'max_deviation': max_dev,
            'grading_threshold_used': self.grading_thresholds[letter_grade]
        }
    
    def create_evaluation_heatmap(self, points: np.ndarray, deviations: np.ndarray,
                                 title: str = "Geometric Accuracy Heatmap") -> go.Figure:
        """Create interactive 3D heatmap"""
        
        fig = go.Figure(data=[go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1], 
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=4,
                color=deviations,
                colorscale='RdYlGn_r',
                opacity=0.8,
                colorbar=dict(title="Deviation"),
                cmin=0,
                cmax=np.percentile(deviations, 95)
            ),
            text=[f'Deviation: {d:.4f}' for d in deviations],
            hovertemplate='<b>Point</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<br>%{text}<extra></extra>'
        )])
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y', 
                zaxis_title='Z',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=600
        )
        
        return fig


class MetadataPlagiarismDetector:
    """Detect plagiarism by analyzing CAD file metadata"""
    
    def __init__(self):
        self.suspicion_threshold = 70
    
    def extract_file_metadata(self, file_data, file_name) -> Dict[str, Any]:
        """Extract metadata from uploaded file"""
        metadata = {
            'file_name': file_name,
            'file_size': len(file_data.getbuffer()),
            'file_hash': hashlib.md5(file_data.getbuffer()).hexdigest(),
            'upload_time': datetime.now()
        }
        return metadata
    
    def analyze_timestamp_patterns(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect suspicious patterns across submissions"""
        suspicious_pairs = []
        
        for i, sub1 in enumerate(submissions):
            for j, sub2 in enumerate(submissions[i+1:], i+1):
                suspicion_score = 0
                reasons = []
                
                # Check file sizes
                size_diff = abs(sub1['file_size'] - sub2['file_size'])
                if size_diff == 0:
                    suspicion_score += 60
                    reasons.append("Identical file size")
                elif size_diff < 1024:
                    suspicion_score += 35
                    reasons.append(f"Nearly identical size (diff: {size_diff} bytes)")
                
                # Check file hash
                if sub1['file_hash'] == sub2['file_hash']:
                    suspicion_score += 100
                    reasons.append("⚠️ EXACT COPY - Identical file hash!")
                
                # Check upload time
                time_diff = abs((sub1['upload_time'] - sub2['upload_time']).total_seconds())
                if time_diff < 300:  # 5 minutes
                    suspicion_score += 40
                    reasons.append(f"Uploaded {int(time_diff/60)} minutes apart")
                
                if suspicion_score >= self.suspicion_threshold:
                    suspicious_pairs.append({
                        'student1': sub1['file_name'],
                        'student2': sub2['file_name'],
                        'suspicion_score': suspicion_score,
                        'reasons': reasons,
                        'severity': self._get_severity(suspicion_score)
                    })
        
        return sorted(suspicious_pairs, key=lambda x: x['suspicion_score'], reverse=True)
    
    def _get_severity(self, score: int) -> str:
        """Determine severity level"""
        if score >= 100:
            return "🚨 CRITICAL - Exact Copy"
        elif score >= 90:
            return "🔴 VERY HIGH"
        elif score >= 80:
            return "🟠 HIGH"
        elif score >= 70:
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"


def generate_student_report(student_name: str, teacher_model, student_model,
                           evaluation_results: Dict, plagiarism_info: Dict) -> str:
    """Generate individual student report"""
    
    report = f"""
# CAD ASSESSMENT REPORT
## Student: {student_name}
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 GEOMETRIC ACCURACY EVALUATION

### Overall Performance
- **Grade:** {evaluation_results['grade']['letter_grade']} ({evaluation_results['grade']['numerical_score']}%)
- **Mean Deviation:** {evaluation_results['geometric_analysis']['mean_deviation']:.4f} units
- **Maximum Deviation:** {evaluation_results['geometric_analysis']['max_deviation']:.4f} units
- **Standard Deviation:** {evaluation_results['geometric_analysis']['std_deviation']:.4f} units

### Detailed Metrics
- **Median Deviation:** {evaluation_results['geometric_analysis']['median_deviation']:.4f} units
- **95th Percentile:** {evaluation_results['geometric_analysis']['percentile_95']:.4f} units
- **99th Percentile:** {evaluation_results['geometric_analysis']['percentile_99']:.4f} units
- **Hausdorff Distance:** {evaluation_results['geometric_analysis']['hausdorff_distance']:.4f} units

### Assessment Summary
"""
    
    grade = evaluation_results['grade']['letter_grade']
    if grade == 'A':
        report += "✅ **Excellent Work!** Model shows exceptional accuracy with professional-level precision.\n"
    elif grade == 'B':
        report += "✅ **Good Work!** Most dimensions are accurate with minor areas for improvement.\n"
    elif grade == 'C':
        report += "⚠️ **Acceptable.** Basic geometry is correct but lacks precision in several areas.\n"
    elif grade == 'D':
        report += "⚠️ **Needs Improvement.** Significant geometric inaccuracies detected.\n"
    else:
        report += "❌ **Unsatisfactory.** Major geometric problems require complete revision.\n"
    
    report += f"""
---

## 🔍 PLAGIARISM CHECK

### Similarity Analysis
"""
    
    if plagiarism_info and 'suspicious_matches' in plagiarism_info:
        if plagiarism_info['suspicious_matches']:
            report += "⚠️ **Potential Issues Detected:**\n"
            for match in plagiarism_info['suspicious_matches']:
                report += f"- Similar to: {match['similar_to']}\n"
                report += f"  - Suspicion Score: {match['score']}%\n"
                report += f"  - Severity: {match['severity']}\n"
                report += f"  - Evidence: {', '.join(match['reasons'])}\n\n"
        else:
            report += "✅ **No plagiarism detected.** Work appears to be original.\n"
    else:
        report += "✅ **No plagiarism detected.** Work appears to be original.\n"
    
    report += f"""
---

## 📈 IMPROVEMENT RECOMMENDATIONS

1. **Dimensional Accuracy:** """
    
    if evaluation_results['geometric_analysis']['std_deviation'] > 0.5:
        report += "Focus on consistent precision throughout the model.\n"
    else:
        report += "Maintain current level of precision.\n"
    
    report += "2. **Critical Features:** "
    if evaluation_results['geometric_analysis']['max_deviation'] > 2 * evaluation_results['geometric_analysis']['mean_deviation']:
        report += "Check for missing or misplaced features.\n"
    else:
        report += "All features appear correctly placed.\n"
    
    report += """3. **Modeling Technique:** Review workflow for areas with highest deviation.

---

## 📋 GRADING SCALE REFERENCE
- **A Grade:** ≤0.1 units mean deviation (95-100%)
- **B Grade:** ≤0.5 units mean deviation (85-94%)
- **C Grade:** ≤1.0 units mean deviation (75-84%)
- **D Grade:** ≤2.0 units mean deviation (65-74%)
- **F Grade:** >2.0 units mean deviation (<65%)

---

*Report generated by CAD Educational Assessment System*
"""
    
    return report


def main():
    st.title("🎓 CAD Educational Assessment System")
    st.markdown("### Complete evaluation and plagiarism detection for CAD assignments")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio("Select Mode", 
                            ["📤 Upload Models", "📊 Evaluate Students", 
                             "🔍 Plagiarism Check", "📋 Generate Reports"])
    
    # Initialize systems
    evaluator = CADEvaluationSystem()
    plagiarism_detector = MetadataPlagiarismDetector()
    
    if mode == "📤 Upload Models":
        st.header("Upload CAD Models")
        
        # Teacher model upload
        st.subheader("Teacher Reference Model")
        teacher_file = st.file_uploader("Upload teacher's reference CAD model",
                                       type=['obj', 'stl', 'ply', 'off','STEP'],
                                       key="teacher")
        
        if teacher_file:
            with st.spinner("Loading teacher model..."):
                teacher_mesh = evaluator.load_mesh(teacher_file, teacher_file.name)
                if teacher_mesh:
                    st.session_state.teacher_model = {
                        'mesh': teacher_mesh,
                        'name': teacher_file.name,
                        'data': teacher_file
                    }
                    st.success(f"✅ Teacher model loaded: {len(teacher_mesh.vertices)} vertices, {len(teacher_mesh.faces)} faces")
        
        # Student models upload
        st.subheader("Student Submissions")
        student_files = st.file_uploader("Upload student CAD models",
                                        type=['obj', 'stl', 'ply', 'off','STEP'],
                                        accept_multiple_files=True,
                                        key="students")
        
        if student_files:
            progress = st.progress(0)
            for i, student_file in enumerate(student_files):
                with st.spinner(f"Loading {student_file.name}..."):
                    student_mesh = evaluator.load_mesh(student_file, student_file.name)
                    if student_mesh:
                        st.session_state.student_models[student_file.name] = {
                            'mesh': student_mesh,
                            'name': student_file.name,
                            'data': student_file,
                            'metadata': plagiarism_detector.extract_file_metadata(
                                student_file, student_file.name)
                        }
                progress.progress((i + 1) / len(student_files))
            
            st.success(f"✅ Loaded {len(st.session_state.student_models)} student models")
    
    elif mode == "📊 Evaluate Students":
        st.header("Evaluate Student Models")
        
        if not st.session_state.teacher_model:
            st.warning("⚠️ Please upload a teacher reference model first")
        elif not st.session_state.student_models:
            st.warning("⚠️ Please upload student models first")
        else:
            num_points = st.slider("Number of sample points", 1000, 5000, 2048)
            
            if st.button("🚀 Start Evaluation", type="primary"):
                progress = st.progress(0)
                
                # Extract teacher point cloud
                teacher_points = evaluator.extract_point_cloud(
                    st.session_state.teacher_model['mesh'], num_points)
                
                results_container = st.container()
                
                for i, (student_name, student_data) in enumerate(st.session_state.student_models.items()):
                    with st.spinner(f"Evaluating {student_name}..."):
                        # Extract student point cloud
                        student_points = evaluator.extract_point_cloud(
                            student_data['mesh'], num_points)
                        
                        # Compute differences
                        geometric_results = evaluator.compute_geometric_differences(
                            teacher_points, student_points)
                        
                        # Calculate grade
                        grading_results = evaluator.calculate_grade(geometric_results)
                        
                        # Create visualization
                        heatmap = evaluator.create_evaluation_heatmap(
                            student_points,
                            geometric_results['teacher_to_student_distances'],
                            f"{student_name} - Grade: {grading_results['letter_grade']}"
                        )
                        
                        # Store results
                        st.session_state.evaluation_results[student_name] = {
                            'grade': grading_results,
                            'geometric_analysis': geometric_results,
                            'visualization': heatmap,
                            'teacher_points': teacher_points,
                            'student_points': student_points
                        }
                        
                        # Display results
                        with results_container.expander(f"📊 {student_name} - Grade: {grading_results['letter_grade']} ({grading_results['numerical_score']}%)"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Grade", grading_results['letter_grade'])
                                st.metric("Score", f"{grading_results['numerical_score']}%")
                                st.metric("Mean Deviation", f"{geometric_results['mean_deviation']:.4f}")
                            
                            with col2:
                                st.metric("Max Deviation", f"{geometric_results['max_deviation']:.4f}")
                                st.metric("Std Deviation", f"{geometric_results['std_deviation']:.4f}")
                                st.metric("95th Percentile", f"{geometric_results['percentile_95']:.4f}")
                            
                            st.plotly_chart(heatmap, use_container_width=True)
                    
                    progress.progress((i + 1) / len(st.session_state.student_models))
                
                st.success("✅ All evaluations complete!")
    
    elif mode == "🔍 Plagiarism Check":
        st.header("Plagiarism Detection")
        
        if not st.session_state.student_models:
            st.warning("⚠️ Please upload student models first")
        else:
            if st.button("🔍 Run Plagiarism Check", type="primary"):
                with st.spinner("Analyzing for plagiarism patterns..."):
                    # Extract metadata
                    submissions = [data['metadata'] 
                                 for data in st.session_state.student_models.values()]
                    
                    # Analyze patterns
                    suspicious_pairs = plagiarism_detector.analyze_timestamp_patterns(submissions)
                    
                    st.session_state.plagiarism_results = suspicious_pairs
                    
                    if suspicious_pairs:
                        st.warning(f"⚠️ Found {len(suspicious_pairs)} suspicious pairs")
                        
                        for pair in suspicious_pairs:
                            with st.expander(f"{pair['severity']} - {pair['student1']} vs {pair['student2']}"):
                                st.metric("Suspicion Score", f"{pair['suspicion_score']}%")
                                st.write("**Evidence:**")
                                for reason in pair['reasons']:
                                    st.write(f"• {reason}")
                    else:
                        st.success("✅ No plagiarism patterns detected")
    
    elif mode == "📋 Generate Reports":
        st.header("Generate Student Reports")
        
        if not st.session_state.evaluation_results:
            st.warning("⚠️ Please run evaluations first")
        else:
            # Generate individual reports
            if st.button("📄 Generate All Reports", type="primary"):
                reports_zip = BytesIO()
                
                with zipfile.ZipFile(reports_zip, 'w') as zf:
                    progress = st.progress(0)
                    
                    for i, (student_name, eval_results) in enumerate(st.session_state.evaluation_results.items()):
                        # Find plagiarism info for this student
                        plagiarism_info = {'suspicious_matches': []}
                        
                        if st.session_state.plagiarism_results:
                            for pair in st.session_state.plagiarism_results:
                                if pair['student1'] == student_name:
                                    plagiarism_info['suspicious_matches'].append({
                                        'similar_to': pair['student2'],
                                        'score': pair['suspicion_score'],
                                        'severity': pair['severity'],
                                        'reasons': pair['reasons']
                                    })
                                elif pair['student2'] == student_name:
                                    plagiarism_info['suspicious_matches'].append({
                                        'similar_to': pair['student1'],
                                        'score': pair['suspicion_score'],
                                        'severity': pair['severity'],
                                        'reasons': pair['reasons']
                                    })
                        
                        # Generate report
                        report = generate_student_report(
                            student_name,
                            st.session_state.teacher_model,
                            st.session_state.student_models[student_name],
                            eval_results,
                            plagiarism_info
                        )
                        
                        # Add to zip
                        report_name = f"{Path(student_name).stem}_report.md"
                        zf.writestr(report_name, report)
                        
                        progress.progress((i + 1) / len(st.session_state.evaluation_results))
                    
                    # Add summary report
                    summary = generate_class_summary()
                    zf.writestr("class_summary.md", summary)
                
                # Download button
                st.download_button(
                    label="📥 Download All Reports (ZIP)",
                    data=reports_zip.getvalue(),
                    file_name=f"cad_assessment_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
                
                st.success("✅ Reports generated successfully!")
            
            # Display summary statistics
            st.subheader("Class Statistics")
            
            grades = [r['grade']['letter_grade'] 
                     for r in st.session_state.evaluation_results.values()]
            scores = [r['grade']['numerical_score'] 
                     for r in st.session_state.evaluation_results.values()]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Score", f"{np.mean(scores):.1f}%")
                st.metric("Median Score", f"{np.median(scores):.1f}%")
            
            with col2:
                st.metric("Highest Score", f"{max(scores):.1f}%")
                st.metric("Lowest Score", f"{min(scores):.1f}%")
            
            with col3:
                grade_counts = pd.Series(grades).value_counts()
                fig = px.pie(values=grade_counts.values, names=grade_counts.index,
                           title="Grade Distribution")
                st.plotly_chart(fig, use_container_width=True)


def generate_class_summary() -> str:
    """Generate class summary report"""
    
    if not st.session_state.evaluation_results:
        return "No evaluation results available"
    
    grades = [r['grade']['letter_grade'] for r in st.session_state.evaluation_results.values()]
    scores = [r['grade']['numerical_score'] for r in st.session_state.evaluation_results.values()]
    
    summary = f"""
# CLASS ASSESSMENT SUMMARY
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 Overall Statistics

- **Total Students:** {len(scores)}
- **Average Score:** {np.mean(scores):.1f}%
- **Median Score:** {np.median(scores):.1f}%
- **Highest Score:** {max(scores):.1f}%
- **Lowest Score:** {min(scores):.1f}%
- **Standard Deviation:** {np.std(scores):.1f}%

## Grade Distribution

"""
    
    grade_counts = pd.Series(grades).value_counts().sort_index()
    for grade, count in grade_counts.items():
        percentage = (count / len(grades)) * 100
        summary += f"- **{grade} Grade:** {count} students ({percentage:.1f}%)\n"
    
    summary += f"""

## 🔍 Plagiarism Analysis

"""
    
    if st.session_state.plagiarism_results:
        summary += f"- **Suspicious Pairs Found:** {len(st.session_state.plagiarism_results)}\n"
        summary += "- **Pairs Requiring Investigation:**\n"
        for pair in st.session_state.plagiarism_results[:5]:  # Top 5
            summary += f"  - {pair['student1']} vs {pair['student2']} ({pair['suspicion_score']}%)\n"
    else:
        summary += "- **No plagiarism patterns detected**\n"
    
    summary += """

---

*Report generated by CAD Educational Assessment System*
"""
    
    return summary


if __name__ == "__main__":
    main()
