#!/usr/bin/env python
"""
Test script for CAD Educational Assessment System
Verifies installation and creates sample test data
"""

import os
import sys
import numpy as np
import trimesh
from pathlib import Path
import json
from datetime import datetime

def create_sample_models():
    """Create sample CAD models for testing"""
    print("\n📦 Creating sample CAD models for testing...")
    
    # Create directories
    Path("sample_models/teacher").mkdir(parents=True, exist_ok=True)
    Path("sample_models/students").mkdir(parents=True, exist_ok=True)
    
    # Create a simple box as teacher reference
    teacher_box = trimesh.creation.box(extents=[2, 2, 2])
    teacher_path = "sample_models/teacher/reference_box.obj"
    teacher_box.export(teacher_path)
    print(f"  ✅ Created teacher reference: {teacher_path}")
    
    # Create student models with varying accuracy
    
    # Student 1: Perfect match (Grade A expected)
    student1_box = trimesh.creation.box(extents=[2, 2, 2])
    student1_path = "sample_models/students/student1_perfect.obj"
    student1_box.export(student1_path)
    print(f"  ✅ Created Student 1 (perfect): {student1_path}")
    
    # Student 2: Slightly off (Grade B expected)
    student2_box = trimesh.creation.box(extents=[2.1, 2.1, 2.1])
    student2_path = "sample_models/students/student2_good.obj"
    student2_box.export(student2_path)
    print(f"  ✅ Created Student 2 (good): {student2_path}")
    
    # Student 3: More deviation (Grade C expected)
    student3_box = trimesh.creation.box(extents=[2.3, 2.3, 2.3])
    student3_path = "sample_models/students/student3_acceptable.obj"
    student3_box.export(student3_path)
    print(f"  ✅ Created Student 3 (acceptable): {student3_path}")
    
    # Student 4: Significant deviation (Grade D/F expected)
    student4_box = trimesh.creation.box(extents=[3, 3, 3])
    student4_path = "sample_models/students/student4_poor.obj"
    student4_box.export(student4_path)
    print(f"  ✅ Created Student 4 (poor): {student4_path}")
    
    # Student 5: Copy of Student 1 (for plagiarism detection)
    student5_box = trimesh.creation.box(extents=[2, 2, 2])
    student5_path = "sample_models/students/student5_copy.obj"
    student5_box.export(student5_path)
    print(f"  ✅ Created Student 5 (copy): {student5_path}")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing module imports...")
    
    modules_to_test = [
        ('streamlit', 'Streamlit (UI framework)'),
        ('numpy', 'NumPy (numerical computing)'),
        ('pandas', 'Pandas (data analysis)'),
        ('trimesh', 'Trimesh (3D mesh processing)'),
        ('plotly', 'Plotly (visualization)'),
        ('sklearn', 'Scikit-learn (machine learning)'),
    ]
    
    all_success = True
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {description}: OK")
        except ImportError as e:
            print(f"  ❌ {description}: FAILED - {e}")
            all_success = False
    
    # Test optional modules
    print("\n  Optional modules:")
    optional_modules = [
        ('pymeshlab', 'PyMeshLab (advanced mesh repair)'),
        ('cascadio', 'Cascadio (STEP file conversion)'),
    ]
    
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            print(f"    ✅ {description}: Available")
        except ImportError:
            print(f"    ⚠️  {description}: Not installed (optional)")
    
    return all_success

def test_evaluation_system():
    """Test the CAD evaluation system"""
    print("\n🧪 Testing CAD Evaluation System...")
    
    try:
        # Import the evaluation system from app.py
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import CADEvaluationSystem, MetadataPlagiarismDetector
        
        # Initialize evaluator
        evaluator = CADEvaluationSystem()
        print("  ✅ CAD Evaluation System initialized")
        
        # Test with sample models
        teacher_mesh = trimesh.creation.box(extents=[2, 2, 2])
        student_mesh = trimesh.creation.box(extents=[2.1, 2.1, 2.1])
        
        # Extract point clouds
        teacher_points = evaluator.extract_point_cloud(teacher_mesh, 1000)
        student_points = evaluator.extract_point_cloud(student_mesh, 1000)
        print("  ✅ Point cloud extraction working")
        
        # Compute differences
        geometric_results = evaluator.compute_geometric_differences(
            teacher_points, student_points)
        print(f"  ✅ Geometric analysis working (mean deviation: {geometric_results['mean_deviation']:.4f})")
        
        # Calculate grade
        grading_results = evaluator.calculate_grade(geometric_results)
        print(f"  ✅ Grading system working (Grade: {grading_results['letter_grade']}, Score: {grading_results['numerical_score']}%)")
        
        # Test plagiarism detector
        detector = MetadataPlagiarismDetector()
        print("  ✅ Plagiarism Detector initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing evaluation system: {e}")
        return False

def test_visualization():
    """Test visualization capabilities"""
    print("\n📊 Testing visualization...")
    
    try:
        import plotly.graph_objects as go
        
        # Create a simple 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=[1, 2, 3],
            y=[1, 2, 3],
            z=[1, 2, 3],
            mode='markers',
            marker=dict(size=10, color='blue')
        )])
        
        fig.update_layout(title="Test 3D Visualization")
        
        # Save to HTML
        test_file = "test_visualization.html"
        fig.write_html(test_file)
        
        if os.path.exists(test_file):
            print(f"  ✅ Visualization working (saved to {test_file})")
            os.remove(test_file)  # Clean up
            return True
        else:
            print("  ❌ Visualization failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Visualization error: {e}")
        return False

def test_file_operations():
    """Test file read/write operations"""
    print("\n💾 Testing file operations...")
    
    try:
        # Test report directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Create test report
        test_report = reports_dir / "test_report.md"
        test_content = f"""
# Test Report
Generated at: {datetime.now().isoformat()}
Status: Testing file operations
        """
        
        with open(test_report, 'w') as f:
            f.write(test_content)
        
        # Read back
        with open(test_report, 'r') as f:
            content = f.read()
        
        if "Test Report" in content:
            print(f"  ✅ File operations working")
            os.remove(test_report)  # Clean up
            return True
        else:
            print("  ❌ File operations failed")
            return False
            
    except Exception as e:
        print(f"  ❌ File operations error: {e}")
        return False

def generate_test_report(results):
    """Generate a test results report"""
    print("\n" + "="*50)
    print("📋 TEST RESULTS SUMMARY")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\n📌 Next steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Open: http://localhost:8501")
        print("  3. Upload the sample models from sample_models/")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        print("You may need to install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    print("\n" + "="*50)

def main():
    """Main test function"""
    print("\n" + "="*50)
    print("🧪 CAD Educational Assessment System - Test Suite")
    print("="*50)
    
    results = {}
    
    # Run tests
    results['Module Imports'] = test_imports()
    results['Sample Model Creation'] = create_sample_models()
    results['Evaluation System'] = test_evaluation_system()
    results['Visualization'] = test_visualization()
    results['File Operations'] = test_file_operations()
    
    # Generate report
    generate_test_report(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
