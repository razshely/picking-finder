import numpy as np
import scipy.io as sio

from code_section.sensors import SensorObj

def aic_pick(x):
    """Return index of AIC minimum (classic variance-based AIC)."""
    N = len(x)
    # work on demeaned signal
    y = x - np.mean(x)
    cumsq = np.cumsum(y**2)
    total = cumsq[-1]
    eps = 1e-20

    k = np.arange(1, N-1)
    var1 = cumsq[k-1] / k
    var2 = (total - cumsq[k-1]) / (N - k)
    var1 = np.maximum(var1, eps)
    var2 = np.maximum(var2, eps)
    aic = k * np.log(var1) + (N - k - 1) * np.log(var2)

    idx = np.argmin(aic) + 1  # shift because k starts at 1
    return idx

def load_mat_file(mat_path_file) -> dict:
    return sio.loadmat(mat_path_file)

def add_noise(full_data, snr_db=2, noise_type="white", fs=2000) -> np.ndarray:
    """
    Add noise (white or pink) to a signal according to a given SNR.
    """
    data_plus_noise = []
    for d in full_data:
        data = np.array(d)
        sig_power = np.mean(data ** 2)
        # SNR: convert dB → linear
        snr_linear = 10 ** (snr_db / 10)
        noise_power = sig_power / snr_linear

        if noise_type.lower() == "white":
            noise = np.random.normal(0, np.sqrt(noise_power), len(data))

        elif noise_type.lower() == "pink":
            # Pink noise via frequency-domain shaping (1/sqrt(f))
            white = np.random.normal(0, 1, len(data))
            fft_vals = np.fft.rfft(white)
            freqs = np.fft.rfftfreq(len(data), 1 / fs)
            fft_vals /= np.where(freqs == 0, 1, np.sqrt(freqs))  # scale by 1/sqrt(f)
            pink = np.fft.irfft(fft_vals, n=len(data))
            pink = pink / np.std(pink) * np.sqrt(noise_power)  # scale to match power
            noise = pink

        else:
            raise ValueError("noise_type must be 'white' or 'pink'")

        data_plus_noise.append(data + noise)
    return np.array(data_plus_noise)

def separate_channels(sensor: SensorObj, threshold_magnitude = 0.052):
    """

    :return:
    """
    frequencies, time_param, magnitude = sensor.get_spectrogram_attribute(nperseg=256, noverlap=128)
    magnitude = np.abs(magnitude)

    # For each time frame, check if any frequency bin exceeds threshold
    above_threshold = np.any(magnitude > threshold_magnitude, axis=0)

    ranges = []
    in_range = False
    start_time = None

    for i, val in enumerate(above_threshold):
        if val and not in_range:
            # Start of new range
            in_range = True
            start_time = time_param[i]

        elif not val and in_range:
            # End of range
            in_range = False
            ranges.append((start_time, time_param[i]))

    # If still inside a range at the end
    if in_range:
        ranges.append((start_time, time_param[-1]))

    return ranges

# # פונקציה לחישוב שגיאה (RMSE או MAE)
# def calc_error(gt_signal, test_signal, metric="rmse"):
#     gt_signal = np.asarray(gt_signal)
#     test_signal = np.asarray(test_signal)
#     if metric == "mae":
#         return np.mean(np.abs(gt_signal - test_signal))
#     elif metric == "rmse":
#         return np.sqrt(np.mean((gt_signal - test_signal)**2))
#     else:
#         raise ValueError("metric must be 'mae' or 'rmse'")
#
# # סימולציה: חקר ביצועים מול SNR
# def snr_performance_demo(gt_signal, snr_values, metric="rmse", runs_per_snr=10):
#     errors = []
#     for snr in snr_values:
#         run_errors = []
#         for _ in range(runs_per_snr):
#             noisy = add_noise_by_snr(gt_signal, snr)
#             err = calc_error(gt_signal, noisy, metric=metric)
#             run_errors.append(err)
#         errors.append(np.mean(run_errors))
#
#     # הצגת גרף
#     plt.figure(figsize=(8, 5))
#     plt.plot(snr_values, errors, marker='o', color='purple')
#     plt.gca().invert_xaxis()  # אופציונלי – להראות ירידה בביצועים עם ירידת SNR
#     plt.title("RMSE כתלות ב-SNR")
#     plt.xlabel("SNR [dB]")
#     plt.ylabel("שגיאה (RMSE)")
#     plt.grid(True)
#     plt.show()