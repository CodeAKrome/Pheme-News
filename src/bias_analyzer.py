import gradio as gr
import json
from collections import defaultdict


def analyze_bias():
    stats_by_source = defaultdict(lambda: defaultdict(int))
    with open("/Users/kyle/hub/Pheme-News/cache/dedupe.jsonl", "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                source = data.get("source")
                stats = data.get("stats")
                if source and stats:
                    for key, value in stats.items():
                        stats_by_source[source][key] += value
            except json.JSONDecodeError:
                continue

    # Prepare data for Gradio output
    html_output = "<html><head><style>table { width: 100%; border-collapse: collapse; } th, td { border: 1px solid black; padding: 8px; text-align: left; }</style></head><body>"
    html_output += "<h1>Media Bias Stats by Source</h1>"
    html_output += "<table>"

    # Header
    html_output += "<tr><th>Source</th>"
    all_keys = sorted(
        set(k for source in stats_by_source.values() for k in source.keys())
    )
    for key in all_keys:
        html_output += f"<th>{key}</th>"
    html_output += "</tr>"

    # Data
    for source, stats in sorted(stats_by_source.items()):
        html_output += f"<tr><td>{source}</td>"
        for key in all_keys:
            html_output += f"<td>{stats.get(key, 0)}</td>"
        html_output += "</tr>"

    html_output += "</table></body></html>"
    return html_output


iface = gr.Interface(
    fn=analyze_bias,
    inputs=[],
    outputs=gr.HTML(),
    title="Media Bias Analyzer",
    description="Displays statistics from cache/dedupe.jsonl, grouped by media source.",
)

if __name__ == "__main__":
    iface.launch()
