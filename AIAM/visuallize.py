#https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
import seaborn as sns

class AffordanceModelVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Affordance Model Accuracy Visualizer")
        self.root.geometry("800x600")

        # Add a label to display instructions
        self.label = tk.Label(self.root, text="Load the dataset and visualize model accuracy.", font=("Arial", 14))
        self.label.pack(pady=20)

        # Button to load dataset
        self.load_button = tk.Button(self.root, text="Load Dataset", command=self.load_dataset, width=20, height=2)
        self.load_button.pack(pady=10)

        # Placeholder for metrics display
        self.metrics_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.metrics_label.pack(pady=10)

        # Placeholder for accuracy plot
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = None  # This will be updated when we plot

    def load_dataset(self):
        """Load dataset from file and compute accuracy and metrics."""
        # Open file dialog to select the dataset (in CSV format for example)
        file_path = filedialog.askopenfilename(title="Select Dataset", filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if not file_path:
            return

        try:
            # Load data (example assumes file is CSV with true labels and predictions)
            data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
            y_true = data[:, 0]  # Assuming true labels are in the first column
            y_pred = data[:, 1]  # Assuming predictions are in the second column

            # Calculate metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
            cm = confusion_matrix(y_true, y_pred)

            # Update metrics display
            metrics_text = f"Accuracy: {accuracy*100:.2f}%\n"
            metrics_text += f"Precision: {precision:.2f}\n"
            metrics_text += f"Recall: {recall:.2f}\n"
            metrics_text += f"F1-Score: {f1:.2f}\n"
            self.metrics_label.config(text=metrics_text)

            # Plot confusion matrix
            self.plot_confusion_matrix(cm)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset or calculate metrics: {e}")

    def plot_confusion_matrix(self, cm):
        """Plot confusion matrix using seaborn."""
        self.ax.clear()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=self.ax)
        self.ax.set_xlabel('Predicted')
        self.ax.set_ylabel('True')
        self.ax.set_title('Confusion Matrix')
        self.fig.tight_layout()

        # Draw the updated plot
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = self.fig.canvas
        self.canvas.get_tk_widget().pack(pady=20)

def main():
    root = tk.Tk()
    app = AffordanceModelVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
