import matplotlib.pyplot as plt
import pandas as pd


def plot_top_symptoms(symptom_data, top_n=30):
    """
    Generate a publication-quality horizontal bar chart showing EXACTLY 30 clinical symptoms.
    
    Automatically filters out disorder-level concepts (Depression, Anxiety, Stress, PTSD, etc.)
    and displays only symptom-level concepts.
    
    Parameters:
    -----------
    symptom_data : dict or pandas.DataFrame
        Dictionary where keys are symptom names and values are frequencies,
        or DataFrame with columns ['symptom', 'frequency'] or similar.
    top_n : int, optional
        Number of top symptoms to display (default: 30)
    
    Returns:
    --------
    None
        Displays the plot.
    """
    # Define disorder terms to exclude (not symptoms)
    DISORDER_LABELS = {
        'depression', 'anxiety', 'stress', 'ptsd', 
        'trauma', 'ocd', 'bipolar', 'schizophrenia',
        'disorder', 'syndrome', 'disease'
    }
    
    # Convert input to dictionary if needed
    if isinstance(symptom_data, pd.DataFrame):
        # Assume first column is symptom name, second is frequency
        symptom_dict = dict(zip(symptom_data.iloc[:, 0], symptom_data.iloc[:, 1]))
    else:
        symptom_dict = symptom_data.copy()
    
    # Filter out disorder-level concepts
    filtered_symptoms = {
        symptom: freq for symptom, freq in symptom_dict.items()
        if symptom.lower() not in DISORDER_LABELS
    }
    
    # Print diagnostic information
    num_available = len(filtered_symptoms)
    print(f"Number of unique symptoms after filtering: {num_available}")
    
    # Validate and warn if insufficient data
    if num_available < top_n:
        print(f"⚠️  WARNING: Only {num_available} symptoms available. Plotting all {num_available} instead of {top_n}.")
        actual_n = num_available
    else:
        actual_n = top_n
        print(f"✓ Plotting top {actual_n} symptoms by frequency.")
    
    # Sort by frequency in descending order and select top N
    sorted_symptoms = sorted(filtered_symptoms.items(), key=lambda x: x[1], reverse=True)
    top_symptoms = sorted_symptoms[:actual_n]  # Use .head(30) equivalent
    
    # Separate symptoms and frequencies
    symptoms = [item[0] for item in top_symptoms]
    frequencies = [item[1] for item in top_symptoms]
    
    # Set publication-quality style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create figure with appropriate size (minimum height = 12 for 30 symptoms)
    fig, ax = plt.subplots(figsize=(12, max(12, len(symptoms) * 0.5)))
    
    # Define calming gradient color palette (teal to soft purple)
    # Creates a soothing gradient suitable for mental health research
    n_bars = len(symptoms)
    colors = plt.cm.cool([(i / max(n_bars - 1, 1)) * 0.6 + 0.2 for i in range(n_bars)])
    
    # Create horizontal bar chart with gradient colors
    bars = ax.barh(symptoms, frequencies, color=colors, alpha=0.85, edgecolor='#4A6B7C', linewidth=0.8)
    
    # Add value labels at the end of each bar
    for i, (bar, freq) in enumerate(zip(bars, frequencies)):
        ax.text(freq + max(frequencies) * 0.01, i, f'{freq}', 
                va='center', ha='left', fontsize=10, color='#2C3E50', fontweight='500')
    
    # Set labels and title
    ax.set_xlabel('Frequency', fontsize=12, fontweight='bold', color='#333333')
    ax.set_ylabel('Symptoms', fontsize=12, fontweight='bold', color='#333333')
    ax.set_title('Top 30 Clinical Symptoms Extracted from Social Media Data', 
                 fontsize=14, fontweight='bold', color='#1a1a1a', pad=20)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    # Lighten grid lines
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Adjust tick parameters
    ax.tick_params(axis='both', which='major', labelsize=10, colors='#333333')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Display the plot
    plt.show()


# Example usage
if __name__ == "__main__":
    # Sample data with both disorders and symptoms
    sample_data = {
        'Fatigue': 156,
        'Insomnia': 142,
        'Anxiety': 138,  # This will be filtered out (disorder)
        'Irritability': 128,
        'Depression': 125,  # This will be filtered out (disorder)
        'Restlessness': 118,
        'Headache': 112,
        'Poor Concentration': 108,
        'Hopelessness': 98,
        'Panic': 95,
        'Stress': 92,  # This will be filtered out (disorder)
        'Muscle Tension': 88,
        'Rapid Heartbeat': 85,
        'Sweating': 78,
        'Trembling': 72,
        'Nausea': 68,
        'Dizziness': 65,
        'Chest Pain': 58
    }
    
    # Plot EXACTLY top 30 symptoms (disorders automatically excluded)
    plot_top_symptoms(sample_data, top_n=30)
