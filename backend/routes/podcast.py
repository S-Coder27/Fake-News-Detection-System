from config.db import db

podcast_collection = db["podcast_checks"]

@podcast_bp.route('/analyze', methods=['POST'])
def analyze_podcast():

    transcript = "ISRO launched a satellite"

    claims = [
        {
            "claim": "ISRO launched a satellite",
            "status": "Verified",
            "confidence": 92
        }
    ]

    credibility = 92

    podcast_collection.insert_one({
        "transcript": transcript,
        "claims": claims,
        "credibility": credibility
    })

    return {"message": "Saved"}