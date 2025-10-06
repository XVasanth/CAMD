# 🎓 CAD Educational Assessment System

A comprehensive Streamlit application for evaluating student CAD models against teacher references, detecting plagiarism, and generating detailed assessment reports.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

### 📊 Geometric Accuracy Evaluation
- Compare student CAD models against teacher reference models
- Point cloud-based geometric analysis
- Automatic grading with configurable thresholds
- Interactive 3D visualization of deviations
- Support for multiple CAD formats (OBJ, STL, PLY, OFF)

### 🔍 Plagiarism Detection
- Metadata-based similarity analysis
- File hash comparison for exact copy detection
- Timestamp pattern analysis
- Severity-based flagging system
- Batch processing of multiple submissions

### 📋 Comprehensive Reporting
- Individual student assessment reports
- Class-wide summary statistics
- Grade distribution analysis
- Downloadable report package (ZIP)
- Markdown format for easy sharing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/cad-assessment-system.git
cd cad-assessment-system
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload Models
- Navigate to "Upload Models" in the sidebar
- Upload the teacher's reference CAD model
- Upload multiple student submissions
- Supported formats: OBJ, STL, PLY, OFF

### 2. Evaluate Students
- Go to "Evaluate Students"
- Configure the number of sample points (default: 2048)
- Click "Start Evaluation"
- View individual results with 3D heatmaps
- Grades are assigned based on geometric deviation

### 3. Check for Plagiarism
- Select "Plagiarism Check"
- Click "Run Plagiarism Check"
- Review suspicious pairs with severity ratings
- Investigate flagged submissions

### 4. Generate Reports
- Navigate to "Generate Reports"
- Click "Generate All Reports"
- Download the ZIP file containing:
  - Individual student reports
  - Class summary report
  - All reports in Markdown format

## 🎯 Grading Scale

| Grade | Score Range | Mean Deviation | Description |
|-------|------------|----------------|-------------|
| A | 95-100% | ≤0.1 units | Excellent accuracy |
| B | 85-94% | ≤0.5 units | Good work with minor deviations |
| C | 75-84% | ≤1.0 units | Acceptable but needs improvement |
| D | 65-74% | ≤2.0 units | Major revision needed |
| F | <65% | >2.0 units | Unsatisfactory |

## 🔧 Configuration

### Customizing Grading Thresholds

Edit the `grading_thresholds` in `app.py`:

```python
self.grading_thresholds = {
    'A': 0.1,   # Adjust these values
    'B': 0.5,   # based on your
    'C': 1.0,   # requirements
    'D': 2.0,
    'F': float('inf')
}
```

### Adjusting Plagiarism Sensitivity

Modify the `suspicion_threshold` in the `MetadataPlagiarismDetector` class:

```python
self.suspicion_threshold = 70  # Lower = more sensitive
```

## 📂 Project Structure

```
cad-assessment-system/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── LICENSE               # License file
│
├── sample_models/        # Sample CAD files (optional)
│   ├── teacher/
│   └── students/
│
└── reports/             # Generated reports directory
```

## 🛠️ Advanced Features

### STEP File Support

To enable STEP file conversion, install the optional dependency:

```bash
pip install cascadio
```

### Mesh Repair

For advanced mesh repair capabilities:

```bash
pip install pymeshlab
```

## 🐛 Troubleshooting

### Common Issues

1. **ImportError for trimesh:**
   ```bash
   pip install trimesh[easy]
   ```

2. **Memory issues with large models:**
   - Reduce the number of sample points
   - Process files in smaller batches

3. **Visualization not showing:**
   - Ensure plotly is installed: `pip install plotly`
   - Check browser console for errors

## 📊 Integration with Microsoft 365

This system can be integrated with Microsoft 365 Education:

1. **SharePoint**: Store CAD files and reports
2. **Power Automate**: Automate submission collection
3. **Teams**: Share results with students
4. **Power BI**: Create advanced analytics dashboards

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- 3D processing powered by [trimesh](https://trimsh.org/)
- Visualization using [Plotly](https://plotly.com/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note:** Ensure all student data is handled in compliance with your institution's privacy policies and educational regulations.
