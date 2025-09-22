import os
import json
import logging
import pandas as pd
from flask import Flask, request, jsonify
from calculate_coefficients import compute_coefficients_array
from stats import calc_chi_pvalue
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import uuid
import numpy as np
from flask import Flask, request, jsonify
from calculate_coefficients import compute_coefficients_array
from stats import calc_chi_pvalue

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Storage for processed data (you might want to use a database)
processed_datasets = {}
processed_stats = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def process_qc_dataset(df, user_id):
    """
    Process QC dataset and return structured data
    """
    try:
        if df.empty:
            return {}
        
        data = {}
        df.index.name = 'sample_id'
        
        for sample_id, row in df.iterrows():
            data[str(sample_id)] = row.to_dict()
        
        return data
    except Exception as e:
        logging.error(f"Error processing QC dataset: {str(e)}")
        return {}

def process_stats_file(df, user_id):
    """
    Process statistical data file
    """
    try:
        processed_stats = {}
        
        for index, row in df.iterrows():
            snp_id = row.get('SNP_ID', f'snp_{index}')
            
            # Extract case and control counts
            case_counts = {
                '0': row.get('case_0', 0),
                '1': row.get('case_1', 0), 
                '2': row.get('case_2', 0)
            }
            
            control_counts = {
                '0': row.get('control_0', 0),
                '1': row.get('control_1', 0),
                '2': row.get('control_2', 0)
            }
            
            processed_stats[snp_id] = {
                'case': case_counts,
                'control': control_counts
            }
        
        return processed_stats
    except Exception as e:
        logging.error(f"Error processing stats file: {str(e)}")
        return {}

@app.route('/upload/qc-dataset', methods=['POST'])
def upload_qc_dataset():
    try:
        user_id = request.form.get('user_id')
        phenotype = request.form.get('field1')  # Map to your form field names
        number_of_samples = request.form.get('field2')
        
        dataset_id = str(uuid.uuid4())
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                df = pd.read_csv(file, index_col=0)
                processed_data = process_qc_dataset(df, user_id)
                
                # Store processed dataset
                processed_datasets[dataset_id] = {
                    'user_id': user_id,
                    'data': processed_data,
                    'phenotype': phenotype,
                    'number_of_samples': number_of_samples
                }
                
                return jsonify({
                    "dataset_id": dataset_id,
                    "processed_data": processed_data,
                    "message": "QC dataset processed successfully"
                }), 200
        
        # Just metadata upload
        return jsonify({
            "dataset_id": dataset_id,
            "message": "Metadata uploaded successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"QC dataset upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload/stats', methods=['POST'])
def upload_stats():
    try:
        user_id = request.form.get('user_id')
        collaboration_uuid = request.form.get('uuid')
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if not file or not file.filename.endswith('.csv'):
            return jsonify({"error": "Invalid file format"}), 400
        
        df = pd.read_csv(file)
        processed_stats = process_stats_file(df, user_id)
        
        return jsonify({
            "user_stats": processed_stats,
            "collaboration_uuid": collaboration_uuid,
            "user_id": user_id,
            "message": "Stats processed successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"Stats upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/process/qc', methods=['POST'])
def process_qc_analysis():
    """
    Process QC analysis on combined datasets
    """
    try:
        data = request.get_json()
        datasets_data = data.get('datasets', [])
        threshold = data.get('threshold', 0.08)
        
        if not datasets_data:
            return jsonify({"error": "No datasets provided"}), 400
        
        # Combine datasets into DataFrame
        combined_df = combine_datasets_to_dataframe(datasets_data)
        
        if combined_df.empty:
            return jsonify({"error": "No valid data to process"}), 400
        
        # Compute QC coefficients
        results = compute_coefficients_array(combined_df)
        
        return jsonify({
            "qc_results": results,
            "threshold": threshold,
            "total_pairs": len(results)
        }), 200
        
    except Exception as e:
        logging.error(f"QC processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/process/chi-square', methods=['POST'])
def process_chi_square_analysis():
    """
    Process chi-square statistical analysis
    """
    try:
        data = request.get_json()
        stats_data = data.get('stats_data', {})
        
        if not stats_data:
            return jsonify({"error": "No statistical data provided"}), 400
        
        chi_square_results = {}
        aggregated_snp_data = {}
        
        for user_id, user_stats in stats_data.items():
            user_snp_stats = {}
            
            for snp_id, snp_data in user_stats.items():
                case_counts = [snp_data.get('case', {}).get(str(i), 0) for i in range(3)]
                control_counts = [snp_data.get('control', {}).get(str(i), 0) for i in range(3)]
                
                # Apply smoothing for zero counts
                case_counts = [0.5 if count == 0 else count for count in case_counts]
                control_counts = [0.5 if count == 0 else count for count in control_counts]
                
                user_snp_stats[snp_id] = [case_counts, control_counts]
                
                # Aggregate data
                if snp_id not in aggregated_snp_data:
                    aggregated_snp_data[snp_id] = {}
                if user_id not in aggregated_snp_data[snp_id]:
                    aggregated_snp_data[snp_id][user_id] = np.zeros((2, 3))
                
                aggregated_snp_data[snp_id][user_id][0] += np.array(case_counts)
                aggregated_snp_data[snp_id][user_id][1] += np.array(control_counts)
            
            # Calculate chi-square for this user
            chi_square_results[user_id] = calc_chi_pvalue(user_snp_stats)
        
        # Calculate aggregated results
        aggregated_results = {}
        for snp_id, user_tables in aggregated_snp_data.items():
            total_table = np.zeros((2, 3))
            for user_table in user_tables.values():
                total_table += user_table
            
            aggregated_snp_stats = {snp_id: [total_table[0].tolist(), total_table[1].tolist()]}
            aggregated_results.update(calc_chi_pvalue(aggregated_snp_stats))
        
        return jsonify({
            "individual_results": chi_square_results,
            "aggregated_results": aggregated_results
        }), 200
        
    except Exception as e:
        logging.error(f"Chi-square processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def combine_datasets_to_dataframe(datasets_data):
    """
    Combine multiple datasets into a single DataFrame
    """
    if not datasets_data:
        return pd.DataFrame()
    
    dfs = []
    all_columns = set()
    
    for dataset in datasets_data:
        if 'data' in dataset:
            user_id = dataset.get('user_id')
            sample_data = dataset['data']
            samples = []
            
            for sample_id, sample in sample_data.items():
                sample['sample_id'] = sample_id
                sample['user_id'] = user_id
                samples.append(sample)
                all_columns.update(sample.keys())
            
            df = pd.DataFrame(samples)
            df = df.reindex(columns=sorted(all_columns))
            df.set_index(['sample_id', 'user_id'], inplace=True)
            
            dfs.append(df)
    
    if dfs:
        combined_df = pd.concat(dfs)
        combined_df = combined_df[sorted(combined_df.columns)]
        return combined_df
    
    return pd.DataFrame()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)