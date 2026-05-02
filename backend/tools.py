# We use this global variable to track if the AI unlocked a step in the current turn.
latest_unlocked_step = None

def get_voter_id_rules(state: str) -> str:
    """Gets the voter ID rules for a given Indian state/UT."""
    return f"In {state}, as per the Election Commission of India, you primarily need your Voter ID (EPIC). Alternatively, you can use Aadhaar Card, PAN Card, Driving License, Indian Passport, or MGNREGA Job Card at the polling booth."

def get_election_timeline(state: str) -> dict:
    """Gets the election timeline for a given Indian state/UT."""
    return {
        "registration_deadline": "Approx 3 weeks before polling (Check voters.eci.gov.in)",
        "polling_day": "Upcoming Phase (Check local ECI schedule)",
        "result_day": "National Counting Day"
    }

def update_progress(step: str) -> str:
    """Unlocks a new step in the skill tree. Valid steps are ONLY: 'Registered', 'ID Ready', 'Polling Booth Found', 'Ballot Submitted', 'Democracy Hero'."""
    global latest_unlocked_step
    latest_unlocked_step = step
    return f"Step '{step}' unlocked successfully!"

def solve_user_issue(issue: str) -> str:
    """Provides a solution to a common voter issue like 'lost ID', 'absentee', 'moving' in India."""
    return f"For '{issue}': You can apply for a duplicate EPIC card online via the Voter Helpline App or the NVSP portal (voters.eci.gov.in). For change of address, fill Form 8."
