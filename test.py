import gridstatus
import pandas as pd 

caiso = gridstatus.CAISO()

# df = caiso.get_load_forecast_day_ahead("2025-08-01")
# df["Time"] = df["Interval Start"]
# df = df[df["TAC Area Name"] == "CA ISO-TAC"]

# df.to_csv("load_forecast-1.csv", index=False)


# df_1 = caiso.get_load_forecast_15_min("2025-08-01")
# df_1.to_csv("load_forecast-15.csv", index=False)

# def get_load_forecast_15_min(date):
#     """Fetch 15-minute load forecast data for a specific date."""
#     caiso = gridstatus.CAISO()
#     load_forecast_df = caiso.get_load_forecast_15_min(date)
#     load_forecast_df["Time"] = load_forecast_df["Interval Start"]
#     load_forecast_df = load_forecast_df[load_forecast_df["TAC Area Name"] == "CA ISO-TAC"]
#     load_forecast_df = load_forecast_df.drop(columns=["TAC Area Name"])
#     return load_forecast_df

# storage_df  = caiso.get_storage(date='latest')
# for key in storage_df.keys():
#     print(key, type(storage_df[key]))

# for key,value in storage_df.items():
#     print(key, value)

# time = storage_df['time']
# time = pd.to_datetime(time).strftime('%H:%M')
# print(time)
# supply = storage_df['supply']
# print(supply)

# # storage_df  = caiso.get_storage(date='2025-08-15')
# # storage_df.to_csv("storage.csv")

# lmp_df = caiso.get_lmp(date='2025-08-01', market=gridstatus.Markets.DAY_AHEAD_HOURLY, locations='ALL')
# lmp_df.to_csv("lmp-all.csv", index=False)

# curtailment_df = caiso.get_curtailment(date=pd.Timestamp("2025-01-01"))
# curtailment_df.to_csv("tmp/curtailment.csv", index=False)

# df = caiso.get_curtailed_non_operational_generator_report(date=pd.Timestamp("2024-08-01"))
# df.to_csv("tmp/curtailed_non_operational_generator_report.csv", index=False)

# print(caiso.get_status())

df = caiso.get_fuel_mix(date="2024-08-01")

# -------- 新增：按能源类型重组为字典 --------
energy_types = [
        "Solar", "Wind", "Geothermal", "Biomass", "Biogas", "Small Hydro",
        "Coal", "Nuclear", "Natural Gas", "Large Hydro", "Batteries", "Imports", "Other"
    ]
result = {}
for energy in energy_types:
    if energy in df.columns:
        # 以时间为key，数值为value
        # result[energy] = dict(zip(df["Time"], df[energy]))
        result[energy] = dict(zip(df["Time"].astype(str), df[energy]))

import json

with open("tmp/fuel_mix_by_type.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

for energy, data in result.items():
    df_energy = pd.DataFrame(list(data.items()), columns=["Time", energy])
    df_energy.to_csv(f"tmp/{energy}_fuel_mix.csv", index=False)


# df = caiso.get_fuel_mix(date="latest")
# df.to_csv("tmp/fuel_mix_latest.csv", index=False)

