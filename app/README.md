# Cricket Score Predictor UI

This Streamlit interface loads `..\t20_score_predictor.pkl`.

## Run locally

Double-click `run_app.bat`, then open the local URL printed in the console
(usually `http://localhost:8501`). Keep the console window open while using the app.
To run manually from the project root:

```powershell
python -m pip install -r app\requirements.txt
python -m streamlit run app\app.py
```

Change any input to update the estimate. The team names use the alphabetical encoding
used during training; the model's original city mapping was not saved, so predictions
use its most common trained city code.
