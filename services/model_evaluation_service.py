import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import subway_service as ss
import bus_service as bs



''' 지하철 '''
# y_pred = ss.loaded_subway_rf.predict(ss.X_test)

## MSE, RMSE, MAE, R²
# mse = mean_squared_error(ss.y_test, y_pred)
# rmse = np.sqrt(mse)
# mae = mean_absolute_error(ss.y_test, y_pred)
# r2 = r2_score(ss.y_test, y_pred)
# print("MSE:", mse)
# print("RMSE:", rmse)
# print("MAE:", mae)
# print("R²:", r2)


## 실제값 vs 예측값 산점도
# plt.scatter(ss.y_test, y_pred, alpha=0.7)
# plt.plot([ss.y_test.min(), ss.y_test.max()],
#          [ss.y_test.min(), ss.y_test.max()],
#          'r--')  # 기준선
# plt.xlabel("Actual")
# plt.ylabel("Predicted")
# plt.title("Actual vs Predicted")
# plt.show()

## 잔차 플롯
# residuals = ss.y_test - y_pred
# plt.scatter(y_pred, residuals, alpha=0.7)
# plt.axhline(0, color='red', linestyle='--')
# plt.xlabel("Predicted")
# plt.ylabel("Residuals")
# plt.title("Residual Plot")
# plt.show()




''' 버스 '''
# y_pred = bs.loaded_bus_rf.predict(bs.X_test)


# # MSE, RMSE, MAE, R²
# mse = mean_squared_error(bs.y_test, y_pred)
# rmse = np.sqrt(mse)
# mae = mean_absolute_error(bs.y_test, y_pred)
# r2 = r2_score(bs.y_test, y_pred)
# print("MSE:", mse)
# print("RMSE:", rmse)
# print("MAE:", mae)
# print("R²:", r2)


# # 실제값 vs 예측값 산점도
# plt.scatter(bs.y_test, y_pred, alpha=0.7)
# plt.plot([bs.y_test.min(), bs.y_test.max()],
#          [bs.y_test.min(), bs.y_test.max()],
#          'r--')  # 기준선
# plt.xlabel("Actual")
# plt.ylabel("Predicted")
# plt.title("Actual vs Predicted")
# plt.show()

# # 잔차 플롯
# residuals = bs.y_test - y_pred
# plt.scatter(y_pred, residuals, alpha=0.7)
# plt.axhline(0, color='red', linestyle='--')
# plt.xlabel("Predicted")
# plt.ylabel("Residuals")
# plt.title("Residual Plot")
# plt.show()