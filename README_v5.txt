v5: PV + wind + SMR + grid, 25 years, baseline x index synthetic weather years feeding the representative days.
Keep together in one folder: app_v5.py, vpp_backend_v5.py, requirements.txt (test_v5.py optional; edit its CSV paths first).
Run:  pip install -r requirements.txt ; streamlit run app_v5.py
Upload solar (timestamp, ghi), wind (timestamp, wind_speed), load (timestamp, load_kw). Files may cover several years.
Then open the Optimization tab and press "Run NSGA-II".
Streamlit Cloud: main file app_v5.py. Rename downloaded files so they have no "(1)" in the name.
