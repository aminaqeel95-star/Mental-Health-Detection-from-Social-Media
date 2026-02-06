import matplotlib.pyplot as plt
import numpy as np

# Data - Taken directly from KG-RAG comparison evaluation output (system_comparison_summary.txt)
# Total Posts Analyzed: 990
# Total Agreement (MATCH): 812
# Total Conflicts (MISMATCH): 178
# Accuracy: 82.02%
categories = ['Match\n(Agreement)', 'Mismatch\n(Conflict)']
values = [812, 178]
accuracy_percentage = 82.02

def plot_comparison_results():
    # Set professional style styling
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Calm, professional academic color palette
    # Muted Green for Match, Muted Red/Rose for Mismatch
    colors = ['#5D9C86', '#C06C84']
    
    # Plot bars with reduced thickness
    x_pos = np.arange(len(categories))
    width = 0.5
    bars = ax.bar(x_pos, values, width, color=colors, zorder=3)
    
    # Axis configuration
    ax.set_ylabel('Number of Posts', fontsize=12, labelpad=12, fontweight='medium')
    ax.set_title('KG–RAG Comparison Results', fontsize=14, pad=20, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, fontsize=11)
    
    # Set Y-axis limit with some headroom
    ax.set_ylim(0, max(values) * 1.15)
    
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
        ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, 
                fontweight='bold', color='#333333')
                
    # Annotate agreement accuracy
    plt.text(0.5, 0.9, f"Agreement Rate: {accuracy_percentage}%", 
             transform=ax.transAxes, ha='center', fontsize=12, 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cccccc', boxstyle='round,pad=0.5'))
    
    # Clean layout
    plt.tight_layout()
    
    # Save the plot
    output_path = 'kg_rag_comparison_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    plot_comparison_results()
