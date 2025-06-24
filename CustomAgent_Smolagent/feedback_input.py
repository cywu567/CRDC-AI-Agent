
"""feedback_input.py

Utility functions to collect user inputs for the feedback loop.
Separate from logging (handled by LogFeedbackTool).
"""
def ask_user_feedback(step_number: int, step_description: str) -> tuple[bool, str]:
    """
    Prompt the user for yes/no acceptance and optional comments for a given step.
    Returns a tuple: (is_accepted, comments)
    """
    print(f"\nStep {step_number}: {step_description}")
    while True:
        response = input("Was this step successful? (yes/no): ").strip().lower()
        if response in {"yes", "no"}:
            break
        print("Please type 'yes' or 'no'.")
    is_accepted = response == "yes"
    comments = input("Any comments? (or press Enter to skip): ").strip()
    return is_accepted, comments
