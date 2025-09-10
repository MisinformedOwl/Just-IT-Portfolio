from databaseConn import databaseConn
import pandas as pd

frame = pd.read_csv("data.csv")
# conn = databaseConn()
# conn.sendData(frame)
frame.loc[frame["NameOfBusiness"] == "MandM", "Salary"] = 0
print(frame[frame["NameOfBusiness"] == "MandM"])