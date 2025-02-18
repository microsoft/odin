import random

def get_random_response(question, chat_history):
    # list of random facts
    facts = [
        "Bananas are berries, but strawberries are not.",
        "A group of flamingos is called a 'flamboyance'.",
        "Octopuses have three hearts.",
        "Honey never spoils; archaeologists have found edible honey in ancient Egyptian tombs.",
        "Wombat poop is cube-shaped."
    ]
    # list of random jokes
    jokes = [
        "Why don’t skeletons fight each other? They don’t have the guts!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "I told my wife she should embrace her mistakes. She gave me a hug."
    ]
    # list of random statements
    statements = [
        "The sky is blue.",
        "Water boils at 100°C at sea level.",
        "Gravity keeps us on the ground.",
        "The Earth orbits the Sun.",
        "Pizza is delicious."
    ]
    # complie response
    resp = {
        'question': question,
        'generation': random.choice(facts + jokes + statements),
        'task': 'conversate',
        'documents': [],
        'chat_history': chat_history
    }
    return resp

# Example usage
if __name__ == "__main__":
    print(get_random_response())
