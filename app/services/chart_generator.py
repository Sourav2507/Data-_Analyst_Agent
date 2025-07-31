import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import seaborn as sns

class ChartGenerator:
    def __init__(self):
        sns.set()

    def create_scatterplot_with_regression(self, x, y, x_label="X", y_label="Y", title="Scatterplot") -> str:
        fig, ax = plt.subplots(figsize=(8, 5))

        ax.scatter(x, y, alpha=0.6, s=40)
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), "r--", linewidth=2, label="Regression line")  # dotted red line

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_bytes = buf.read()

        # Optional: You may compress/reduce image size here to keep under 100,000 bytes if needed

        img_b64 = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{img_b64}"
