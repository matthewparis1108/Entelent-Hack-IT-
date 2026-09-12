import json

def load_json_file(file_path):
    """Load a JSON file and return its contents as a Python object."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
def display_json_data(data):
    """Display the contents of a JSON object in a readable format."""
    print(json.dumps(data, indent=4))
animaldb = load_json_file('animals.json')
plantdb = load_json_file('plant_dataset.json')
plant_unlock_conditions = load_json_file('plant_unlock_conditions.json')
classifications = load_json_file('classifications.json')
display_json_data(animaldb)
display_json_data(plantdb)
display_json_data(plant_unlock_conditions)
display_json_data(classifications)