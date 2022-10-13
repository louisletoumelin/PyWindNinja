from src import downscale_windninja
import matplotlib.pyplot as plt

df_inputs, df_outputs = downscale_windninja()

plt.figure()
ax = plt.gca()
df_outputs["Col du Lac Blanc"]["UV_wn"].plot(ax=ax, label="Wind Ninja")
df_inputs["Wind"][df_inputs["name"] == "Col du Lac Blanc"].plot(ax=ax, label="AROME")
df_inputs["vw10m(m/s)"][df_inputs["name"] == "Col du Lac Blanc"].plot(ax=ax, label="observation")
plt.legend()
