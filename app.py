from flask import Flask, render_template, request, jsonify
from crop_data import crop_info, additional_info, soil_characteristics
import requests
import pickle

crop_data = {
    "rice": (80, 40, 40),
    "maize": (80, 40, 20),
    "chickpea": (40, 60, 80),
    "kidneybeans": (20, 60, 20),
    "pigeonpeas": (20, 60, 20),
    "mothbeans": (20, 40, 20),
    "mungbean": (20, 40, 20),
    "blackgram": (40, 60, 20),
    "lentil": (20, 60, 20),
    "pomegranate": (20, 10, 40),
    "banana": (100, 75, 50),
    "mango": (20, 20, 30),
    "grapes": (20, 125, 200),
    "watermelon": (100, 10, 50),
    "muskmelon": (100, 10, 50),
    "apple": (20, 125, 200),
    "orange": (20, 10, 10),
    "papaya": (50, 50, 50),
    "coconut": (20, 10, 30),
    "cotton": (120, 40, 20),
    "jute": (80, 40, 40),
    "coffee": (100, 20, 30)
}

with open('models/model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
app = Flask(__name__)


def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = "fb9f123dddebbaf87cb6cfd477e2c65f"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

from flask import Flask, render_template, request

app = Flask(__name__)

# Import your model here
# Example: from models import your_model_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crop_recommender', methods=['GET', 'POST'])
def crop_recommender():
    if request.method == 'POST':
        # Get form data from the request
        nitrogen = float(request.form['nitrogen'])
        potassium = float(request.form['potassium'])
        phosphorous = float(request.form['phosphorous'])
        state = request.form['state']
        city = request.form['city']
        rainfall = float(request.form['rainfall'])
        ph = float(request.form['ph'])

        # Call your crop recommendation function with the provided data
        temperature, humidity = weather_fetch(city)
        crop_recommendation = model.predict([[nitrogen, phosphorous, potassium, temperature, humidity, ph, rainfall]])
        
        # Replace the above line with actual prediction logic using your model
        
        return render_template('crop_recommender.html', crop_recommendation=crop_recommendation[0])

    return render_template('crop_recommender.html')

def recommend_fertilizer(nitrogen, phosphorous, potassium, crop):
    crop = str(crop).lower()
    if crop in crop_data:
        recommended_fertilizer = crop_data[crop]
        recommended_nitrogen, recommended_phosphorous, recommended_potassium = recommended_fertilizer

        # Calculate the difference between recommended and provided nutrient levels
        nitrogen_diff = recommended_nitrogen - nitrogen
        phosphorous_diff = recommended_phosphorous - phosphorous
        potassium_diff = recommended_potassium - potassium

        # Generate a paragraph of soil improvement suggestions and fertilizer recommendations
        paragraph = f"For growing {crop}, it is recommended to improve the soil's nutrient content. Your current soil analysis indicates that your soil may benefit from the following actions:\n"

        if nitrogen_diff > 0:
            paragraph += f"- Increase Nitrogen content by adding organic matter or nitrogen-rich fertilizers like urea or ammonium sulfate. Apply {nitrogen_diff} kg/ha of nitrogen to reach the recommended level.\n"
        if phosphorous_diff > 0:
            paragraph += f"- Enhance Phosphorous content by applying phosphorous-rich fertilizers such as superphosphate or triple superphosphate. Apply {phosphorous_diff} kg/ha of phosphorous as needed.\n"
        if potassium_diff > 0:
            paragraph += f"- Boost Potassium content by using potassium-rich fertilizers like potassium chloride or potassium sulfate. Apply {potassium_diff} kg/ha of potassium to meet the recommended level.\n"

        paragraph += f"These fertilizers will help provide the essential nutrients needed for {crop} growth and improve soil fertility. It's also important to monitor soil pH and adjust it if necessary to ensure optimal nutrient uptake."

        return paragraph
    else:
        return "Crop not found in recommendations"

@app.route('/fertilizer_recommender', methods=['GET', 'POST'])
def fertilizer_recommender():
    if request.method == 'POST':
        # Get form data from the request
        nitrogen = float(request.form['nitrogen'])
        potassium = float(request.form['potassium'])
        phosphorous = float(request.form['phosphorous'])
        crop = request.form['crop']

        # Call your fertilizer recommendation function with the provided data
        fertilizer_recommendation = recommend_fertilizer(nitrogen, phosphorous, potassium , crop)
        
        # Replace the above line with actual prediction logic using your model
        
        return render_template('fertilizer_result.html', fertilizer_recommendation=fertilizer_recommendation)

    return render_template('fertilizer_recommender.html')
@app.route('/information', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        selected_crop = request.form.get('crop')
        crop_details = crop_info.get(selected_crop)
        additional_details = additional_info.get(selected_crop)
        return render_template('information.html', crop=crop_details, additional=additional_details)
    crops = list(crop_info.keys())
    return render_template('information.html', crops=crops)
@app.route("/soil_recommender", methods=["GET", "POST"])
def find_soil():
    if request.method == 'POST':
        selected_soil = request.form.get('soil_type')
        prediction = soil_characteristics.get(selected_soil)
        return render_template('soil_recommender.html', soil_types=soil_characteristics.keys(), selected_soil=selected_soil, prediction=prediction)

    return render_template('soil_recommender.html', soil_types=soil_characteristics.keys())
        


if __name__ == '__main__':
    app.run(debug=True)
