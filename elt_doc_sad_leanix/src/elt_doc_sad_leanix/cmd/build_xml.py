#!/usr/bin/env python3
"""
Generate Workday Integration XML from a JSON Specification.
This script is designed to be the "Builder" in an LLM-driven workflow:
1. LLM reads SAD -> Produces JSON.
2. This script reads JSON -> Produces XML.
"""
import sys
import json
import argparse
from pathlib import Path
from elt_doc_sad_leanix.diagram_generator import WorkdayIntegrationDiagramGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate LeanIX XML from JSON Specification')
    parser.add_argument('json_path', help='Path to input JSON specification file')
    parser.add_argument('--output-dir', help='Directory to save the generated XML file')
    args = parser.parse_args()
    
    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"Error: File {json_path} not found")
        sys.exit(1)
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
        
    # Validate minimum requirements
    required_fields = ['title', 'integration_id', 'source_system', 'target_system']
    missing = [f for f in required_fields if f not in spec]
    if missing:
        print(f"Error: Missing required fields in JSON: {missing}")
        sys.exit(1)
        
    print(f"Generating XML for {spec.get('integration_id')} - {spec.get('title')}...")
    if 'template_id' in spec:
        print(f"Using Template Pattern: {spec['template_id']}")
    
    generator = WorkdayIntegrationDiagramGenerator()
    xml = generator.generate_xml(spec)
    
    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / json_path.with_suffix('.xml').name
    else:
        output_path = json_path.with_suffix('.xml')
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml)
        
    print(f"✅ Generated: {output_path}")

if __name__ == '__main__':
    main()
