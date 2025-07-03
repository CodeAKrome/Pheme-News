import matplotlib.pyplot as plt
import numpy as np

# Enable inline plotting for Jupyter
%matplotlib inline

# Sample data - replace with your actual data
news_sources = ['CNN', 'Fox News', 'BBC', 'Reuters', 'Associated Press', 'The Guardian', 'Wall Street Journal']
positive_counts = [45, 38, 52, 41, 48, 35, 42]
negative_counts = [32, 28, 25, 22, 18, 30, 24]

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create horizontal bar chart
y_pos = np.arange(len(news_sources))

# Plot positive bars (to the right)
bars_pos = ax.barh(y_pos, positive_counts, align='center', color='#2E8B57', alpha=0.8, label='Positive')

# Plot negative bars (to the left, using negative values)
bars_neg = ax.barh(y_pos, [-x for x in negative_counts], align='center', color='#DC143C', alpha=0.8, label='Negative')

# Customize the chart
ax.set_yticks(y_pos)
ax.set_yticklabels(news_sources)
ax.invert_yaxis()  # Labels read top-to-bottom
ax.set_xlabel('Sentiment Count')
ax.set_title('News Sources: Positive vs Negative Sentiment Analysis', fontsize=16, fontweight='bold', pad=20)

# Add vertical line at x=0 for reference
ax.axvline(x=0, color='black', linewidth=0.8, alpha=0.7)

# Add grid for better readability
ax.grid(axis='x', alpha=0.3, linestyle='--')

# Add legend
ax.legend(loc='upper right')

# Add value labels on bars
for i, (pos, neg) in enumerate(zip(positive_counts, negative_counts)):
    # Positive values
    ax.text(pos + 1, i, str(pos), va='center', ha='left', fontweight='bold')
    # Negative values
    ax.text(-neg - 1, i, str(neg), va='center', ha='right', fontweight='bold')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Display the chart
plt.show()

# Optional: Save the chart
# plt.savefig('news_sentiment_chart.png', dpi=300, bbox_inches='tight')