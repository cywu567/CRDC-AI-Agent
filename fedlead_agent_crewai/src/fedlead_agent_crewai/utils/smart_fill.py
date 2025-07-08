#from fedlead_agent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
#from faker import Faker
#import re
#import json

#def normalize(text):
#    return re.sub(r'[^a-z0-9]', '', text.lower())

#def get_dropdown_options(page, label):
#    try:
#        dropdown_el = page.query_selector(f"label:has-text('{label}') + * [role='button']")
#        if dropdown_el:
#            dropdown_el.click()
#            page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)
#            page.wait_for_timeout(300)  # Let animations settle
#            options = page.query_selector_all("[role='presentation'] [role='option']")
#            texts = [opt.inner_text().strip() for opt in options]
#            page.keyboard.press("Escape")  # Close dropdown safely
#            page.wait_for_timeout(200)
#            return texts
#    except Exception as e:
#        print(f"[get_dropdown_options] Failed for label '{label}': {e}")
#    return []



#def handle_dropdown(page, el, label_text, chosen):
#    try:
#        el.click()
#        page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)
#        options = page.query_selector_all("[role='presentation'] [role='option']")
#        options = [opt for opt in options if opt.is_visible()]

#        for opt in options:
#            text = opt.inner_text().strip()
#            if normalize(chosen) in normalize(text):
#                print(f"[handle_dropdown] Clicking option: {text}")
#                page.evaluate("""
#                    el => {
#                        const backdrop = document.querySelector('.MuiBackdrop-root');
#                        if (backdrop && backdrop.parentNode) {
#                            backdrop.parentNode.removeChild(backdrop);
#                        }
#                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
#                        el.click();
#                    }
#                """, opt)
#                page.wait_for_timeout(1000)
#                return True

#        print(f"[handle_dropdown] No matching option for '{chosen}' in {label_text}")
#    except Exception as e:
#        print(f"[handle_dropdown] Error handling dropdown '{label_text}': {e}")
#    return False

#def smart_fill(page, goal: str = "Fill out the form as reasonably as possible"):
#    fake = Faker()
#    decision_tool = BedrockDecisionTool()

#    page.wait_for_timeout(1000)
#    form = page.query_selector_all("form")[0]

#    def scrape_elements():
#        elements = form.query_selector_all("input, textarea, select, div[role='button']")
#        field_info = []
#        field_map = {}

#        for el in elements:
#            if not el.is_visible():
#                continue
#            if el.get_attribute("aria-hidden") == "true":
#                continue
#            if el.get_attribute("tabindex") == "-1":
#                continue

#            el_id = el.get_attribute("id")
#            el_name = el.get_attribute("name")
#            el_placeholder = el.get_attribute("placeholder")
#            el_type = el.get_attribute("type")
#            el_tag = el.evaluate("el => el.tagName").lower()
#            el_role = el.get_attribute("role")
#            is_dropdown = el_tag == "div" and el_role == "button" and el.get_attribute("aria-haspopup") == "listbox"

#            label_text = ""
#            if el_id:
#                label_el = form.query_selector(f"label[for='{el_id}']")
#                if label_el:
#                    label_text = label_el.inner_text().strip()

#            if not label_text:
#                if el_name:
#                    label_text = el_name
#                elif el_placeholder:
#                    label_text = el_placeholder
#                elif el_id and not el_id.startswith(":r"):
#                    label_text = el_id
#                else:
#                    continue

#            field_info.append({
#                "label": label_text,
#                "name": el_name,
#                "placeholder": el_placeholder,
#                "type": el_type,
#                "tag": el_tag,
#                "kind": "select" if is_dropdown else "input"
#            })

#            norm_label = normalize(label_text)
#            norm_name = normalize(el_name) if el_name else None
#            entry = (el, "select" if is_dropdown else "input")

#            if norm_label:
#                field_map.setdefault(norm_label, []).append(entry)
#            if norm_name:
#                field_map.setdefault(norm_name, []).append(entry)

#        return field_info, field_map

#    field_info, field_map = scrape_elements()

#    if not field_info:
#        return "No usable fields found."

#    field_descriptions = "\n".join([
#        f"- Label: {f['label']}\n  Tag: {f['tag']}\n  Name: {f['name']}\n  Options: {get_dropdown_options(page, f['label']) if f['kind'] == 'select' else 'N/A'}"
#        for f in field_info
#    ])

#    prompt = f"""
#    You are filling out a web form with the goal: "{goal}".

#    Here are the fields and their details:
#    {field_descriptions}

#    If a field has options, choose one that makes sense. 
#    Return only a valid JSON object where each key is the name of the field, and the value is the chosen or generated input.
#    """

#    response = decision_tool._run(
#        goal=goal,
#        options=[f"{f['label']} ({f['tag']})" for f in field_info],
#        custom_prompt=prompt,
#        max_tokens=300
#    )

#    try:
#        json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
#        answers = json.loads(json_str)
#    except Exception:
#        return f"Failed to parse AI response:\n{response}"

#    filled = 0
#    # Pass 1: Fill dropdowns
#    for label, value in answers.items():
#        norm_key = normalize(label)
#        if norm_key in field_map:
#            for el, kind in field_map[norm_key]:
#                if kind == "select":
#                    if isinstance(value, dict):
#                        value = value.get("name") or next(iter(value.values()), None)
#                    if handle_dropdown(page, el, label, value):
#                        filled += 1
#                        break

#    # Re-scrape inputs after dropdown changes
#    page.wait_for_timeout(1000)
#    field_info, field_map = scrape_elements()

#    # Pass 2: Fill text fields
#    for label, value in answers.items():
#        norm_key = normalize(label)
#        if norm_key in field_map:
#            for el, kind in field_map[norm_key]:
#                if kind == "input":
#                    try:
#                        el.fill(str(value))
#                        filled += 1
#                        break
#                    except Exception as e:
#                        print(f"[smart_fill] Could not fill '{label}': {e}")
#        else:
#            print(f"[smart_fill] No matching element for '{label}'")

#    return f"Filled {filled} fields based on AI reasoning."
