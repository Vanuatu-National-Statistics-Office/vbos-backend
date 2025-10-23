import pandas as pd
import os
import sys
from pathlib import Path

def split_csv_hierarchically(input_file, output_dir='output'):
    """
    Split a CSV file by Cluster, then Type, then Indicator.
    Each split removes the splitting column and adds it to the filename.
    
    Args:
        input_file: Path to the input CSV file
        output_dir: Directory where output files will be saved
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Read the CSV file with low_memory=False to avoid dtype warnings
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file, low_memory=False)
    
    # Strip whitespace from all column headers
    df.columns = df.columns.str.strip()
    print("Stripped whitespace from column headers")
    
    # Convert Year column to integer if it exists, handling missing values
    if 'Year' in df.columns:
        # Convert to nullable integer type (Int64 instead of int64)
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Year'] = df['Year'].astype('Int64')
        print("Converted 'Year' column to integers (preserving empty values)")
    
    # Clean and convert Value column if it exists
    if 'Value' in df.columns:
        # Remove commas and other non-numeric characters, then convert to number
        df['Value'] = df['Value'].astype(str).str.replace(',', '', regex=False)
        df['Value'] = df['Value'].str.replace(' ', '', regex=False)
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        print("Cleaned and converted 'Value' column to numbers")
    
    # Verify required columns exist
    required_columns = ['Cluster', 'Type', 'Indicator']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in CSV. Available columns: {df.columns.tolist()}")
    
    # Get unique values for each splitting column
    clusters = df['Cluster'].unique()
    
    print(f"Found {len(clusters)} unique clusters")
    
    # Split by Cluster
    for cluster in clusters:
        cluster_df = df[df['Cluster'] == cluster].copy()
        
        # Get unique Types for this cluster
        types = cluster_df['Type'].unique()
        
        # Split by Type
        for type in types:
            type_df = cluster_df[cluster_df['Type'] == type].copy()
            
            # Get unique Indicators for this Type
            indicators = type_df['Indicator'].unique()
            
            # Split by Indicator
            for indicator in indicators:
                indicator_df = type_df[type_df['Indicator'] == indicator].copy()
                
                # Remove the splitting columns
                indicator_df = indicator_df.drop(columns=['Cluster', 'Type', 'Indicator'])
                
                # Create filename with all three values
                # Clean the values to make them filesystem-safe
                clean_cluster = str(cluster).replace('/', '_').replace('\\', '_').replace(' ', '_')
                clean_type = str(type).replace('/', '_').replace('\\', '_').replace(' ', '_')
                clean_indicator = str(indicator).replace('/', '_').replace('\\', '_').replace(' ', '_')
                
                filename = f"{clean_cluster}_{clean_type}_{clean_indicator}.csv"
                output_path = os.path.join(output_dir, filename)
                
                # Save the split CSV
                indicator_df.to_csv(output_path, index=False)
                print(f"Created: {filename} ({len(indicator_df)} rows)")
    
    print(f"\nAll files saved to '{output_dir}' directory")

# Main execution
if __name__ == "__main__":
    # Check if file path was provided
    if len(sys.argv) < 2:
        print("Usage: python split_csv.py <input_file.csv> [output_directory]")
        print("\nExamples:")
        print("  python split_csv.py mydata.csv")
        print("  python split_csv.py mydata.csv split_output")
        print("  python split_csv.py /path/to/mydata.csv /path/to/output")
        sys.exit(1)
    
    # Get input file from command line argument
    input_csv = sys.argv[1]
    
    # Get output directory (optional, defaults to 'output')
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    
    try:
        split_csv_hierarchically(input_csv, output_dir=output_dir)
    except FileNotFoundError:
        print(f"Error: File '{input_csv}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
