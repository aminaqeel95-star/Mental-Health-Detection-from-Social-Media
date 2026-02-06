"""
Script to visualize the pipeline accuracy metrics.
Creates a professional bar chart showing stage-wise performance and final accuracy.
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_pipeline_accuracy():
    """
    Plot the stage-wise performance metrics and final pipeline accuracy.
    """
    # Stage-wise accuracy values
    stage1_accuracy = 1.0000  # NER (Concept Recall)
    stage2_accuracy = 0.8148  # Triple Accuracy
    stage3_accuracy = 0.8202  # Comparison Accuracy
    final_accuracy = 0.8720   # Final Pipeline Accuracy
    
    # Weights
    w1 = 0.30
    w2 = 0.40
    w3 = 0.30
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ============================================================
    # Subplot 1: Stage-wise Performance
    # ============================================================
    stages = ['Stage 1\n(NER Concept\nRecall)', 
              'Stage 2\n(Triple\nAccuracy)', 
              'Stage 3\n(Comparison\nAccuracy)']
    accuracies = [stage1_accuracy, stage2_accuracy, stage3_accuracy]
    weights = [w1, w2, w3]
    
    # Color palette: professional academic colors
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    # Create bars with reduced width for elegance
    bars = ax1.bar(stages, accuracies, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.4)
    
    # Add value labels on bars
    for i, (bar, acc, weight) in enumerate(zip(bars, accuracies, weights)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{acc:.4f}\n(w={weight:.2f})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Styling
    ax1.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax1.set_title('Stage-wise Performance Metrics', fontsize=14, fontweight='bold', pad=20)
    ax1.set_ylim(0, 1.15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
    ax1.set_axisbelow(True)
    
    # ============================================================
    # Subplot 2: Final Pipeline Accuracy
    # ============================================================
    # Single bar for final accuracy with reduced width
    bar_final = ax2.bar(['Final Pipeline\nAccuracy'], [final_accuracy], 
                        color='#06A77D', alpha=0.85, edgecolor='black', linewidth=1.5, width=0.3)
    
    # Add value label
    ax2.text(0, final_accuracy + 0.02, f'{final_accuracy:.4f}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add weighted formula annotation
    formula_text = f'= {w1:.2f}×{stage1_accuracy:.4f} + {w2:.2f}×{stage2_accuracy:.4f} + {w3:.2f}×{stage3_accuracy:.4f}'
    ax2.text(0, final_accuracy - 0.15, formula_text,
            ha='center', va='top', fontsize=9, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.3))
    
    # Styling
    ax2.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax2.set_title('Final Pipeline Accuracy', fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylim(0, 1.15)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
    ax2.set_axisbelow(True)
    
    # Overall title
    fig.suptitle('Clinical NLP Pipeline Performance Evaluation', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    output_path = 'pipeline_accuracy_plot.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n[+] Plot saved to: {output_path}")
    
    # Show plot
    plt.show()
    
    # Print summary
    print("\n" + "="*60)
    print("STAGE-WISE PERFORMANCE METRICS:")
    print("="*60)
    print(f"Stage 1 (NER Concept Recall):    {stage1_accuracy:.4f} (weight: {w1:.2f})")
    print(f"Stage 2 (Triple Accuracy):       {stage2_accuracy:.4f} (weight: {w2:.2f})")
    print(f"Stage 3 (Comparison Accuracy):   {stage3_accuracy:.4f} (weight: {w3:.2f})")
    print("-" * 60)
    print(f"Final Pipeline Accuracy:         {final_accuracy:.4f}")
    print("="*60)

if __name__ == "__main__":
    plot_pipeline_accuracy()
