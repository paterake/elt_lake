#!/usr/bin/env python3
"""
Workday Integration Diagram XML Generator
Generates diagrams.net XML from integration specifications
"""

import xml.etree.ElementTree as ET
import uuid
from typing import Dict, List

class WorkdayIntegrationDiagramGenerator:
    """Generate diagrams.net XML for Workday integrations"""
    
    # Color constants matching LeanIX standard
    WORKDAY_BLUE = "#497db0"
    VENDOR_ORANGE = "#ffa31f"
    INFRA_BROWN = "#d29270"
    
    def __init__(self):
        self.id_counter = 2  # Start at 2 (0 and 1 are reserved)
        
    def _next_id(self) -> str:
        """Get next available ID"""
        current = str(self.id_counter)
        self.id_counter += 1
        return current
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities for XML"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
    
    def create_root(self) -> ET.Element:
        """Create root mxGraphModel element"""
        root = ET.Element('mxGraphModel', {
            'dx': '240', 'dy': '-80', 'grid': '0', 'gridSize': '10',
            'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
            'fold': '0', 'page': '0', 'pageScale': '1',
            'pageWidth': '826', 'pageHeight': '1169',
            'math': '0', 'shadow': '0', 'lxXmlVersion': '1'
        })
        
        root_elem = ET.SubElement(root, 'root')
        
        # Add settings
        settings = ET.SubElement(root_elem, 'lx-settings', {'id': '0'})
        ET.SubElement(settings, 'mxCell', {'style': ''})
        
        # Add base cell
        ET.SubElement(root_elem, 'mxCell', {'id': '1', 'parent': '0', 'style': ''})
        
        return root
    
    def add_title(self, root: ET.Element, title: str):
        """Add diagram title"""
        root_elem = root.find('root')
        title_id = self._next_id()
        
        title_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': title_id,
            'parent': '1',
            'style': 'text;strokeColor=none;fillColor=none;html=1;fontSize=24;fontStyle=1;verticalAlign=middle;align=center;',
            'value': title,
            'vertex': '1'
        })
        ET.SubElement(title_cell, 'mxGeometry', {
            'height': '40', 'width': '800', 'x': '200', 'y': '80', 'as': 'geometry'
        })
    
    def add_system_box(self, root: ET.Element, label: str, x: int, y: int, 
                       width: int = 160, height: int = 160, 
                       is_workday: bool = True) -> str:
        """Add a system box (fact sheet)"""
        root_elem = root.find('root')
        box_id = self._next_id()
        
        color = self.WORKDAY_BLUE if is_workday else self.VENDOR_ORANGE
        fact_sheet_type = "Application" if is_workday else "Provider"
        
        box = ET.SubElement(root_elem, 'object', {
            'type': 'factSheet',
            'label': label,
            'factSheetType': fact_sheet_type,
            'factSheetId': str(uuid.uuid4()),
            'id': box_id
        })
        
        if not is_workday:
            box.set('lxCustomLabel', '1')
        
        cell = ET.SubElement(box, 'mxCell', {
            'parent': '1',
            'style': f'shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor={color};strokeColor={color};fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1',
            'vertex': '1'
        })
        ET.SubElement(cell, 'mxGeometry', {
            'height': str(height), 'width': str(width), 
            'x': str(x), 'y': str(y), 'as': 'geometry'
        })
        
        return box_id
    
    def add_arrow(self, root: ET.Element, source_id: str, target_id: str, 
                  waypoints: List[tuple] = None):
        """Add an arrow between systems"""
        root_elem = root.find('root')
        arrow_id = self._next_id()
        
        arrow = ET.SubElement(root_elem, 'mxCell', {
            'id': arrow_id,
            'edge': '1',
            'parent': '1',
            'source': source_id,
            'target': target_id,
            'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
        })
        
        geo = ET.SubElement(arrow, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        
        if waypoints:
            points = ET.SubElement(geo, 'Array', {'as': 'points'})
            for x, y in waypoints:
                ET.SubElement(points, 'mxPoint', {'x': str(x), 'y': str(y)})
    
    def add_text_label(self, root: ET.Element, text: str, x: int, y: int,
                       width: int = 300, height: int = 50, font_size: int = 14):
        """Add a text label"""
        root_elem = root.find('root')
        label_id = self._next_id()
        
        label_obj = ET.SubElement(root_elem, 'UserObject', {
            'label': text,
            'placeholders': '1',
            'name': 'Variable',
            'id': label_id
        })
        
        label_cell = ET.SubElement(label_obj, 'mxCell', {
            'parent': '1',
            'style': f'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize={font_size};',
            'vertex': '1'
        })
        ET.SubElement(label_cell, 'mxGeometry', {
            'height': str(height), 'width': str(width),
            'x': str(x), 'y': str(y), 'as': 'geometry'
        })
    
    def add_info_box(self, root: ET.Element, title: str, items: List[str],
                     x: int, y: int, width: int = 530, height: int = 280):
        """Add an information box with bullet points"""
        root_elem = root.find('root')
        box_id = self._next_id()
        
        content = f"<div><b>{title}</b></div><div><ul>"
        for item in items:
            content += f"<li>{item}</li>"
        content += "</ul></div>"
        
        box_obj = ET.SubElement(root_elem, 'UserObject', {
            'label': content,
            'placeholders': '1',
            'name': 'Variable',
            'id': box_id
        })
        
        box_cell = ET.SubElement(box_obj, 'mxCell', {
            'parent': '1',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=14;',
            'vertex': '1'
        })
        ET.SubElement(box_cell, 'mxGeometry', {
            'height': str(height), 'width': str(width),
            'x': str(x), 'y': str(y), 'as': 'geometry'
        })
    
    def generate_xml(self, integration_spec: Dict) -> str:
        """
        Generate complete XML from integration specification
        
        Args:
            integration_spec: Dict containing:
                - title: Diagram title
                - integration_id: INT001, INT006, etc.
                - source_system: Source system name
                - target_system: Target system name
                - intermediary: Optional middle system
                - direction: 'outbound', 'inbound', or 'bidirectional'
                - flow_labels: List of dicts with text, x, y, width, height
                - security_details: List of security items
                - system_of_record: List of SOR items
                - key_attributes: List of key attributes
        """
        
        root = self.create_root()
        
        # Add title
        self.add_title(root, integration_spec['title'])
        
        # Add systems based on pattern
        if integration_spec.get('intermediary'):
            # Three-box pattern
            source_id = self.add_system_box(root, integration_spec['source_system'], 
                                           240, 280, is_workday=True)
            middle_id = self.add_system_box(root, 
                                           f"{integration_spec['intermediary']}<div><b>{integration_spec['integration_id']}</b></div>",
                                           560, 280, width=170, is_workday=False)
            target_id = self.add_system_box(root, integration_spec['target_system'],
                                           880, 280, is_workday=False)
            
            # Add arrows
            self.add_arrow(root, source_id, middle_id)
            self.add_arrow(root, middle_id, target_id)
            
        else:
            # Two-box pattern
            source_id = self.add_system_box(root, integration_spec['source_system'],
                                           240, 280, is_workday=True)
            target_id = self.add_system_box(root,
                                           f"{integration_spec['target_system']}<div><b>{integration_spec['integration_id']}</b></div>",
                                           800, 280, width=170, is_workday=False)
            
            # Add arrows based on direction
            if integration_spec['direction'] in ['outbound', 'bidirectional']:
                self.add_arrow(root, source_id, target_id,
                              waypoints=[(320, 240), (885, 240)])
            
            if integration_spec['direction'] in ['inbound', 'bidirectional']:
                self.add_arrow(root, target_id, source_id,
                              waypoints=[(885, 480), (320, 480)])
        
        # Add flow labels
        for label in integration_spec.get('flow_labels', []):
            self.add_text_label(root, label['text'], label['x'], label['y'],
                               label.get('width', 300), label.get('height', 50))
        
        # Add security details box
        self.add_info_box(root, "SECURITY & TECHNICAL DETAILS",
                         integration_spec.get('security_details', []),
                         27, 840)
        
        # Add System of Record box
        self.add_info_box(root, "SYSTEM OF RECORD",
                         integration_spec.get('system_of_record', []),
                         560, 840, height=90)
        
        # Add Key Attributes box
        self.add_info_box(root, "KEY ATTRIBUTES SYNCHRONIZED",
                         integration_spec.get('key_attributes', []),
                         560, 930, height=110)
        
        # Convert to string
        return ET.tostring(root, encoding='unicode')


# Example: Barclaycard Integration
def generate_barclaycard_diagram():
    """Generate XML for Barclaycard integration"""
    
    spec = {
        'title': 'Workday Barclaycard Credit Card Transactions Integration SFTP',
        'integration_id': 'INT006',
        'source_system': 'Workday Financial Management',
        'intermediary': 'FA SFTP',
        'target_system': 'Barclaycard',
        'direction': 'inbound',  # Barclaycard → SFTP → Workday
        'flow_labels': [
            {
                'text': 'Barclaycard delivers Visa VCF4.4 scrubbed file to FA SFTP<div>(PGP encrypted, SSH authentication)</div><div>Daily scheduled delivery</div>',
                'x': 100, 'y': 180, 'width': 350, 'height': 80
            },
            {
                'text': 'Workday retrieves encrypted VCF4.4 file from SFTP<div>Scheduled daily retrieval (time TBC)</div><div>File decrypted using Workday private PGP key</div>',
                'x': 700, 'y': 180, 'width': 350, 'height': 80
            }
        ],
        'security_details': [
            'Integration Type: Cloud Connect - Financials (Credit Card)',
            'Template: Import Visa VCF4 File (Scrubbed) - Delivered',
            'File Format: Visa Commercial Format (VCF) Version 4.4.x, Tab-delimited',
            'Expected Volume: TBC monthly statement transactions',
            'Encryption: PGP for data at rest (MANDATORY); TLS/SSL for SFTP',
            'Authentication: SSH key authentication',
            'SFTP Server: FA Managed SFTP',
            'File Naming: TBC (to be confirmed with Barclaycard)',
            'Data Retention: Integration outputs stored in Workday for 180 days',
            'Frequency: Daily (scheduled time TBC)',
            'ISU Account: ISU_INT006_Barclaycard_CreditCard_Inbound'
        ],
        'system_of_record': [
            'Workday Expenses: Credit card transactions, cardholder data',
            'Barclaycard: Source system for credit card transaction data',
            'Scope: The Football Association Limited employees only'
        ],
        'key_attributes': [
            'Cardholder Information: Employee ID, Name, Masked Card Number',
            'Transaction Details: Transaction Date, Post Date, Merchant Name, Amount',
            'Enhanced Airline Data: Ticket Number, Passenger Name, Origin, Destination',
            'Enhanced Hotel Data: Check-in/out Dates, Hotel Name, Room Rate',
            'Enhanced Car Rental Data: Agreement Number, Dates, Locations'
        ]
    }
    
    generator = WorkdayIntegrationDiagramGenerator()
    xml = generator.generate_xml(spec)
    
    # Save to file
    filename = f'{spec["integration_id"]}_{spec["target_system"]}.xml'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml)
    
    print(f"✅ Generated: {filename}")
    print(f"📊 Ready to import into LeanIX!")
    
    return filename


if __name__ == '__main__':
    generate_barclaycard_diagram()
