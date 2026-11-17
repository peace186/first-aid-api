from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "First Aid API is running!"

@app.route('/api/guides', methods=['GET'])
def get_guides():
    # This is the master list of guides your Kivy app will sync with
    guides = [
        {
            "id": 1,
            "category_id": 1,
            "title": "Minor Thermal Burns",
            "symptoms": "Red skin, pain, mild swelling",
            "steps": "1. Cool the burn under cool running water for 10-20 minutes.\n2. Remove any tight jewelry or rings before swelling starts.\n3. Cover loosely with a clean, non-fluffy bandage or cloth.",
            "version": 2
        },
        {
            "id": 2,
            "category_id": 2,
            "title": "Severe Bleeding",
            "symptoms": "Blood spurting or flowing continuously",
            "steps": "1. Apply direct, firm pressure on the wound using a clean cloth.\n2. Elevate the injured area above the heart.\n3. Keep applying pressure and seek emergency help immediately.",
            "version": 1
        },
        {
            "id": 3,
            "category_id": 3,
            "title": "Adult CPR",
            "symptoms": "Unresponsive, not breathing normally",
            "steps": "1. Call for emergency help and get an AED if available.\n2. Place hands in the center of the chest and push hard and fast (100-120 beats/min).\n3. Allow the chest to recoil completely between compressions.",
            "version": 1
        }
        ,
        {
            "id": 4,
            "category_id": 4,
            "title": "snake Bite",
            "symptoms": "fang marks, severe pain, swelling, redness, numbness, or dizziness.",
            "steps": "1. keep the victim calm and still to slow the spread of venom.\n2. position the affected area below heart level.\n3. wash the bite gently with soap and water.\n4. Apply a clean, dry bandage over the site.\n5. DO NOT cut the wound, attempt to suck out the venom, or apply a tournniquet.\n6. Seek emergency medical help immediately.",
            "version": 1
            
        }
    ]
    return jsonify(guides)

if __name__ == '__main__':
    app.run(debug=True)