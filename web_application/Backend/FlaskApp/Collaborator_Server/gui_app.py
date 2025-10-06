#!/usr/bin/env python3
"""
Flask GUI Application for PCA Handler
Provides a web interface for all PCA operations
"""

import os
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from pca_handler import (
    train_pca_model_handler,
    load_pca_model_handler,
    transform_data_handler,
    get_model_info_handler,
    list_models_handler,
    clear_cache_handler
)
from metadata_generation_relatedness import (
    randomized_response,
    shuffle_data,
    add_noise,
    add_synthetic_samples
)

app = Flask(__name__)
app.secret_key = 'pca_handler_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Add custom Jinja2 filter for basename
@app.template_filter('basename')
def basename_filter(path):
    """Extract filename from path"""
    return os.path.basename(path)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_metadata_generation(input_csv, snp_file, output_filename, seed=1234, eps=5, 
                              num_synthetic_samples=100, num_existing_samples_to_combine=3):
    """Process metadata generation with relatedness"""
    try:
        # Read the SNP list from the file
        with open(snp_file, 'r') as file:
            snp_list = [line.strip() for line in file]
            
        # Load the dataset
        data = pd.read_csv(input_csv, sep=",", index_col=0).T
        data.columns = data.columns.astype(str)
        data = data.loc[snp_list]

        # Shuffle the data
        shuffled_data = shuffle_data(data, seed)

        # Add noise to the data
        noisy_data = add_noise(shuffled_data, eps)

        # Add synthetic samples to the data
        augmented_data = add_synthetic_samples(noisy_data, num_synthetic_samples, num_existing_samples_to_combine)

        # Transpose back the final data if needed
        augmented_data = augmented_data.T

        # Save the generated metadata to the specified output CSV
        augmented_data.to_csv(output_filename, index=True)
        
        return {'success': True, 'message': 'Metadata generation completed successfully'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    """Main page with navigation to all features"""
    models_result = list_models_handler()
    available_models = models_result.get('models', []) if models_result['success'] else []
    
    return render_template('index.html', models=available_models)

@app.route('/train', methods=['GET', 'POST'])
def train_model():
    """Train a new PCA model"""
    if request.method == 'POST':
        try:
            # Get form data
            model_name = request.form['model_name'].strip()
            n_components = request.form.get('n_components', '2')
            
            # Handle file upload
            if 'data_file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['data_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Convert n_components to appropriate type
                try:
                    if '.' in n_components:
                        n_components = float(n_components)
                    else:
                        n_components = int(n_components)
                except ValueError:
                    n_components = 2
                
                # Train the model
                result = train_pca_model_handler(file_path, model_name, n_components)
                
                if result['success']:
                    flash(f'Model "{model_name}" trained successfully!', 'success')
                    return redirect(url_for('model_info', model_name=model_name))
                else:
                    flash(f'Training failed: {result["error"]}', 'error')
            else:
                flash('Invalid file type. Please upload CSV files only.', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('train.html')

@app.route('/transform', methods=['GET', 'POST'])
def transform_data():
    """Transform data using existing PCA model"""
    models_result = list_models_handler()
    available_models = models_result.get('models', []) if models_result['success'] else []
    
    if request.method == 'POST':
        try:
            model_name = request.form['model_name']
            add_noise = 'add_noise' in request.form
            epsilon = float(request.form.get('epsilon', 1.0))
            random_seed = request.form.get('random_seed')
            
            if random_seed:
                random_seed = int(random_seed)
            else:
                random_seed = None
            
            # Handle file upload
            if 'data_file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['data_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Get model info first to check compatibility
                model_info = get_model_info_handler(model_name)
                if model_info['success']:
                    expected_features = len(model_info['feature_names'])
                    
                    # Check uploaded file structure
                    try:
                        test_data = pd.read_csv(file_path)
                        available_features = len(test_data.select_dtypes(include=[np.number]).columns) - 1  # -1 for first column
                        
                        if available_features < expected_features:
                            flash(f'Feature mismatch: Model "{model_name}" expects {expected_features} features, '
                                  f'but uploaded file has only {available_features} numeric features (excluding first column). '
                                  f'Please upload a file with compatible structure or train a new model with this data.', 'error')
                            return redirect(request.url)
                    except Exception as e:
                        flash(f'Error reading uploaded file: {str(e)}', 'error')
                        return redirect(request.url)
                
                # Transform the data
                result = transform_data_handler(
                    model_name, 
                    data_file=file_path, 
                    add_noise=add_noise, 
                    epsilon=epsilon, 
                    random_seed=random_seed
                )
                
                if result['success']:
                    # Save transformed data to outputs folder
                    output_filename = f"transformed_{model_name}_{filename}"
                    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                    
                    # Create DataFrame and save
                    transformed_data = result['transformed_data']
                    df = pd.DataFrame(transformed_data)
                    
                    # Add proper column names
                    if transformed_data.shape[1] > 2:
                        # First column + PC columns
                        columns = ['ID'] + [f'PC_{i+1}' for i in range(transformed_data.shape[1]-1)]
                    else:
                        columns = [f'PC_{i+1}' for i in range(transformed_data.shape[1])]
                    
                    df.columns = columns[:df.shape[1]]  # Ensure we don't have more names than columns
                    df.to_csv(output_path, index=False)
                    
                    flash(f'Data transformed successfully! Output saved as {output_filename}', 'success')
                    
                    return render_template('transform_result.html', 
                                         result=result, 
                                         output_file=output_filename,
                                         model_name=model_name)
                else:
                    # Provide more specific error messages
                    error_msg = result['error']
                    if 'Found array with 0 feature(s)' in error_msg:
                        flash(f'Feature compatibility error: The selected model was trained on different data structure. '
                              f'Please either:\n'
                              f'1. Upload data with the same structure as the training data\n'
                              f'2. Train a new model with your current data format', 'error')
                    elif 'feature(s)' in error_msg.lower():
                        flash(f'Data structure mismatch: {error_msg}. '
                              f'Please check that your data has the same format as used for training.', 'error')
                    else:
                        flash(f'Transformation failed: {error_msg}', 'error')
            else:
                flash('Invalid file type. Please upload CSV files only.', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('transform.html', models=available_models)

@app.route('/metadata', methods=['GET', 'POST'])
def metadata_generation():
    """Metadata generation with relatedness"""
    if request.method == 'POST':
        try:
            # Get form data
            seed = int(request.form.get('seed', 1234))
            eps = float(request.form.get('eps', 5.0))
            num_synthetic_samples = int(request.form.get('num_synthetic_samples', 100))
            num_existing_samples_to_combine = int(request.form.get('num_existing_samples_to_combine', 3))
            output_name = request.form.get('output_name', 'metadata_output.csv')
            
            # Ensure output name has .csv extension
            if not output_name.endswith('.csv'):
                output_name += '.csv'
            
            # Handle input CSV file upload
            if 'input_csv' not in request.files or 'snp_file' not in request.files:
                flash('Both input CSV and SNP list files are required', 'error')
                return redirect(request.url)
            
            input_file = request.files['input_csv']
            snp_file = request.files['snp_file']
            
            if input_file.filename == '' or snp_file.filename == '':
                flash('Both files must be selected', 'error')
                return redirect(request.url)
            
            if input_file and snp_file and allowed_file(input_file.filename) and allowed_file(snp_file.filename):
                # Save uploaded files
                input_filename = secure_filename(input_file.filename)
                snp_filename = secure_filename(snp_file.filename)
                
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
                snp_path = os.path.join(app.config['UPLOAD_FOLDER'], snp_filename)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)
                
                input_file.save(input_path)
                snp_file.save(snp_path)
                
                # Process metadata generation
                result = process_metadata_generation(
                    input_path, snp_path, output_path,
                    seed=seed, eps=eps,
                    num_synthetic_samples=num_synthetic_samples,
                    num_existing_samples_to_combine=num_existing_samples_to_combine
                )
                
                if result['success']:
                    flash(f'Metadata generation completed! Output saved as {output_name}', 'success')
                    return render_template('metadata_result.html', 
                                         output_file=output_name,
                                         parameters={
                                             'seed': seed,
                                             'eps': eps,
                                             'num_synthetic_samples': num_synthetic_samples,
                                             'num_existing_samples_to_combine': num_existing_samples_to_combine
                                         })
                else:
                    flash(f'Metadata generation failed: {result["error"]}', 'error')
            else:
                flash('Invalid file type. Please upload CSV/TXT files only.', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('metadata.html')

@app.route('/models')
def list_models():
    """List all available models"""
    result = list_models_handler()
    
    if result['success']:
        models_info = []
        for model_name in result['models']:
            info = get_model_info_handler(model_name)
            if info['success']:
                models_info.append(info)
        
        return render_template('models.html', models=models_info)
    else:
        flash(f'Error listing models: {result["error"]}', 'error')
        return render_template('models.html', models=[])

@app.route('/model/<model_name>')
def model_info(model_name):
    """Show detailed information about a specific model"""
    result = get_model_info_handler(model_name)
    
    if result['success']:
        return render_template('model_detail.html', model=result)
    else:
        flash(f'Error getting model info: {result["error"]}', 'error')
        return redirect(url_for('list_models'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download output files"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/clear_cache', methods=['POST'])
def api_clear_cache():
    """API endpoint to clear model cache"""
    result = clear_cache_handler()
    return jsonify(result)

@app.route('/outputs')
def list_outputs():
    """List all output files"""
    try:
        output_files = []
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if filename.endswith('.csv'):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                file_size = os.path.getsize(file_path)
                output_files.append({
                    'filename': filename,
                    'size': file_size,
                    'size_mb': round(file_size / 1024 / 1024, 2)
                })
        
        return render_template('outputs.html', files=output_files)
    except Exception as e:
        flash(f'Error listing output files: {str(e)}', 'error')
        return render_template('outputs.html', files=[])

if __name__ == '__main__':
    print("🚀 Starting PCA Handler GUI Application...")
    print("📊 Available at: http://localhost:5000")
    print("🔧 Features: Train Models, Transform Data, Generate Metadata, View Results")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
