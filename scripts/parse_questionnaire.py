import os
import re
from bs4 import BeautifulSoup

HTML_FILE = r'g:\field-assist-bot\docs\knowledge_base\ICM_follow_up_launch_integrated_printable.html'
OUTPUT_FILE = r'g:\field-assist-bot\docs\knowledge_base\questionnaire_knowledge.md'

def clean_text(text):
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_html_to_md():
    if not os.path.exists(HTML_FILE):
        print(f"File not found: {HTML_FILE}")
        return

    print(f"Reading HTML file: {HTML_FILE}")
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    print(f"Writing markdown to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# ICM Household Survey Knowledge Base\n\n")
        f.write("This document is automatically generated from the questionnaire HTML export.\n\n")
        
        # Locate the main table
        main_table = soup.find('table', class_='table-condensed')
        
        if not main_table:
            tables = soup.find_all('table')
            if tables:
                main_table = max(tables, key=lambda t: len(t.find_all('tr')))
            
        if not main_table:
            print("Could not find main table.")
            return

        print("Found main table.")

        rows = []
        thead = main_table.find('thead')
        if thead:
            rows.extend(thead.find_all('tr', recursive=False))
        
        tbody = main_table.find('tbody')
        if tbody:
            rows.extend(tbody.find_all('tr', recursive=False))
            
        if not rows:
            rows = main_table.find_all('tr', recursive=False)

        print(f"Processing {len(rows)} rows.")
        
        for i, row in enumerate(rows):
            if i % 100 == 0:
                print(f"Processed {i} rows...")
            
            cells = row.find_all(['td', 'th'], recursive=False)
            
            if not cells:
                continue

            # Header Rows (colspan=3)
            is_header = False
            if len(cells) == 1:
                colspan = cells[0].get('colspan')
                if colspan == '3':
                    is_header = True
            
            if is_header:
                text = clean_text(cells[0].get_text())
                if not text:
                    continue
                if '>' in text:
                    parts = text.split('>')
                    header_text = parts[-1].strip()
                    f.write(f"## {header_text}\n\n")
                else:
                    f.write(f"## {text}\n\n")
                continue

            # Question Rows
            if len(cells) == 3:
                field_cell = cells[0]
                question_cell = cells[1]
                answer_cell = cells[2]
                
                field_text_all = clean_text(field_cell.get_text())
                field_name = field_text_all.replace('(required)', '').strip()
                
                field_name_lower = field_name.lower()
                q_cell_text_lower = clean_text(question_cell.get_text()).lower()

                if 'field' in field_name_lower and 'question' in q_cell_text_lower:
                    continue
                
                relevance = ""
                constraint = ""
                q_components = []
                
                for element in question_cell.children:
                    if element.name == 'p':
                        p_classes = element.get('class', [])
                        p_text = clean_text(element.get_text())
                        if 'relevance' in p_classes:
                            relevance = p_text.replace("Question relevant when:", "").strip()
                        elif 'constraint' in p_classes:
                            constraint = p_text.replace("Response constrained to:", "").strip()
                        elif 'hint' in p_classes:
                             q_components.append(f"_{p_text}_")
                        else:
                            q_components.append(p_text)
                    elif element.name is None:
                        text = clean_text(element)
                        if text: 
                            q_components.append(text)
                    elif element.name in ['b', 'strong']:
                        q_components.append(f"**{clean_text(element.get_text())}**")
                    elif element.name in ['i', 'em']:
                        q_components.append(f"*{clean_text(element.get_text())}*")
                    elif element.name == 'font':
                        q_components.append(clean_text(element.get_text()))
                    elif element.name == 'br':
                        q_components.append("__BR__")
                    else: 
                         q_components.append(clean_text(element.get_text()))
                
                q_text = " ".join(q_components).strip()
                q_text = re.sub(r'\s+', ' ', q_text).strip()
                q_text = q_text.replace('__BR__', '\n\n')

                answers = []
                # Check for nested table in answer_cell
                # Usually answer_cell has children. If Table is one, use it.
                nested_table = answer_cell.find('table')
                if nested_table:
                    n_rows = nested_table.find_all('tr')
                    for n_row in n_rows:
                        n_cells = n_row.find_all('td')
                        cell_texts = [clean_text(c.get_text()) for c in n_cells]
                        cell_texts = [c for c in cell_texts if c]
                        
                        if len(cell_texts) >= 2:
                            # Heuristic: Value is likely short, Label is longer
                            # In HTML: Value is usually first non-empty
                            val = cell_texts[0]
                            label = cell_texts[1]
                            answers.append(f"- **{val}**: {label}")
                        elif len(cell_texts) == 1:
                            answers.append(f"- {cell_texts[0]}")
                else:
                     ans_text = clean_text(answer_cell.get_text())
                     if ans_text:
                         answers.append(f"- {ans_text}")
                
                f.write(f"### Variable: `{field_name}`\n")
                f.write(f"**Question:** {q_text}\n")
                
                if answers:
                    f.write("\n**Options:**\n")
                    for ans in answers:
                        f.write(f"{ans}\n")
                else:
                    f.write("\n**Type:** Free Text / Input\n")

                if relevance:
                    f.write(f"\n> **Logic:** Show if `{relevance}`\n")
                
                if constraint:
                     f.write(f"\n> **Validation:** `{constraint}`\n")
                
                f.write("\n---\n\n")

    print("Done.")

if __name__ == "__main__":
    parse_html_to_md()
