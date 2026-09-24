# PumpCalc

PumpCalc is a Streamlit mini project for **Problem No. 16 — Centrifugal Pump
Total Head & Power Sizing Tool**. It calculates pipe velocities, Darcy-Weisbach
friction losses, total manometric head, water power, pump shaft power and a
preliminary standard motor rating.

## Main features

- Clear inputs with SI units
- Input validation and practical design warnings
- Total-head and power calculations
- Automatic next-higher motor selection
- System-head curve with the selected operating point
- Head-contribution chart
- Formula-by-formula calculation page
- Viva questions and engineering assumptions
- Downloadable CSV result table
- Responsive industrial-style interface

## Project files

```text
PumpCalc_Streamlit/
├── app.py
├── pump_calculations.py
├── requirements.txt
├── MANUAL_TEST_CASE.md
├── README.md
└── tests/
    └── test_pump_calculations.py
```

## Run on a computer

1. Install Python 3.10 or newer.
2. Open a terminal inside this project folder.
3. Install the required libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local address shown in the terminal, normally
   `http://localhost:8501`.

## Verify the calculations

Run the automated tests from the project folder:

```bash
python -m unittest discover -s tests -v
```

The default values reproduce the solved case in `MANUAL_TEST_CASE.md`.

## Team details

The submitted team information is stored near the top of `app.py` in:

- `TEAM_MEMBERS`
- `DEFAULT_GROUP_NUMBER`
- `DEFAULT_COLLEGE_NAME`
- `DEFAULT_COURSE_NAME`

## Upload to GitHub

1. Create a new public GitHub repository.
2. Upload all files and the `tests` folder from this project.
3. Confirm that `app.py` and `requirements.txt` are in the repository root.

## Deploy on Streamlit Community Cloud

1. Sign in at Streamlit Community Cloud using GitHub.
2. Select **Create app**.
3. Choose the repository and branch.
4. Set the main file path to `app.py`.
5. Select **Deploy** and wait for the public URL.

## Engineering scope

The app assumes water transfer between two open reservoirs. It includes static
head and straight-pipe Darcy friction losses. It does not include minor losses,
NPSH, cavitation analysis, a manufacturer pump curve, pressure-vessel terms or
transient effects. The motor result is suitable for a student design exercise,
not direct equipment purchasing.
