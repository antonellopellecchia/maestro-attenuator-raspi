from flask import Flask
from attenuator_control import AttenuatorController

app = Flask(__name__)

controller = AttenuatorController()
print('Controller connected')

@app.route("/get")
def get_attenuation():
    attenuation = float(controller.GetAttenuation()*100)
    return {'status': 'OK', 'attenuation': f"{attenuation}"}

@app.route("/set/<int:attenuation>")
def set_attenuation(attenuation):
    try:
        controller.SetAttenuation(attenuation)
        return {'status': 'OK'}
    except: return {'status': 'ERROR'}