STATES_DATA = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Krishna", "Nellore", "Tirupati"],
    "Arunachal Pradesh": ["Tawang", "Itanagar", "Ziro"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
    "Florida": ["Miami", "Orlando", "Tampa"], # Just in case kept for legacy
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala"],
    "India": ["General District"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Chandigarh"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri"]
}

def get_all_states():
    states = list(STATES_DATA.keys())
    states.sort()
    return states

def get_districts_by_state(state: str):
    return STATES_DATA.get(state, ["General District"])

def get_mock_polling_booth(district: str, taluk: str, pincode: str):
    return [
        {
            "name": f"Government Public School, {district}",
            "address": f"Ward 4, {taluk if taluk else 'Central Area'}, {district}, PIN - {pincode if pincode else 'XXXXXX'}",
            "timings": "7:00 AM to 6:00 PM",
            "distance": "1.2 km",
            "map_link": f"https://maps.google.com/?q=Polling+Booth+{district}"
        },
        {
            "name": f"Community Center, {district}",
            "address": f"Sector 12, Near Bus Stand, {district}, PIN - {pincode if pincode else 'XXXXXX'}",
            "timings": "7:00 AM to 6:00 PM",
            "distance": "2.5 km",
            "map_link": f"https://maps.google.com/?q=Community+Center+{district}"
        }
    ]

def get_mock_candidates(district: str):
    return [
        {
            "name": "Rajesh Kumar",
            "party": "National Democratic Party (NDP)",
            "age": 45,
            "education": "Post Graduate",
            "profession": "Social Worker",
            "cases": 0,
            "assets": "2.5 Crores",
            "previous_history": "Incumbent MLA (2019-2024)",
            "summary": "Focus on infrastructure and youth employment."
        },
        {
            "name": "Sunita Sharma",
            "party": "United Progressive Front (UPF)",
            "age": 38,
            "education": "Ph.D. in Economics",
            "profession": "Professor",
            "cases": 1,
            "assets": "1.2 Crores",
            "previous_history": "First-time candidate",
            "summary": "Improving public education and women's safety."
        },
        {
            "name": "Arun Patel",
            "party": "Independent",
            "age": 52,
            "education": "Graduate",
            "profession": "Businessman",
            "cases": 0,
            "assets": "15 Crores",
            "previous_history": "Former City Mayor",
            "summary": "Promoting local businesses and transparent governance."
        }
    ]
