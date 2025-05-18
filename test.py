import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.patches import Circle

# Load and normalize data
def load_normalized_data(file_path):
    df = pd.read_csv(file_path)
    class_col = [col for col in df.columns if col.lower() == 'class'][0]
    features = [col for col in df.columns if col != class_col]
    df_norm = df.copy()
    df_norm[features] = (df[features] - df[features].min()) / (df[features].max() - df[features].min())
    return df_norm, features, class_col

# Circle projection per attribute
def project_circle(ax, data, center, radius, attr_angle, values, class_colors, size=1.0, rot=0.0):
    n = len(values)
    # Draw the main attribute node
    ax.plot(center[0], center[1], 'o', color='gray', markersize=6)
    
    # Calculate positions around the circle based on attribute values
    for i in range(n):
        # Scale value (0-1) to an angle around the attribute circle
        value_angle = 2 * np.pi * values[i] + rot
        
        # Calculate position on the attribute circle
        x = center[0] + size * radius * np.cos(value_angle)
        y = center[1] + size * radius * np.sin(value_angle)
        
        # Plot the data point
        ax.plot(x, y, 'o', color=class_colors[i], markersize=4, alpha=0.8)

# Main visualization function
def visualize(data, features, class_col):
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(left=0.1, bottom=0.3)
    ax.set_aspect('equal')
    ax.axis('off')

    colors = plt.cm.tab10(data[class_col].astype('category').cat.codes / data[class_col].nunique())

    # Initial parameters
    attr_radius = 1.0
    attr_rot = 0.0
    global_rot = 0.0
    outer_radius = 5.0
    num_attrs = len(features)
    
    # Calculate maximum attribute size before overlapping would occur
    # This is based on the chord length between adjacent attribute centers
    max_attr_size = outer_radius * np.sin(np.pi / num_attrs) / attr_radius

    # Drawing function
    def draw(attr_size, attr_rot, global_rot):
        ax.clear()
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw the outer circle where all attribute circles are positioned
        outer_circle = plt.Circle((0, 0), outer_radius, fill=False, color='lightgray', linestyle='--', linewidth=1)
        ax.add_patch(outer_circle)
        
        # Store the positions of each data point in each attribute circle
        positions = {}
        
        # First pass: draw all attribute circles and calculate positions
        for i, attr in enumerate(features):
            angle = 2 * np.pi * i / num_attrs + global_rot
            center = (outer_radius * np.cos(angle), outer_radius * np.sin(angle))
            values = data[attr].values
            
            # Draw the main attribute node
            ax.plot(center[0], center[1], 'o', color='gray', markersize=6)
            
            # Draw the attribute circle (axis)
            attr_circle = plt.Circle(center, attr_size * attr_radius, fill=False, color='gray', linestyle='-', linewidth=0.8)
            ax.add_patch(attr_circle)
            
            # Calculate positions for this attribute
            positions[attr] = []
            for j in range(len(values)):
                value_angle = 2 * np.pi * values[j] + attr_rot
                x = center[0] + attr_size * attr_radius * np.cos(value_angle)
                y = center[1] + attr_size * attr_radius * np.sin(value_angle)
                positions[attr].append((x, y))
                
                # Plot the data point
                ax.plot(x, y, 'o', color=colors[j], markersize=4, alpha=0.8)
        
        # Second pass: connect points for each data case with polylines
        for j in range(len(data)):
            x_points = []
            y_points = []
            for attr in features:
                x, y = positions[attr][j]
                x_points.append(x)
                y_points.append(y)
            
            # Connect last point back to first to close the loop
            if len(features) > 1:
                x_points.append(x_points[0])
                y_points.append(y_points[0])
            
            # Draw the polyline connecting points for this case
            ax.plot(x_points, y_points, '-', color=colors[j], alpha=0.3, linewidth=1)
        
        fig.canvas.draw_idle()

    # Initial draw
    draw(attr_radius, attr_rot, global_rot)

    # Sliders
    ax_size = plt.axes([0.1, 0.2, 0.8, 0.03])
    ax_attr_rot = plt.axes([0.1, 0.15, 0.8, 0.03])
    ax_global_rot = plt.axes([0.1, 0.1, 0.8, 0.03])
    s_size = Slider(ax_size, 'Attr Size', 0.1, max_attr_size, valinit=1.0)
    s_attr_rot = Slider(ax_attr_rot, 'Attr Rotation', 0.0, 2*np.pi, valinit=0.0)
    s_global_rot = Slider(ax_global_rot, 'Global Rotation', 0.0, 2*np.pi, valinit=0.0)

    # Update
    def update(val):
        draw(s_size.val, s_attr_rot.val, s_global_rot.val)

    s_size.on_changed(update)
    s_attr_rot.on_changed(update)
    s_global_rot.on_changed(update)

    plt.show()

# Usage
if __name__ == '__main__':
    data, features, class_col = load_normalized_data('wbc9.csv')  # Replace with your file
    visualize(data, features, class_col)
