import os
import requests
import json
import datetime
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION ---
# 1. Your Real WAQI Token (Added!)
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

# 2. Your Google API Key (You still need to plug this in)
# Get it from https://aistudio.google.com/
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Nano Banana Pro Client
client = genai.Client(api_key=GOOGLE_API_KEY)

def get_coordinates_gemini(city_name):
    """
    Asks Gemini to resolve the city name to lat/lng.
    This handles broad regions (Goa) or ambiguous names better than keyword search.
    """
    print(f"🌍 Resolving coordinates for '{city_name}'...")
    try:
        prompt = f"Return only a JSON object with 'lat' and 'lng' (floats) for the center of {city_name}. No markdown, no code blocks, just raw JSON."
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        # Clean response just in case
        text = response.text.strip().replace("```json", "").replace("```", "")
        coords = json.loads(text)
        return coords['lat'], coords['lng']
    except Exception as e:
        print(f"❌ Geocoding failed: {e}")
        return None, None


def get_live_data(city="beijing", override_aqi=None):
    """
    Fetches real-time AQI from WAQI API using the provided token.
    If override_aqi is provided, it uses that value instead.
    """

    if override_aqi is not None:
        print(f"🔧 Using Manual AQI Override: {override_aqi}")
        # Mocking data structure for manual override
        now = datetime.datetime.now()
        formatted_date = now.strftime("%d %b %Y").upper()

        # Determine level/color based on manual value
        aqi = override_aqi
        # ...reuse classification logic...
        # Standardized Classification
        if aqi > 300:
            level, color, fog = "HAZARDOUS", "#7e0023", "dense white winter smog, low visibility"
        elif aqi > 200:
            level, color, fog = "VERY UNHEALTHY", "#8f3f97", "thick white mist, cold hazy air, reduced visibility"
        elif aqi > 150:
            level, color, fog = "UNHEALTHY", "#ff0000", "moderate winter fog, white haze layer"
        elif aqi > 100:
            level, color, fog = "SENSITIVE", "#ff7e00", "light mist, soft cold sunlight"
        elif aqi > 50:
            level, color, fog = "MODERATE", "#ffff00", "very light haze, distinct buildings"
        else:
            level, color, fog = "GOOD", "#009966", "crystal clear winter sky, sharp distinct shadows, no smog"

        return {
            "search_city": city,
            "city": city,
            "aqi": aqi,
            "temp": "N/A", # No temp in manual mode
            "temp_val": 25, # Default warm
            "level": level,
            "color": color,
            "fog_prompt": fog,
            "date": formatted_date
        }

    print(f"📡 Fetching live data for {city}...")
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"

    try:
        response = requests.get(url).json()

        if response['status'] != 'ok':
            print(f"⚠️ Direct lookup failed for '{city}'. Trying AI Geolocation...")

            # 1. Get Coordinates via Gemini
            lat, lng = get_coordinates_gemini(city)

            if lat and lng:
                # 2. Use WAQI Geo-Feed
                print(f"📍 Found Location: {lat}, {lng}. Finding nearest station...")
                geo_url = f"https://api.waqi.info/feed/geo:{lat};{lng}/?token={WAQI_TOKEN}"
                response = requests.get(geo_url).json()
            else:
                 print(f"❌ Could not resolve location for '{city}'")
                 return None

        if response['status'] != 'ok':
             print(f"⚠️ API Error: {response.get('data', 'Unknown error')}")
             return None

        data = response['data']

        # Log the actual station being used
        station_name = data.get('city', {}).get('name', 'Unknown Station')
        print(f"📍 Data source: {station_name}")

        aqi = data['aqi']

        # Extract Timestamp from API (more accurate than system time)
        # Format: "2025-12-15 15:00:00" -> "15 DEC 2025"
        raw_time = data.get('time', {}).get('s', '')
        try:
            if raw_time:
                date_obj = datetime.datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
            else:
                raise ValueError("Empty time string")
        except:
            date_obj = datetime.datetime.now() # Fallback to system time

        formatted_date = date_obj.strftime("%d %b %Y").upper()

        # Classify AQI Levels (Standardized)
        # VISUAL ADJUSTMENT: Use "White/Grey Fog" for pollution to simulate Winter Smog, not Dust/Sand.
        if aqi > 300:
            level, color, fog = "HAZARDOUS", "#7e0023", "dense white winter smog, low visibility" # Removed 'freezing'
        elif aqi > 200:
            level, color, fog = "VERY UNHEALTHY", "#8f3f97", "thick white mist, cold hazy air, reduced visibility"
        elif aqi > 150:
            level, color, fog = "UNHEALTHY", "#ff0000", "moderate winter fog, white haze layer"
        elif aqi > 100:
            level, color, fog = "SENSITIVE", "#ff7e00", "light mist, soft cold sunlight"
        elif aqi > 50:
            level, color, fog = "MODERATE", "#ffff00", "very light haze, distinct buildings"
        else:
            level, color, fog = "GOOD", "#009966", "crystal clear winter sky, sharp distinct shadows, no smog"

        # Try to get temperature (IAQI)
        try:
            temp = data['iaqi']['t']['v']
            temp_str = f"{temp}°C"
        except:
            temp = 25 # Default fallback
            temp_str = "N/A"

        # Try to keep the full name or find native script in parens if available
        # WAQI often returns "Beijing (北京)"
        raw_api_city = data['city']['name']

        return {
            "search_city": city,
            "city": raw_api_city, # Keep full string so model can infer native name or extraction
            "aqi": aqi,
            "temp": temp_str,
            "temp_val": temp, # Numeric value for logic
            "level": level,
            "color": color,
            "fog_prompt": fog,
            "date": formatted_date
        }

    except Exception as e:
        print(f"❌ Critical Data Error: {e}")
        return None

def generate_nano_banana_art(data):
    """
    Uses 'Nano Banana Pro' (gemini-3-pro-image-preview) to render the base map.
    """
    args = {
        "city": data['search_city'],
        "full_city_string": data['city'],
        "date": data['date'],
        "temp": data['temp'],
        "temp_val": data.get('temp_val', 20),
        "aqi_level": data['level'],
        "aqi_val": data['aqi']
    }

    # Logic to prevent snow in warm/mild cities
    snow_instruction = ""
    if args['temp_val'] > 4: # If warmer than 4C, assume no snow on ground
        snow_instruction = "IMPORTANT: RELATIVE TO TEMPERATURE, DO NOT RENDER SNOW ON THE GROUND OR BUILDINGS. It is a winter season but NOT freezing. Keep ground and roofs clean of snow."
    else:
        snow_instruction = "Light dusting of snow is acceptable if consistent with the city's climate."

    # --- NEW: THOUGHTFUL VIBE CHECK ---
    # Ask Gemini Text model to decide what transit/mood fits this specific city.
    print(f"🧠 Thinking about {args['city']}'s specific vibe...")
    vibe_prompt = f"""
    I am generating a 3D isometric miniature map of {args['city']}.
    Identify the ONE most iconic form of *public* or *local* transport that makes this city unique.
    - If Delhi -> Delhi Metro (Cyan/Blue line train) + Auto Rickshaws.
    - If Goa -> colorful rented scooters + a ferry boat.
    - If London -> Double decker red bus + Black cab.
    - If Venice -> Gondola/Vaporetto.
    - If a generic city -> City buses + cars.

    Output a single short sentence describing exactly what energetic miniature vehicles should be added to the roads/water.
    Example output: "Render a cute miniature cyan-line metro train crossing a viaduct and green-and-yellow auto rickshaws on the roads."
    """
    try:
        vibe_response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=vibe_prompt
        )
        transit_instruction = vibe_response.text.strip()
        print(f"🚌 Decided transit: {transit_instruction}")
    except:
        transit_instruction = "Include moving city traffic like buses and cars."

    # --- REGIONAL BEAUTY & CULTURE CHECK ---
    # Ask Gemini about the unique beauty, culture, and landscape of the region
    print(f"🏔️ Discovering the beauty of {args['city']}...")
    beauty_prompt = f"""
    I am generating a 3D isometric miniature art of {args['city']}.
    Describe in 2-3 sentences the UNIQUE visual beauty of this place that MUST be shown:
    - What natural landscape defines this region? (hills, valleys, rivers, forests, beaches, etc.)
    - What traditional/cultural architecture or structures are iconic? (traditional houses, temples, monuments)
    - What cultural elements make it visually distinct? (tribal art, festivals, traditional dress patterns)

    Examples:
    - Nagaland -> "Lush green rolling hills, traditional Naga morung (community houses) with carved wooden pillars, hornbill motifs, bamboo structures, and vibrant tribal shawl patterns in red and black."
    - Kerala -> "Palm-fringed backwaters, traditional snake boats, red-tiled sloped roof houses, and coconut groves."
    - Rajasthan -> "Golden sand dunes, ornate havelis with jharokha windows, colorful turbans, and majestic forts."

    Output a vivid visual description focusing on what makes {args['city']} and its region UNIQUELY beautiful.
    """
    try:
        beauty_response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=beauty_prompt
        )
        regional_beauty = beauty_response.text.strip()
        print(f"🎨 Regional beauty: {regional_beauty}")
    except:
        regional_beauty = ""

    prompt = f"""
    Create a FLOATING MINIATURE DIORAMA of {args['city']} in isometric 3D style (45° top-down view, 9:16 vertical).

    CRITICAL STYLE REQUIREMENTS:
    - The scene MUST be a FLOATING ISLAND/DIORAMA with clean edges, hovering against a soft pastel blue/grey background.
    - Think of it as a tiny detailed 3D model on a floating platform - NOT a flat landscape photograph.
    - The diorama should have visible depth with layered terrain (foreground, middle, background all on the floating base).

    REGIONAL BEAUTY & CULTURE (MUST BE THE HERO):
    {regional_beauty}
    - If this is a hill region: Show DRAMATIC ROLLING GREEN HILLS as the main visual, with buildings nestled among them.
    - If this has traditional architecture: Make it PROMINENT and CENTERED, not tiny background elements.
    - The natural landscape (hills, rivers, forests) should be sculpted INTO the floating diorama base.

    LANDMARK & SCENE DETAILS:
    - Center the most iconic visual element (whether landmark OR landscape) prominently.
    - Include traditional architecture and cultural structures specific to this area as key features.
    - **TRANSIT & LIFE**: {transit_instruction}
    - Tiny people in traditional local attire, native trees and vegetation.

    The scene features soft, refined textures with realistic PBR materials and gentle, lifelike lighting and shadow effects.

    ATMOSPHERE & SEASON:
    This is a WINTER scene. ({args['date']}, Temp: {args['temp']}).
    - The atmosphere is determined by the AQI: {args['aqi_val']} ({args['aqi_level']}).
    - VISUALS: "{data.get('fog_prompt')}".
    - {snow_instruction}
    - CRITICAL: If the AQI is high, render **WHITE/GREY WINTER FOG**. DO NOT RENDER BROWN DUST OR ORANGE SANDSTORM.
    - If the AQI is low (Good/Moderate), render **CRYSTAL CLEAR BLUE SKIES**, even if it is winter. Winter does not always mean smog.
    - Weather elements should be creatively integrated.

    Use a clean, unified composition with minimalistic aesthetics and a soft, solid-colored background (e.g. soft pastel blue or grey) that highlights the main content. The overall visual style is fresh and soothing.

    TEXT & UI INSTRUCTIONS:
    - RENDER THE TEXT EXACTLY AS REQUESTED BELOW.
    - TOP CENTER: Display the City Name "{args['city'].title()}" in LARGE, BOLD, CLEAN 3D English Text. It should hover prominently in the sky.
    - BELOW CITY NAME: Place a high-quality 3D Weather Icon (Sun/Cloud).
    - BELOW ICON:
       Line 1: "{args['date']}" (Medium size, grey/neutral).
       Line 2: "{args['temp']} | AQI: {args['aqi_val']}" (Medium size, clear text).

    - STYLE: The text must be clean, legible, and floating. NO background plates or boxes. Make it look like a high-end weather app card.
    """

    print(f"🍌 Asking Nano Banana Pro to render {args['city']} (Temp: {args['temp']}, AQI: {args['aqi_val']})...")

    try:
        response = client.models.generate_content(
            model='gemini-3-pro-image-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )

        # Extract image
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return Image.open(BytesIO(part.inline_data.data))

    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        # Return a blank grey image so the script doesn't crash
        return Image.new('RGB', (1080, 1920), color=(200, 200, 200))

def overlay_hud(image, data):
    """
    Draws the text overlay using local fonts.
    """
    if not image: return

    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 1. Setup Fonts (Adjust size relative to image width)
    try:
        # Tries to find Arial, falls back to default
        font_large = ImageFont.truetype("arial.ttf", int(width * 0.12)) # City Name
        font_med = ImageFont.truetype("arial.ttf", int(width * 0.05))   # AQI
        font_small = ImageFont.truetype("arial.ttf", int(width * 0.035)) # Date
    except:
        font_large = font_med = font_small = ImageFont.load_default()

    # 2. Define Text
    city_text = data['city'].upper()
    aqi_text = f"AQI: {data['level']} ({data['aqi']})"
    date_text = data['date']

    # 3. Helper to center text
    def draw_center(text, font, y_pct, color, bold=False):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) / 2
        y = height * y_pct

        # distinct "shadow" for readability against 3D art
        draw.text((x+2, y+2), text, font=font, fill="black") # Shadow
        draw.text((x, y), text, font=font, fill=color)

    # 4. Draw
    draw_center(city_text, font_large, 0.08, "white")
    draw_center(aqi_text, font_med, 0.18, data['color']) # Dynamic AQI Color
    draw_center(date_text, font_small, 0.23, "lightgrey")

    return image

# --- MAIN RUN ---
if __name__ == "__main__":
    target_city = input("Enter the city name: ").strip()
    if not target_city:
        target_city = "beijing" # Default to Beijing if empty

    # Allow manual override for specific demos or data gaps
    manual_aqi = input("Enter manual AQI (optional, press Enter to skip): ").strip()

    live_data = get_live_data(target_city, override_aqi=int(manual_aqi) if manual_aqi.isdigit() else None)

    if live_data:
        # Generate art with embedded text (no HUD overlay needed if the model follows instructions)
        base_art = generate_nano_banana_art(live_data)

        # Determine filename
        filename = f"{target_city}_Status_Card.png"
        base_art.save(filename)
        base_art.show()
        print(f"✅ Success! Saved to {filename}")
