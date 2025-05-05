import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import os

app = FastAPI()
LM_STUDIO_URL = os.getenv('LM_STUDIO_URL', 'http://localhost:1234/v1')
IMG_DIR = "/app/img"

# Ensure img directory exists
os.makedirs(IMG_DIR, exist_ok=True)

class Record(BaseModel):
    text: str

class BulkInput(BaseModel):
    records: list[Record]

def extract_svo_tuples(text: str) -> list[dict]:
    """Send text to LM-Studio and extract SVO tuples."""
    try:
        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": "Extract subject-verb-object tuples from the input text. Return as a JSON list of objects with 'subject', 'verb', and 'object' fields."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "max_tokens": 512
        }
        
        response = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        svo_text = result['choices'][0]['message']['content']
        return json.loads(svo_text)
    except Exception as e:
        print(f"Error in SVO extraction: {str(e)}")
        return []

def create_digraph(svo_tuples: list[dict]) -> str:
    """Create a directed graph from SVO tuples and save as PNG in img directory."""
    G = nx.DiGraph()
    
    for svo in svo_tuples:
        subject = svo.get('subject', '').strip()
        verb = svo.get('verb', '').strip()
        obj = svo.get('object', '').strip()
        
        if subject and verb and obj:
            G.add_edge(subject, obj, verb=verb)
    
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=10, arrows=True)
    
    edge_labels = nx.get_edge_attributes(G, 'verb')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(IMG_DIR, f"digraph_{timestamp}.png")
    
    plt.savefig(output_path, format='png', bbox_inches='tight')
    plt.close()
    
    return output_path

@app.post("/bulk_load")
async def bulk_load(input_data: BulkInput):
    try:
        all_svo_tuples = []
        for record in input_data.records:
            if record.text:
                svo_tuples = extract_svo_tuples(record.text)
                all_svo_tuples.extend(svo_tuples)
        
        if not all_svo_tuples:
            raise HTTPException(status_code=400, detail="No valid SVO tuples extracted")
        
        graph_path = create_digraph(all_svo_tuples)
        
        return FileResponse(
            graph_path,
            media_type='image/png',
            filename=os.path.basename(graph_path)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
