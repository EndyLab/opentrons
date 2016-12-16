from flask import Flask, render_template
from flask_ask import Ask, statement, question
import robocontroller
import threading

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def start_skill():
    text = "Welcome to RoboBench. Please ask me to do something, or ask for help"
    return question(text) \
        .reprompt("I didn't get that. Ask me to do something. For example, 'Make a dilution series'")

@ask.intent('HelloIntent')
def hello(firstname):
    text = "Hello {}".format(firstname)
    return statement(text).simple_card('Hello', text)

@ask.intent('MoveLiquidIntent', convert={'volume': int}, default={'volume': 200})
def moveliquid(start, end, volume):
    if start is None or end is None:
        return question("Please tell me where to move things. For example, Alexa, tell Robo Bench to move 100 microlitres of A 1 to C 1")

    start = start.upper().replace(" ", "")
    end = end.upper().replace(" ", "")

    print("Starting move from {} to {}: {} ul".format(start, end, volume))

    threading.Thread(target=robocontroller.move_liquid, args=(start, end, volume)).start()    # robocontroller.move_liquid(start, end, volume)

    return statement("Moving {} microlitres from {} to {}".format(volume, start, end))

@ask.intent('DilutionSeriesIntent', convert={'count': int, 'ratio': int})
def protocol(count, ratio):
    if count is None or ratio is None:
        return question("Please tell me the number of tubes and the ratio")

    print("Starting dilution series with count {} and ratio 1:{}".format(count, ratio))

    threading.Thread(target=robocontroller.dilution_series, args=(1/ratio, count)).start()    # robocontroller.move_liquid(start, end, volume)

    # robocontroller.dilution_series(1/ratio, count)

    return statement("Okay, making a 1 in {} dilution series with {} tubes".format(ratio, count)) \
        .simple_card(
            title="Making dilution series",
            content="1 in {} dilutions, {} tubes".format(ratio, count)
        )


@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
