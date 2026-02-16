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
                       is_workday: bool = True, fact_sheet_id: str = None,
                       fact_sheet_type: str = None,
                       use_fact_sheet: bool = None) -> str:
        """
        Add a system box - either as a fact sheet object (Workday) or plain mxCell (vendors).

        Args:
            use_fact_sheet: If True, wrap in fact sheet object. If None, auto-detect (True for Workday only)
        """
        root_elem = root.find('root')
        box_id = self._next_id()

        # By default, only use fact sheet wrapper when a valid fact_sheet_id is provided
        if use_fact_sheet is None:
            use_fact_sheet = bool(fact_sheet_id)

        color = self.WORKDAY_BLUE if is_workday else self.VENDOR_ORANGE

        if use_fact_sheet:
            # Fact sheet object wrapper (for Workday)
            if not fact_sheet_type:
                fact_sheet_type = "Application"

            box = ET.SubElement(root_elem, 'object', {
                'type': 'factSheet',
                'label': label,
                'factSheetType': fact_sheet_type,
                'factSheetId': fact_sheet_id,
                'id': box_id,
                'lxCustomLabel': '1'
            })

            # Inner mxCell must have its own id for stable import
            inner_id = self._next_id()
            cell = ET.SubElement(box, 'mxCell', {
                'id': inner_id,
                'parent': '1',
                'style': f'shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor={color};strokeColor={color};fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1',
                'vertex': '1'
            })
        else:
            # Plain mxCell box (for vendors) - matches working reference style
            cell = ET.SubElement(root_elem, 'mxCell', {
                'id': box_id,
                'parent': '1',
                # Avoid light-dark() function for maximum LeanIX compatibility
                'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#497db0;fontColor=#ffffff;fontSize=14;strokeWidth=0;labelBorderColor=default;align=center;',
                'value': label,
                'vertex': '1'
            })

        ET.SubElement(cell, 'mxGeometry', {
            'height': str(height), 'width': str(width),
            'x': str(x), 'y': str(y), 'as': 'geometry'
        })

        return box_id
    
    def add_arrow(self, root: ET.Element, source_id: str, target_id: str, 
                  waypoints: List[tuple] = None, fact_sheet_id: str = None, 
                  fact_sheet_label: str = None):
        """Add an arrow between systems"""
        root_elem = root.find('root')
        arrow_id = self._next_id()
        
        # Determine parent element (root or object wrapper)
        if fact_sheet_id:
            parent = ET.SubElement(root_elem, 'object', {
                'type': 'factSheet',
                'label': fact_sheet_label or "Interface",
                'factSheetType': 'Interface',
                'factSheetId': fact_sheet_id,
                'id': arrow_id
            })
            # Use a new ID for the inner mxCell
            inner_id = self._next_id()
        else:
            parent = root_elem
            inner_id = arrow_id
            
        arrow = ET.SubElement(parent, 'mxCell', {
            'id': inner_id,
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
    
    def add_process_table(self, root: ET.Element, items: Dict[str, str], x: int, y: int, width: int = 1186):
        """Add a process table with 4 columns"""
        root_elem = root.find('root')
        table_id = self._next_id()
        
        # Table container
        table = ET.SubElement(root_elem, 'mxCell', {
            'id': table_id,
            'parent': '1',
            'style': 'childLayout=tableLayout;recursiveResize=0;shadow=0;fillColor=none;verticalAlign=top;',
            'value': '',
            'vertex': '1'
        })
        ET.SubElement(table, 'mxGeometry', {
            'height': '240', 'width': str(width), 'x': str(x), 'y': str(y), 'as': 'geometry'
        })
        
        # Header row
        header_row_id = self._next_id()
        header_row = ET.SubElement(table, 'mxCell', {
            'id': header_row_id,
            'parent': table_id,
            'style': 'shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;',
            'value': '',
            'vertex': '1'
        })
        ET.SubElement(header_row, 'mxGeometry', {'height': '52', 'width': str(width), 'as': 'geometry'})
        
        headers = ["Extraction Method", "Security Controls", "Transmission", "Processing"]
        col_width = width // 4
        
        for header in headers:
            cell_id = self._next_id()
            cell = ET.SubElement(header_row, 'mxCell', {
                'id': cell_id,
                'parent': header_row_id,
                'style': 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=center;whiteSpace=wrap;html=1;fontStyle=1;',
                'value': header,
                'vertex': '1'
            })
            geom = ET.SubElement(cell, 'mxGeometry', {'height': '52', 'width': str(col_width), 'as': 'geometry'})
            ET.SubElement(geom, 'mxRectangle', {'height': '52', 'width': str(col_width), 'as': 'alternateBounds'})
            
        # Content row
        content_row_id = self._next_id()
        content_row = ET.SubElement(table, 'mxCell', {
            'id': content_row_id,
            'parent': table_id,
            'style': 'shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;',
            'vertex': '1'
        })
        ET.SubElement(content_row, 'mxGeometry', {'height': '188', 'width': str(width), 'y': '52', 'as': 'geometry'})
        
        values = [
            items.get('process_extraction', 'N/A'),
            items.get('process_security', 'N/A'),
            items.get('process_transmission', 'N/A'),
            items.get('process_processing', 'N/A')
        ]
        
        for val in values:
            cell_id = self._next_id()
            cell = ET.SubElement(content_row, 'mxCell', {
                'id': cell_id,
                'parent': content_row_id,
                'style': 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=left;whiteSpace=wrap;html=1;verticalAlign=top;overflow=hidden;',
                'value': val,
                'vertex': '1'
            })
            geom = ET.SubElement(cell, 'mxGeometry', {'height': '188', 'width': str(col_width), 'as': 'geometry'})
            ET.SubElement(geom, 'mxRectangle', {'height': '188', 'width': str(col_width), 'as': 'alternateBounds'})

    def add_standalone_table(self, root: ET.Element, title: str,
                            col1_header: str, col2_header: str,
                            col1_content: str, col2_content: str,
                            x: int, y: int, col_width: int = 296):
        """
        Add a 2-column table using standalone cells (for multi-connector integrations).
        This creates separate mxCell elements with parent="1" instead of nested table structure.
        """
        root_elem = root.find('root')

        # Title cell
        title_id = self._next_id()
        title_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': title_id,
            'parent': '1',
            'style': 'text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;rounded=0;fontStyle=1',
            'value': title,
            'vertex': '1'
        })
        ET.SubElement(title_cell, 'mxGeometry', {
            'height': '30',
            'width': str(col_width * 2),
            'x': str(x),
            'y': str(y),
            'as': 'geometry'
        })

        # Helper function to add table cell
        def add_cell(value, cell_x, cell_y, height, is_header=False):
            cell_id = self._next_id()
            style = 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=center;whiteSpace=wrap;html=1;' if is_header else 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=left;whiteSpace=wrap;html=1;verticalAlign=top;'

            cell = ET.SubElement(root_elem, 'mxCell', {
                'id': cell_id,
                'parent': '1',
                'style': style,
                'value': value,
                'vertex': '1'
            })
            geom = ET.SubElement(cell, 'mxGeometry', {
                'height': str(height),
                'width': str(col_width),
                'x': str(cell_x),
                'y': str(cell_y),
                'as': 'geometry'
            })
            ET.SubElement(geom, 'mxRectangle', {
                'height': str(height),
                'width': str(col_width),
                'as': 'alternateBounds'
            })

        # Add header cells
        header_y = y + 40  # Below title
        add_cell(col1_header, x, header_y, 52, is_header=True)
        add_cell(col2_header, x + col_width, header_y, 52, is_header=True)

        # Add content cells
        content_y = header_y + 52
        add_cell(col1_content, x, content_y, 228, is_header=False)
        add_cell(col2_content, x + col_width, content_y, 228, is_header=False)

    def generate_xml(self, integration_spec: Dict) -> str:
        """
        Generate complete XML from integration specification
        """
        root = self.create_root()
        
        # Add title
        self.add_title(root, integration_spec['title'])
        
        direction = integration_spec.get('direction', 'outbound')
        intermediary = integration_spec.get('intermediary')
        template_id = integration_spec.get('template_id')

        target_system = integration_spec.get('target_system') or 'Target System'
        source_system = integration_spec.get('source_system') or 'Workday'

        # Multi-connector pattern (e.g., INT018 Barclays Banking)
        if template_id == 'multi_connector':
            # Layout: Workday <-> Gateway <-> Vendor Platform (left-aligned at x=100)
            # Workday at x=100, y=280
            source_id = self.add_system_box(root, source_system,
                                           100, 280, is_workday=True,
                                           fact_sheet_id=integration_spec.get('source_id'),
                                           fact_sheet_type=integration_spec.get('source_type'))

            # Gateway/Intermediary at x=650, y=280
            gateway_label = integration_spec.get('gateway_label') or intermediary or 'Gateway'
            middle_id = self.add_system_box(root, gateway_label,
                                           650, 280, is_workday=False,
                                           fact_sheet_id=integration_spec.get('intermediary_id'),
                                           fact_sheet_type=integration_spec.get('intermediary_type'))

            # Vendor Platform at x=1280, y=280
            target_id = self.add_system_box(root, target_system,
                                           1280, 280, is_workday=False,
                                           fact_sheet_id=integration_spec.get('target_id'),
                                           fact_sheet_type=integration_spec.get('target_type'))

            # Bidirectional arrows
            self.add_arrow(root, source_id, middle_id)
            self.add_arrow(root, middle_id, source_id)
            self.add_arrow(root, middle_id, target_id)
            self.add_arrow(root, target_id, middle_id)

        elif intermediary:
            # Three-box pattern
            if direction == 'outbound':
                # Outbound: Workday -> SFTP -> Vendor (Linear: y=110)
                source_id = self.add_system_box(root, source_system, 
                                               10, 110, is_workday=True,
                                               fact_sheet_id=integration_spec.get('source_id'),
                                               fact_sheet_type=integration_spec.get('source_type'))
                # SFTP (Middle)
                middle_id = self.add_system_box(root, 
                                               f"{intermediary}<div><b>{integration_spec['integration_id']}</b></div>",
                                               520, 110, width=170, is_workday=False,
                                               fact_sheet_id=integration_spec.get('intermediary_id'),
                                               fact_sheet_type=integration_spec.get('intermediary_type'))
                target_id = self.add_system_box(root, target_system,
                                               1036, 110, is_workday=False,
                                               fact_sheet_id=integration_spec.get('target_id'),
                                               fact_sheet_type=integration_spec.get('target_type'))
                
                # Arrows: Source -> Middle -> Target
                self.add_arrow(root, source_id, middle_id, 
                               fact_sheet_id=integration_spec.get('interface_id'),
                               fact_sheet_label=integration_spec.get('interface_label'))
                self.add_arrow(root, middle_id, target_id)
                
            else: # inbound or bidirectional (defaulting to inbound layout)
                # Inbound: Vendor -> SFTP -> Workday (y=280)
                # Note: 'source_system' is Workday, 'target_system' is Vendor in our spec
                # But visually: Target(Vendor) -> Middle(SFTP) -> Source(Workday)
                
                vendor_id = self.add_system_box(root, target_system,
                                               240, 280, is_workday=False,
                                               fact_sheet_id=integration_spec.get('target_id'),
                                               fact_sheet_type=integration_spec.get('target_type'))
                
                # SFTP (Middle)
                middle_id = self.add_system_box(root, 
                                               f"{intermediary}<div><b>{integration_spec['integration_id']}</b></div>",
                                               560, 280, width=170, is_workday=False,
                                               fact_sheet_id=integration_spec.get('intermediary_id'),
                                               fact_sheet_type=integration_spec.get('intermediary_type'))
                
                wd_id = self.add_system_box(root, source_system, 
                                           880, 280, is_workday=True,
                                           fact_sheet_id=integration_spec.get('source_id'),
                                           fact_sheet_type=integration_spec.get('source_type'))
                
                # Arrows
                if direction == 'inbound':
                    # Vendor -> SFTP -> Workday
                    self.add_arrow(root, vendor_id, middle_id)
                    self.add_arrow(root, middle_id, wd_id,
                                   fact_sheet_id=integration_spec.get('interface_id'),
                                   fact_sheet_label=integration_spec.get('interface_label'))
                else: # bidirectional
                    # Arrows both ways (simplified)
                    self.add_arrow(root, vendor_id, middle_id)
                    self.add_arrow(root, middle_id, vendor_id)
                    self.add_arrow(root, middle_id, wd_id,
                                   fact_sheet_id=integration_spec.get('interface_id'),
                                   fact_sheet_label=integration_spec.get('interface_label'))
                    self.add_arrow(root, wd_id, middle_id)
            
        else:
            # Two-box pattern

            source_id = self.add_system_box(root, source_system,
                                           240, 280, is_workday=True,
                                           fact_sheet_id=integration_spec.get('source_id'),
                                           fact_sheet_type=integration_spec.get('source_type'))
            target_id = self.add_system_box(root,
                                           f"{target_system}<div><b>{integration_spec['integration_id']}</b></div>",
                                           800, 280, width=170, is_workday=False,
                                           fact_sheet_id=integration_spec.get('target_id'),
                                           fact_sheet_type=integration_spec.get('target_type'))
            
            # Add arrows based on direction
            if integration_spec['direction'] in ['outbound', 'bidirectional']:
                self.add_arrow(root, source_id, target_id,
                              waypoints=[(320, 240), (885, 240)],
                              fact_sheet_id=integration_spec.get('interface_id'),
                              fact_sheet_label=integration_spec.get('interface_label'))
            
            if integration_spec['direction'] in ['inbound', 'bidirectional']:
                # For bidirectional, we might want the interface on both or just one.
                # If we already added it on outbound, maybe skip here or add same ID?
                # Usually bidirectional has one Interface entity.
                # If outbound existed, we already added it.
                # Let's add it here ONLY if direction is JUST inbound.
                fs_id = integration_spec.get('interface_id') if integration_spec['direction'] == 'inbound' else None
                
                self.add_arrow(root, target_id, source_id,
                              waypoints=[(885, 480), (320, 480)],
                              fact_sheet_id=fs_id,
                              fact_sheet_label=integration_spec.get('interface_label'))
        
        # Add flow labels
        for label in integration_spec.get('flow_labels', []):
            self.add_text_label(root, label['text'], label['x'], label['y'],
                               label.get('width', 300), label.get('height', 50))

        # Add Process Table(s)
        # Multi-connector integrations use 3 separate 2-column tables
        if integration_spec.get('template_id') == 'multi_connector':
            # Get sub-integration tables from spec
            sub_integrations = integration_spec.get('sub_integrations', [])

            if len(sub_integrations) >= 1:
                # INT018a - Outbound at y=640, x=100 (left-aligned)
                self.add_standalone_table(
                    root,
                    title=sub_integrations[0].get('title', ' INT018a OUTBOUND'),
                    col1_header=sub_integrations[0].get('col1_header', 'Column 1'),
                    col2_header=sub_integrations[0].get('col2_header', 'Column 2'),
                    col1_content=sub_integrations[0].get('col1_content', ''),
                    col2_content=sub_integrations[0].get('col2_content', ''),
                    x=100, y=640
                )

            if len(sub_integrations) >= 2:
                # INT018b - Inbound at y=640, x=740 (spaced from INT018a)
                self.add_standalone_table(
                    root,
                    title=sub_integrations[1].get('title', ' INT018b INBOUND'),
                    col1_header=sub_integrations[1].get('col1_header', 'Column 1'),
                    col2_header=sub_integrations[1].get('col2_header', 'Column 2'),
                    col1_content=sub_integrations[1].get('col1_content', ''),
                    col2_content=sub_integrations[1].get('col2_content', ''),
                    x=740, y=640
                )

            if len(sub_integrations) >= 3:
                # INT018c - Inbound at y=640, x=1380 (spaced from INT018b)
                self.add_standalone_table(
                    root,
                    title=sub_integrations[2].get('title', ' INT018c INBOUND'),
                    col1_header=sub_integrations[2].get('col1_header', 'Column 1'),
                    col2_header=sub_integrations[2].get('col2_header', 'Column 2'),
                    col1_content=sub_integrations[2].get('col1_content', ''),
                    col2_content=sub_integrations[2].get('col2_content', ''),
                    x=1380, y=640
                )
        else:
            # Standard single process table for other integration types
            self.add_process_table(root, integration_spec, x=27, y=500, width=1100)
        
        # Add information boxes in a 2x3 grid layout with consistent left alignment
        # Left margin: x=100, spacing between columns: 573px (530 width + 43 gap)
        # Row 1 (y=1320): Security, System of Record, Key Attributes
        # Row 2 (y=1650): Notes, Environment Strategy, Critical Constraints

        # Row 1, Column 1: Security & Technical Details
        security_items = integration_spec.get('security_details') or []
        if security_items:
            self.add_info_box(root, "SECURITY & TECHNICAL DETAILS",
                             security_items,
                             100, 1320, width=530, height=280)

        # Row 1, Column 2: System of Record
        sor_items = integration_spec.get('system_of_record') or []
        if sor_items:
            self.add_info_box(root, "SYSTEM OF RECORD",
                             sor_items,
                             673, 1320, width=530, height=280)

        # Row 1, Column 3: Key Attributes
        key_items = integration_spec.get('key_attributes') or []
        if key_items:
            self.add_info_box(root, "KEY ATTRIBUTES SYNCHRONIZED",
                             key_items,
                             1246, 1320, width=530, height=280)

        # Row 2, Column 1: Notes & Assumptions
        notes_items = integration_spec.get('notes') or []
        if notes_items:
            self.add_info_box(root, "NOTES & ASSUMPTIONS",
                             notes_items,
                             100, 1650, width=530, height=280)

        # Row 2, Column 2: Environment Strategy
        env_items = integration_spec.get('environment_notes') or []
        if env_items:
            self.add_info_box(root, "ENVIRONMENT STRATEGY",
                             env_items,
                             673, 1650, width=530, height=280)

        # Row 2, Column 3: Critical Constraints
        constraint_items = integration_spec.get('critical_constraints') or []
        if constraint_items:
            self.add_info_box(root, "CRITICAL CONSTRAINTS",
                             constraint_items,
                             1246, 1650, width=530, height=280)

        # Convert to string
        return ET.tostring(root, encoding='unicode')
