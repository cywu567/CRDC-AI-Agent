from fedlead_agent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool

decision_tool = BedrockDecisionTool()

def smart_click(page, goal: str, filter_by_tag: str = None):
    print(f"[smart_click] Goal: {goal}")

    # Only consider <button> and <a> elements
    elements = []
    if filter_by_tag:
        selectors = [filter_by_tag]
    else:
        selectors = ["button", "a", "input[type='submit']", "input[type='button']", "div[role='button']"]
    for selector in selectors:
        elements += page.query_selector_all(selector)

    # Filter for visibility
    visible_elements = [el for el in elements if el.is_visible()]

    options = []
    element_map = {}

    for el in visible_elements:
        try:
            text = el.inner_text().strip()
            if not text:
                text = el.get_attribute("value") or el.text_content() or ""
            text = text.strip()
            if text:
                options.append(text)
                element_map[text.lower()] = el
        except Exception as e:
            continue

    if not options:
        raise Exception("No visible <button> or <a> elements with text found.")

    print("[smart_click] Visible options:", options)

    try:
        # Run Claude decision
        chosen = decision_tool._run(goal=goal, options=options).lower().strip('"').strip()
        print(f"[smart_click] LLM chose: {chosen}")

        for text, el in element_map.items():
            text_norm = text.lower().strip()
            if chosen in text_norm or text_norm in chosen:
                print(f"[smart_click] Clicking element with text: '{text}'")
                el.click()
                return text

        raise Exception(f"No matching element found for LLM choice: '{chosen}'")
    
    except Exception as e:
        raise Exception(f"[smart_click] Failed to click: {e}")
