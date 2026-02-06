import matplotlib.pyplot as plt
import numpy as np

# Data - Taken directly from KG triple evaluation output
# Precision: 0.615385
# Recall: 0.615385
# F1-Score: 0.615385
# Accuracy (closed-world): 0.814815
metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
values = [0.6154, 0.6154, 0.6154, 0.8148]

def plot_kg_metrics():
    # Set professional style styling
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Calm, professional academic color palette
    # Sage Green, Muted Gold, Soft Terracotta, Deep Blue-Grey
    colors = ['#5D9C86', '#D4AC6E', '#C06C84', '#455A64']
    
    # Plot bars with reduced thickness
    x_pos = np.arange(len(metrics))
    width = 0.5
    bars = ax.bar(x_pos, values, width, color=colors, zorder=3)
    
    # Axis configuration
    ax.set_ylabel('Score (0 to 1)', fontsize=12, labelpad=12, fontweight='medium')
    ax.set_title('Knowledge Graph Triple Evaluation Performance', fontsize=14, pad=20, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(metrics, fontsize=11)
    
    # Set Y-axis limits strictly from 0 to 1
    ax.set_ylim(0, 1)
    
    # Remove unnecessary borders (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#888888')
    ax.spines['bottom'].set_color('#888888')
    ax.tick_params(axis='both', which='major', labelsize=10, color='#888888')
    
    # Add light grid for readability
    ax.grid(axis='y', linestyle='--', alpha=0.3, zorder=0, color='gray')
    
    # Add numeric value labels on each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.015,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=10, 
                fontweight='bold', color='#333333')
    
    # Clean layout
    plt.tight_layout()
    
    # Save the plot
    output_path = 'kg_triple_metrics_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    plot_kg_metrics()
