# main.py - Enhanced Carbon Footprint Tracker
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import spacy
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os

# Initialize FastAPI app
app = FastAPI(title="Enhanced Voice Carbon Footprint Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
whisper_model = None
nlp_model = None

@app.on_event("startup")
async def startup_event():
    global whisper_model, nlp_model
    try:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
        
        print("Loading spaCy model...")
        nlp_model = spacy.load("en_core_web_sm")
        print("spaCy model loaded successfully!")
    except Exception as e:
        print(f"Error loading models: {e}")

# Enhanced Carbon Footprint Calculation - Expanded Dataset
EMISSION_FACTORS = {
    # Transportation (kg CO2e per km)
    "car_gasoline": 0.21,
    "car_diesel": 0.17,
    "car_electric": 0.05,
    "car_hybrid": 0.12,
    "motorcycle": 0.14,
    "bus": 0.089,
    "train": 0.041,
    "metro": 0.035,
    "tram": 0.030,
    "plane_domestic": 0.255,
    "plane_international": 0.195,
    "taxi": 0.23,
    "uber": 0.23,
    "ferry": 0.115,
    "walk": 0.0,
    "bike": 0.0,
    "scooter": 0.0,
    
    # Food (kg CO2e per kg or serving)
    "beef": 27.0,
    "lamb": 24.5,
    "pork": 7.6,
    "chicken": 5.7,
    "turkey": 6.1,
    "fish": 3.1,
    "seafood": 4.2,
    "cheese": 13.5,
    "milk": 1.9,
    "eggs": 4.2,
    "rice": 2.7,
    "pasta": 1.1,
    "bread": 1.4,
    "vegetables": 0.4,
    "fruits": 0.3,
    "nuts": 0.3,
    "beans": 0.4,
    "tofu": 2.0,
    "pizza": 3.2,
    "burger": 5.5,
    "sandwich": 2.1,
    "salad": 0.5,
    "coffee": 0.28,
    "tea": 0.05,
    "soda": 0.33,
    "beer": 0.74,
    "wine": 1.28,
    
    # Energy & Utilities (kg CO2e per unit)
    "electricity": 0.233,  # per kWh
    "gas_heating": 0.185,  # per kWh
    "water_heating": 0.15,  # per minute
    "shower": 0.7,  # per minute
    "bath": 2.5,  # per bath
    "washing_machine": 0.6,  # per load
    "dryer": 2.4,  # per load
    "dishwasher": 0.8,  # per load
    "air_conditioning": 0.5,  # per hour
    "heating": 0.3,  # per hour
    "tv": 0.097,  # per hour
    "computer": 0.15,  # per hour
    "phone_charging": 0.008,  # per charge
    
    # Waste & Recycling (kg CO2e per kg)
    "landfill_waste": 0.57,
    "recycling": 0.02,
    "composting": -0.05,  # negative because it sequesters carbon
    "plastic_bottle": 0.082,
    "glass_bottle": 0.51,
    "aluminum_can": 0.33,
    "paper": 0.017,
    
    # Shopping & Consumption (kg CO2e per item/kg)
    "clothing_cotton": 8.0,
    "clothing_polyester": 5.9,
    "clothing_wool": 17.0,
    "shoes": 12.5,
    "electronics": 300.0,  # average smartphone
    "books": 1.0,
    "furniture": 25.0,  # average chair
    "cosmetics": 3.0,
    "cleaning_products": 2.0,
    
    # Services & Activities (kg CO2e per activity)
    "hotel_night": 10.9,
    "restaurant_meal": 2.8,
    "movie_theater": 1.4,
    "gym_session": 0.8,
    "haircut": 0.5,
    "online_shopping": 0.5,  # per order
    "streaming_hour": 0.036,  # per hour
    "email": 0.000004,  # per email
    "google_search": 0.0002,  # per search
}

# Enhanced activity keywords with more comprehensive coverage
ACTIVITY_KEYWORDS = {
    # Transportation
    "drive": ["drive", "drove", "driving", "car", "commute", "road trip", "vehicle", "auto", "automotive"],
    "fly": ["fly", "flew", "flight", "plane", "aircraft", "airport", "aviation", "jet"],
    "train": ["train", "railway", "railroad", "metro", "subway", "rail"],
    "bus": ["bus", "public transport", "transit", "coach"],
    "walk": ["walk", "walked", "walking", "stroll", "hike", "hiking"],
    "bike": ["bike", "bicycle", "cycling", "cycle", "biked"],
    "taxi": ["taxi", "cab", "uber", "lyft", "ride share"],
    "motorcycle": ["motorcycle", "motorbike", "scooter", "moped"],
    "ferry": ["ferry", "boat", "ship", "cruise"],
    
    # Food & Dining
    "cook": ["cook", "cooked", "cooking", "prepare", "prepared", "meal", "breakfast", "lunch", "dinner"],
    "eat": ["ate", "eating", "consumed", "had", "ordered", "dined"],
    "restaurant": ["restaurant", "cafe", "diner", "takeout", "delivery", "fast food"],
    "drink": ["drink", "drank", "beverage", "coffee", "tea", "beer", "wine", "soda"],
    
    # Energy & Utilities
    "shower": ["shower", "showered", "bath", "bathing", "bathe"],
    "laundry": ["laundry", "wash", "washing", "clothes", "detergent", "dryer"],
    "heating": ["heating", "heat", "warm", "furnace", "boiler"],
    "cooling": ["air conditioning", "ac", "cool", "cooling", "fan"],
    "electricity": ["electricity", "power", "lights", "appliances", "device"],
    
    # Shopping & Consumption
    "shopping": ["shopping", "bought", "purchased", "store", "mall", "retail", "online shopping"],
    "clothes": ["clothes", "clothing", "shirt", "pants", "dress", "shoes", "fashion"],
    "electronics": ["phone", "computer", "laptop", "tv", "electronics", "gadget"],
    
    # Waste
    "waste": ["trash", "garbage", "waste", "throw away", "dispose"],
    "recycle": ["recycle", "recycling", "recycled", "reuse"],
    "compost": ["compost", "composting", "organic waste"],
    
    # Services
    "hotel": ["hotel", "motel", "accommodation", "stay", "lodging"],
    "entertainment": ["movie", "theater", "cinema", "concert", "show", "streaming"],
    "gym": ["gym", "workout", "exercise", "fitness", "sports"],
}

# Food-specific keywords for better detection
FOOD_KEYWORDS = {
    "beef": ["beef", "steak", "burger", "hamburger", "cow", "cattle"],
    "chicken": ["chicken", "poultry", "wings", "breast", "thigh"],
    "pork": ["pork", "bacon", "ham", "sausage", "pig"],
    "fish": ["fish", "salmon", "tuna", "cod", "seafood"],
    "cheese": ["cheese", "cheddar", "mozzarella", "dairy"],
    "vegetables": ["vegetables", "veggie", "salad", "broccoli", "carrot", "tomato"],
    "pizza": ["pizza", "slice", "pie"],
    "pasta": ["pasta", "spaghetti", "noodles", "macaroni"],
    "rice": ["rice", "grain", "pilaf"],
    "bread": ["bread", "sandwich", "toast", "bun"],
}

def extract_numbers_and_units(text):
    """Enhanced number and unit extraction with better patterns"""
    result = {}
    text_lower = text.lower()
    
    # Distance patterns (enhanced)
    distance_patterns = [
        r"(\d+(?:\.\d+)?)\s?(km|kilometers|miles|mi|m|meters|blocks)",
        r"(\d+(?:\.\d+)?)\s?(?:km|kilometers|miles|mi|m|meters|blocks)",
        r"about\s+(\d+(?:\.\d+)?)\s?(km|kilometers|miles|mi|m|meters)",
        r"approximately\s+(\d+(?:\.\d+)?)\s?(km|kilometers|miles|mi|m|meters)",
    ]
    
    for pattern in distance_patterns:
        distance_match = re.search(pattern, text_lower)
        if distance_match:
            value = float(distance_match.group(1))
            unit = distance_match.group(2) if len(distance_match.groups()) > 1 else "km"
            
            # Convert to km
            if unit in ["miles", "mi"]:
                value *= 1.609
            elif unit in ["m", "meters"]:
                value *= 0.001
            elif unit in ["blocks"]:
                value *= 0.08  # Average city block
            
            result["distance"] = value
            break
    
    # Time patterns (enhanced)
    time_patterns = [
        r"(\d+(?:\.\d+)?)\s?(hours|hour|hrs|hr|h|minutes|mins|min|seconds|secs|sec)",
        r"for\s+(\d+(?:\.\d+)?)\s?(hours|hour|hrs|hr|h|minutes|mins|min)",
        r"(\d+(?:\.\d+)?)\s?(?:hours|hour|hrs|hr|h|minutes|mins|min)",
    ]
    
    for pattern in time_patterns:
        time_match = re.search(pattern, text_lower)
        if time_match:
            value = float(time_match.group(1))
            unit = time_match.group(2) if len(time_match.groups()) > 1 else "min"
            
            # Convert to minutes
            if unit in ["hours", "hour", "hrs", "hr", "h"]:
                value *= 60
            elif unit in ["seconds", "secs", "sec"]:
                value /= 60
            
            result["duration"] = value
            break
    
    # Quantity patterns (enhanced)
    quantity_patterns = [
        r"(\d+(?:\.\d+)?)\s?(times|loads|meals|servings|cups|pieces|items|bottles|cans|kg|pounds|lbs|g|grams)",
        r"(\d+(?:\.\d+)?)\s?(?:times|loads|meals|servings|cups|pieces|items|bottles|cans|kg|pounds|lbs|g|grams)",
        r"ate\s+(\d+(?:\.\d+)?)",
        r"had\s+(\d+(?:\.\d+)?)",
        r"bought\s+(\d+(?:\.\d+)?)",
    ]
    
    for pattern in quantity_patterns:
        quantity_match = re.search(pattern, text_lower)
        if quantity_match:
            value = float(quantity_match.group(1))
            unit = quantity_match.group(2) if len(quantity_match.groups()) > 1 else "items"
            
            # Convert to standard units
            if unit in ["pounds", "lbs"]:
                value *= 0.453592  # Convert to kg
            elif unit in ["g", "grams"]:
                value *= 0.001  # Convert to kg
            
            result["quantity"] = value
            result["unit"] = unit
            break
    
    # Extract numbers without units (context-dependent)
    if not result:
        number_match = re.search(r"(\d+(?:\.\d+)?)", text_lower)
        if number_match:
            result["raw_number"] = float(number_match.group(1))
    
    return result

def detect_food_type(sentence):
    """Enhanced food type detection"""
    sentence_lower = sentence.lower()
    
    # Check for specific food keywords
    for food_type, keywords in FOOD_KEYWORDS.items():
        if any(keyword in sentence_lower for keyword in keywords):
            return food_type
    
    # Check for cooking methods that might indicate food type
    if any(word in sentence_lower for word in ["grilled", "roasted", "bbq", "barbecue"]):
        if any(word in sentence_lower for word in ["meat", "steak", "chicken"]):
            return "beef" if "steak" in sentence_lower else "chicken"
    
    # Default based on common patterns
    if any(word in sentence_lower for word in ["meal", "dinner", "lunch"]):
        return "general_meal"
    
    return "general"

def get_smart_defaults(activity_type, sentence):
    """Enhanced intelligent defaults with better context understanding"""
    defaults = {}
    sentence_lower = sentence.lower()
    
    if activity_type == "drive":
        # Context-based distance estimation
        if any(word in sentence_lower for word in ["work", "office", "job"]):
            defaults["distance"] = 15
        elif any(word in sentence_lower for word in ["store", "shop", "mall", "grocery"]):
            defaults["distance"] = 5
        elif any(word in sentence_lower for word in ["airport", "station"]):
            defaults["distance"] = 25
        elif any(word in sentence_lower for word in ["downtown", "city", "center"]):
            defaults["distance"] = 12
        elif any(word in sentence_lower for word in ["friend", "visit", "party"]):
            defaults["distance"] = 8
        else:
            defaults["distance"] = 10
        
        # Handle round trip
        if any(phrase in sentence_lower for phrase in ["round trip", "there and back", "return"]):
            defaults["distance"] = defaults.get("distance", 10) * 2
    
    elif activity_type in ["cook", "eat"]:
        defaults["quantity"] = 1
        defaults["food_type"] = detect_food_type(sentence)
        
        # Adjust quantity based on context
        if any(word in sentence_lower for word in ["family", "everyone", "group"]):
            defaults["quantity"] = 4
        elif any(word in sentence_lower for word in ["couple", "two", "both"]):
            defaults["quantity"] = 2
    
    elif activity_type == "shower":
        if any(word in sentence_lower for word in ["quick", "fast", "short"]):
            defaults["duration"] = 5
        elif any(word in sentence_lower for word in ["long", "relaxing", "hot"]):
            defaults["duration"] = 15
        else:
            defaults["duration"] = 10
    
    elif activity_type == "laundry":
        defaults["quantity"] = 1
        if any(word in sentence_lower for word in ["loads", "multiple", "several"]):
            defaults["quantity"] = 2
    
    elif activity_type == "fly":
        if any(word in sentence_lower for word in ["international", "overseas", "abroad"]):
            defaults["distance"] = 2000
        elif any(word in sentence_lower for word in ["domestic", "within", "local"]):
            defaults["distance"] = 500
        else:
            defaults["distance"] = 1000
    
    elif activity_type in ["shopping", "clothes"]:
        defaults["quantity"] = 1
        if any(word in sentence_lower for word in ["spree", "lots", "many", "several"]):
            defaults["quantity"] = 3
    
    elif activity_type == "electricity":
        defaults["duration"] = 1  # 1 hour default
        if any(word in sentence_lower for word in ["all day", "whole day"]):
            defaults["duration"] = 8
        elif any(word in sentence_lower for word in ["night", "evening"]):
            defaults["duration"] = 4
    
    return defaults

def extract_activities(text, nlp=None):
    """Enhanced activity extraction with improved NLP"""
    if nlp:
        doc = nlp(text.lower())
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        # Enhanced sentence splitting
        sentences = re.split(r'[.!?;]\s+', text.lower())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Additional splitting for comma-separated activities
        expanded_sentences = []
        for sent in sentences:
            if ', and ' in sent or ', then ' in sent:
                parts = re.split(r',\s*(?:and|then)\s*', sent)
                expanded_sentences.extend(parts)
            else:
                expanded_sentences.append(sent)
        sentences = expanded_sentences
    
    activities = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if not sentence_lower:
            continue
        
        # Check each activity type with priority system
        activity_found = False
        
        # Priority 1: Specific activities (transportation, food, etc.)
        for activity_type, keywords in ACTIVITY_KEYWORDS.items():
            if any(keyword in sentence_lower for keyword in keywords):
                activity = {
                    "type": activity_type,
                    "sentence": sentence,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": "high" if len([k for k in keywords if k in sentence_lower]) > 1 else "medium"
                }
                
                # Extract numbers and units
                numbers = extract_numbers_and_units(sentence)
                if numbers:
                    activity.update(numbers)
                
                # Apply intelligent defaults
                defaults = get_smart_defaults(activity_type, sentence_lower)
                for key, value in defaults.items():
                    if key not in activity:
                        activity[key] = value
                
                activities.append(activity)
                activity_found = True
                break
        
        # Priority 2: General consumption patterns
        if not activity_found:
            # Check for general consumption keywords
            consumption_keywords = ["used", "consumed", "spent", "wasted", "generated"]
            if any(keyword in sentence_lower for keyword in consumption_keywords):
                activity = {
                    "type": "general_consumption",
                    "sentence": sentence,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": "low"
                }
                
                numbers = extract_numbers_and_units(sentence)
                if numbers:
                    activity.update(numbers)
                
                activities.append(activity)
    
    return activities

def calculate_single_emission(activity):
    """Enhanced emission calculation with expanded logic"""
    activity_type = activity["type"]
    
    # Transportation emissions
    if activity_type == "drive":
        distance = activity.get("distance", 10)
        vehicle_type = activity.get("vehicle_type", "car_gasoline")
        return EMISSION_FACTORS.get(vehicle_type, EMISSION_FACTORS["car_gasoline"]) * distance
    
    elif activity_type == "fly":
        distance = activity.get("distance", 1000)
        # Determine if domestic or international
        if distance > 1500:
            return EMISSION_FACTORS["plane_international"] * distance
        else:
            return EMISSION_FACTORS["plane_domestic"] * distance
    
    elif activity_type in ["train", "bus", "taxi", "motorcycle"]:
        distance = activity.get("distance", 20)
        emission_factor = EMISSION_FACTORS.get(activity_type, EMISSION_FACTORS["bus"])
        return emission_factor * distance
    
    # Food emissions
    elif activity_type in ["cook", "eat"]:
        quantity = activity.get("quantity", 1)
        food_type = activity.get("food_type", "general")
        
        if food_type in EMISSION_FACTORS:
            # Most food emissions are per kg, but we'll assume serving sizes
            serving_multiplier = 0.25  # Average serving size in kg
            return EMISSION_FACTORS[food_type] * quantity * serving_multiplier
        elif food_type == "general_meal":
            return 2.8 * quantity  # Average meal emission
        else:
            return EMISSION_FACTORS.get("cook", 0.5) * quantity
    
    elif activity_type == "restaurant":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["restaurant_meal"] * quantity
    
    # Energy & Utilities
    elif activity_type == "shower":
        duration = activity.get("duration", 10)
        return EMISSION_FACTORS["shower"] * duration
    
    elif activity_type == "laundry":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["washing_machine"] * quantity
    
    elif activity_type == "electricity":
        duration = activity.get("duration", 1)
        return EMISSION_FACTORS["electricity"] * duration
    
    elif activity_type in ["heating", "cooling"]:
        duration = activity.get("duration", 1)
        if activity_type == "heating":
            return EMISSION_FACTORS["heating"] * duration
        else:
            return EMISSION_FACTORS["air_conditioning"] * duration
    
    # Shopping & Consumption
    elif activity_type == "shopping":
        quantity = activity.get("quantity", 1)
        return 2.0 * quantity  # Average shopping emission
    
    elif activity_type == "clothes":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["clothing_cotton"] * quantity
    
    elif activity_type == "electronics":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["electronics"] * quantity
    
    # Waste
    elif activity_type == "waste":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["landfill_waste"] * quantity
    
    elif activity_type == "recycle":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["recycling"] * quantity
    
    # Services
    elif activity_type == "hotel":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["hotel_night"] * quantity
    
    elif activity_type == "entertainment":
        quantity = activity.get("quantity", 1)
        return EMISSION_FACTORS["movie_theater"] * quantity
    
    # Zero emission activities
    elif activity_type in ["walk", "bike"]:
        return 0.0
    
    # General consumption
    elif activity_type == "general_consumption":
        return 1.0  # Default general emission
    
    else:
        return 0.0

def get_calculation_details(activity, emission):
    """Enhanced calculation details with better explanations"""
    details = {
        "method": f"Used {activity['type']} emission factor",
        "assumptions": [],
        "confidence": activity.get("confidence", "medium"),
        "emission_factor": None,
        "calculation": None
    }
    
    # Add specific calculation details
    activity_type = activity["type"]
    
    if activity_type == "drive":
        factor = EMISSION_FACTORS["car_gasoline"]
        distance = activity.get("distance", 10)
        details["emission_factor"] = f"{factor} kg CO2e per km"
        details["calculation"] = f"{distance} km × {factor} kg CO2e/km = {emission:.2f} kg CO2e"
    
    elif activity_type in ["cook", "eat"]:
        food_type = activity.get("food_type", "general")
        quantity = activity.get("quantity", 1)
        if food_type in EMISSION_FACTORS:
            factor = EMISSION_FACTORS[food_type]
            details["emission_factor"] = f"{factor} kg CO2e per kg"
            details["calculation"] = f"{quantity} servings × {factor * 0.25:.2f} kg CO2e/serving = {emission:.2f} kg CO2e"
    
    # Add assumptions
    if activity.get("distance") and not re.search(r'\d+\s*(km|mile|meter)', activity.get("sentence", "")):
        details["assumptions"].append(f"Assumed distance: {activity['distance']} km")
    
    if activity.get("duration") and not re.search(r'\d+\s*(hour|minute|min)', activity.get("sentence", "")):
        details["assumptions"].append(f"Assumed duration: {activity['duration']} minutes")
    
    if activity.get("quantity") and not re.search(r'\d+', activity.get("sentence", "")):
        details["assumptions"].append(f"Assumed quantity: {activity['quantity']}")
    
    if activity.get("food_type") and activity["food_type"] != "general":
        details["assumptions"].append(f"Detected food type: {activity['food_type']}")
    
    return details

def calculate_emissions(activities):
    """Enhanced emissions calculation with categorization"""
    results = []
    totals = {
        "transportation": 0,
        "food": 0,
        "energy": 0,
        "consumption": 0,
        "waste": 0,
        "services": 0,
        "total": 0
    }
    
    # Category mapping
    category_map = {
        "drive": "transportation", "fly": "transportation", "train": "transportation",
        "bus": "transportation", "taxi": "transportation", "motorcycle": "transportation",
        "cook": "food", "eat": "food", "restaurant": "food",
        "shower": "energy", "laundry": "energy", "electricity": "energy",
        "heating": "energy", "cooling": "energy",
        "shopping": "consumption", "clothes": "consumption", "electronics": "consumption",
        "waste": "waste", "recycle": "waste",
        "hotel": "services", "entertainment": "services"
    }
    
    for activity in activities:
        emission = calculate_single_emission(activity)
        category = category_map.get(activity["type"], "consumption")
        
        totals[category] += emission
        totals["total"] += emission
        
        result = {
            "activity": activity["sentence"],
            "type": activity["type"],
            "category": category,
            "emission": round(emission, 3),
            "confidence": activity.get("confidence", "medium"),
            "details": get_calculation_details(activity, emission)
        }
        results.append(result)
    
    # Add category summaries
    for category, total in totals.items():
        if total > 0 and category != "total":
            results.append({
                "activity": f"{category.title()} Total",
                "emission": round(total, 3),
                "type": "category_summary",
                "category": category
            })
    
    # Add overall total
    results.append({
        "activity": "Total Carbon Footprint",
        "emission": round(totals["total"], 3),
        "type": "total_summary",
        "breakdown": {k: round(v, 3) for k, v in totals.items() if k != "total" and v > 0}
    })
    
    return results

# API endpoints (unchanged)
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Process uploaded audio file and return carbon footprint analysis"""
    try:
        if not whisper_model:
            raise HTTPException(status_code=500, detail="Whisper model not loaded")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Transcribe audio
            result = whisper_model.transcribe(tmp_file_path)
            transcription = result["text"]
            
            # Extract activities
            activities = extract_activities(transcription, nlp_model)
            
            # Calculate emissions
            emissions = calculate_emissions(activities)
            
            return {
                "transcription": transcription,
                "activities": activities,
                "emissions": emissions,
                "total_emission": emissions[-1]["emission"] if emissions else 0
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-text")
async def analyze_text(data: dict):
    """Analyze text input for carbon footprint"""
    try:
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Extract activities
        activities = extract_activities(text, nlp_model)
        
        # Calculate emissions
        emissions = calculate_emissions(activities)
        
        return {
            "text": text,
            "activities": activities,
            "emissions": emissions,
            "total_emission": emissions[-1]["emission"] if emissions else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "whisper_loaded": whisper_model is not None,
        "spacy_loaded": nlp_model is not None,
        "emission_factors_count": len(EMISSION_FACTORS),
        "activity_keywords_count": len(ACTIVITY_KEYWORDS)
    }

@app.get("/emission-factors")
async def get_emission_factors():
    """Get all available emission factors"""
    return {
        "emission_factors": EMISSION_FACTORS,
        "categories": {
            "transportation": [k for k in EMISSION_FACTORS.keys() if k.startswith(("car_", "plane_", "train", "bus", "taxi", "motorcycle", "ferry"))],
            "food": [k for k in EMISSION_FACTORS.keys() if k in ["beef", "chicken", "pork", "fish", "vegetables", "pizza", "pasta", "rice", "bread", "cheese", "milk", "eggs"]],
            "energy": [k for k in EMISSION_FACTORS.keys() if k in ["electricity", "gas_heating", "shower", "bath", "washing_machine", "dryer", "dishwasher", "air_conditioning", "heating"]],
            "consumption": [k for k in EMISSION_FACTORS.keys() if k.startswith(("clothing_", "electronics", "furniture", "cosmetics"))],
            "waste": [k for k in EMISSION_FACTORS.keys() if k in ["landfill_waste", "recycling", "composting", "plastic_bottle", "glass_bottle", "aluminum_can"]]
        }
    }

@app.post("/calculate-custom")
async def calculate_custom_emission(data: dict):
    """Calculate emissions for custom activities with specific parameters"""
    try:
        activity_type = data.get("activity_type")
        parameters = data.get("parameters", {})
        
        if not activity_type:
            raise HTTPException(status_code=400, detail="Activity type is required")
        
        # Create a custom activity object
        custom_activity = {
            "type": activity_type,
            "sentence": f"Custom {activity_type} activity",
            "timestamp": datetime.now().isoformat(),
            "confidence": "high",
            **parameters
        }
        
        # Calculate emission
        emission = calculate_single_emission(custom_activity)
        details = get_calculation_details(custom_activity, emission)
        
        return {
            "activity": custom_activity,
            "emission": round(emission, 3),
            "details": details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
