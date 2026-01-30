import joblib
import os
import numpy as np
class AIEngine:
    def __init__(self):
        self.model = None
        self.sc = None
        if os.path.exists("SolarServer_model.pkl"):
            self.model = joblib.load("SolarServer_model.pkl")
            print("AI Engine: Online")
        else:
            print("AI Engine: Offline")
        if os.path.exists("SolarServer_scaler.pkl"):
            self.sc = joblib.load("SolarServer_scaler.pkl")
    def predict_threat(self,ip,port,status="ESTABLISHED"):
        if not self.model:
            return False
        https = 1 if port==443 else 0
        f = [[port,1000,5000,10,https]]
        if self.sc:
            f = self.sc.transform(f)
        return self.model.predict(f)[0]==-1
    def get_threat_score(self,ip,port,status="ESTABLISHED"):
        if not self.model:
            return 0.0
        https = 1 if port==443 else 0
        f = [[port,1000,5000,10,https]]
        if self.sc:
            f = self.sc.transform(f)
        return float(self.model.decision_function(f)[0])
    def get_stats(self):
        return {"model_loaded":self.model is not None}
e = AIEngine()
print(f"Port 443: {'THREAT' if e.predict_threat('',443) else 'SAFE'}")
print(f"Port 4444: {'THREAT' if e.predict_threat('',4444) else 'SAFE'}")
print(f"Port 6666: {'THREAT' if e.predict_threat('',6666) else 'SAFE'}")