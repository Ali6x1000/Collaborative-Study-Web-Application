# Collaborator Server - PCA Handler with Docker GUI

This folder contains the **fully consolidated** PCA (Principal Component Analysis) handler for the Collaborator Server, now with a **web-based GUI** and **Docker containerization**.

## Files

- `pca_handler.py` - **Complete PCA handler** with all functionality in class methods
- `test_pca_handler.py` - Test script to verify functionality
- `README.md` - This documentation

## Features

✅ **Fully Consolidated**: All PCA functionality in class methods only  
✅ **No Redundancy**: No standalone functions, everything in class  
✅ **Model Training**: Train PCA models and save as pickle files  
✅ **Model Loading**: Load models with intelligent caching  
✅ **Data Transformation**: Transform new data using trained models  
✅ **Model Management**: List models, get info, clear cache  
✅ **Flexible Input**: Accept data files or DataFrames  
✅ **Error Handling**: Comprehensive error handling and logging  
✅ **Self-Contained**: No external dependencies  
✅ **Web-Based GUI**: Intuitive interface for PCA operations  
✅ **Dockerized**: Easy deployment and scaling  

## 🚀 Quick Start with Docker

### Method 1: Docker Compose (Recommended)

```bash
# Navigate to the directory
cd /Users/alinawaf/Desktop/Erman/Collaborative-Study-Web-Application/web_application/Backend/FlaskApp/Collaborator_Server

# Build and start the container
docker-compose up --build

# Access the GUI at http://localhost:5000
```

### Method 2: Docker Build & Run

```bash
# Build the Docker image
docker build -t pca-handler-gui .

# Run the container
docker run -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  pca-handler-gui

# Access the GUI at http://localhost:5000
```

## 📁 Files Structure

```
Collaborator_Server/
├── 🐳 Dockerfile                  # Container configuration
├── 🐳 docker-compose.yml          # Multi-service setup  
├── 📋 requirements.txt            # Python dependencies
├── 🌐 gui_app.py                  # Flask web GUI application
├── 🔧 pca_handler.py             # Core PCA functionality
├── 🧪 test_pca_handler.py        # Test script
├── 📊 transformed_data*.csv       # Sample datasets
├── 📖 README.md                   # This documentation
└── templates/                     # HTML templates
    ├── base.html                  # Base template
    ├── index.html                 # Dashboard
    ├── train.html                 # Model training
    ├── transform.html             # Data transformation
    ├── models.html               # Models listing
    └── outputs.html              # Results download
```

## 🌐 Web GUI Features

### 🏠 Dashboard (`/`)
- **Overview**: System status and quick stats
- **Navigation**: Access to all features
- **Quick Actions**: Train, transform, view models

### 🔧 Train Models (`/train`)
- **Upload CSV**: Drag & drop data files
- **Configure**: Set model name and components
- **Progress**: Real-time training feedback
- **Results**: Model info and statistics

### 🔄 Transform Data (`/transform`)
- **Model Selection**: Choose from trained models
- **Data Upload**: Upload files to transform
- **Privacy Options**: Add differential privacy noise
- **Download**: Get transformed results instantly

### 📊 Manage Models (`/models`)
- **List Models**: View all trained models
- **Model Details**: Components, variance explained
- **Performance**: Training statistics and info

### 📥 Download Results (`/outputs`)
- **File Browser**: All transformed datasets
- **One-Click Download**: Get CSV files instantly
- **File Info**: Size and metadata

## Quick Start

### 1. Import the Handler

```python
from pca_handler import (
    train_pca_model_handler,
    load_pca_model_handler,
    transform_data_handler,
    get_model_info_handler,
    list_models_handler
)
```

### 2. Train a PCA Model

```python
# Train PCA model using data_party_a.csv
result = train_pca_model_handler(
    data_file="../../../datasets/eye_color/data_party_a.csv",
    model_name="party_a_pca_model",
    n_components=0.95  # Keep 95% of variance
)

if result['success']:
    print(f"Model trained: {result['model_name']}")
    print(f"Components: {result['results']['n_components']}")
    print(f"Variance: {result['results']['total_variance_explained']:.4f}")
```

### 3. Transform Data

```python
# Transform data using the trained model
transform_result = transform_data_handler(
    model_name="party_a_pca_model",
    data_file="../../../datasets/eye_color/data_party_a.csv"  # or use data_df=your_dataframe
)

if transform_result['success']:
    print(f"Original shape: {transform_result['original_shape']}")
    print(f"Transformed shape: {transform_result['transformed_shape']}")
    transformed_data = transform_result['transformed_data']
```

## Functions

### `train_pca_model_handler(data_file, model_name, n_components=0.95)`

Trains a PCA model and saves it.

**Parameters:**

- `data_file`: Path to training data file
- `model_name`: Name for the model (without .pkl extension)
- `n_components`: Number of components (0.95 = 95% variance)

**Returns:** Dictionary with success status and results

### `load_pca_model_handler(model_name)`

Loads a PCA model (with caching).

**Parameters:**

- `model_name`: Name of the model to load

**Returns:** Dictionary with model data or error

### `transform_data_handler(model_name, data_file=None, data_df=None)`

Transforms data using a PCA model.

**Parameters:**

- `model_name`: Name of the model to use
- `data_file`: Path to data file (optional)
- `data_df`: DataFrame (optional)

**Returns:** Dictionary with transformation results

### `get_model_info_handler(model_name)`

Gets information about a PCA model.

**Parameters:**

- `model_name`: Name of the model

**Returns:** Dictionary with model information

### `list_models_handler()`

Lists all available PCA models.

**Returns:** Dictionary with list of models

## Example Usage

### Complete Workflow

```python
from pca_handler import *

# 1. Train model using data_party_a.csv
train_result = train_pca_model_handler(
    "../../../datasets/eye_color/data_party_a.csv",
    "party_a_pca_model",
    n_components=0.95
)

# 2. Get model info
info = get_model_info_handler("party_a_pca_model")
print(f"Model has {info['n_components']} components")

# 3. Transform new data
transform_result = transform_data_handler(
    "party_a_pca_model",
    data_file="../../../datasets/eye_color/data_party_a.csv"
)

# 4. Use transformed data
transformed_data = transform_result['transformed_data']
# transformed_data is now a numpy array with reduced dimensions
```

### Using with DataFrames

```python
import pandas as pd
from pca_handler import transform_data_handler

# Load your data
data = pd.read_csv("../../../datasets/eye_color/data_party_a.csv")

# Transform using DataFrame
result = transform_data_handler(
    model_name="party_a_pca_model",
    data_df=data
)

if result['success']:
    transformed = result['transformed_data']
    print(f"Transformed shape: {transformed.shape}")
```

## Model Caching

The handler automatically caches loaded models for better performance:

- First load: Loads from file
- Subsequent loads: Uses cached version
- Cache persists until manually cleared

## Testing

Run the test script to verify everything works:

```bash
cd Collaborator_Server
python test_pca_handler.py
```

This will:

1. Train a PCA model on your data
2. Test loading and caching
3. Test data transformation
4. Test with both files and DataFrames

## Integration with Your App

You can now use these functions in your main application:

```python
# In your main app
from Collaborator_Server.pca_handler import transform_data_handler

# Use with data_party_a.csv dataset
result = transform_data_handler(
    model_name="party_a_pca_model",
    data_file="../../../datasets/eye_color/data_party_a.csv"
)
```

## Dataset Information

The PCA handler is configured to work with the `data_party_a.csv` dataset:

- **Location**: `datasets/eye_color/data_party_a.csv`
- **Size**: 471 rows × 3001 columns
- **Type**: Genetic SNP data
- **Format**: CSV with numeric values

This dataset contains genetic variant data suitable for PCA dimensionality reduction and analysis.

## Benefits of Full Consolidation

✅ **Zero Redundancy**: No duplicate functions or code  
✅ **Single Source**: All logic in class methods only  
✅ **Cleaner Code**: No standalone functions to maintain  
✅ **Better Organization**: Everything logically grouped in class  
✅ **Easier Debugging**: All functionality in one place  
✅ **Reduced Complexity**: Simpler architecture  
✅ **Self-Contained**: Can be moved or copied easily  

## 🔒 Privacy Features

### Differential Privacy
- **Laplacian Noise**: Added to transformed data
- **Configurable Epsilon**: Control privacy-utility tradeoff
- **Reproducible**: Set random seed for consistent results

### Usage Example
```python
# Transform with privacy protection
result = transform_data_handler(
    model_name="my_model",
    data_file="data.csv",
    add_noise=True,      # Enable differential privacy
    epsilon=1.0,         # Privacy parameter
    random_seed=42       # For reproducibility
)
```

## 🐳 Docker Benefits

✅ **Isolated Environment**: No dependency conflicts  
✅ **Consistent Deployment**: Same environment everywhere  
✅ **Easy Scaling**: Run multiple instances  
✅ **Volume Persistence**: Data persists across restarts  
✅ **Health Monitoring**: Built-in health checks  
✅ **Production Ready**: Optimized for deployment  

## 📋 Container Management

### Check Container Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Container
```bash
docker-compose down
```

### Restart Container
```bash
docker-compose restart
```

### Update Container
```bash
docker-compose down
docker-compose up --build
```

## 🔧 Environment Variables

Configure the container with environment variables:

```yaml
environment:
  - FLASK_ENV=production        # Flask environment
  - PYTHONUNBUFFERED=1         # Python output buffering
  - MAX_UPLOAD_SIZE=100        # Max file size in MB
```

## 📁 Volume Mounts

The container mounts these directories:

- `./models` → `/app/models` - Trained PCA models
- `./uploads` → `/app/uploads` - Uploaded data files  
- `./outputs` → `/app/outputs` - Transformed results
- `./transformed_data*.csv` → Sample datasets

## 🚀 Production Deployment

### AWS/Cloud Deployment
```bash
# Build for production
docker build -t pca-handler:latest .

# Tag for registry
docker tag pca-handler:latest your-registry/pca-handler:latest

# Push to registry
docker push your-registry/pca-handler:latest
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pca-handler-gui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pca-handler
  template:
    metadata:
      labels:
        app: pca-handler
    spec:
      containers:
      - name: pca-handler
        image: your-registry/pca-handler:latest
        ports:
        - containerPort: 5000
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Or use different port
docker run -p 8080:5000 pca-handler-gui
```

### Permission Issues
```bash
# Fix file permissions
chmod -R 755 models uploads outputs

# Or run with user mapping
docker run --user $(id -u):$(id -g) -p 5000:5000 pca-handler-gui
```

### Memory Issues
```bash
# Increase Docker memory limit
# Or clear model cache via GUI
curl -X POST http://localhost:5000/api/clear_cache
```

## 🎯 Next Steps

1. **Access GUI**: Open http://localhost:5000
2. **Upload Data**: Try the sample datasets
3. **Train Model**: Create your first PCA model  
4. **Transform Data**: Apply PCA to new datasets
5. **Download Results**: Get transformed CSV files

The containerized PCA Handler provides a complete, production-ready solution for PCA analysis with an intuitive web interface!
