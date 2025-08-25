import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt


def load_mat_file(mat_path_file) -> dict:
    return sio.loadmat(mat_path_file)

def plot_seismogram(sensors_list, plot_title="Title"):
    """
    Function for plotting seismogram.
    """
    assert len(sensors_list) > 0, "sensors_list is empty"
    dt = 1.0 / sensors_list[0].sampling_rate
    time = np.arange(len(sensors_list[0].data)) * dt

    full_data = [sensor_i.data for sensor_i in sensors_list]

    plt.figure(figsize=(14, 6))
    scale = 0.5 / np.max(np.abs(full_data))
    offset = np.arange(len(sensors_list)) * 1.0

    for i in range(len(sensors_list)):
        trace = sensors_list[i].data
        plt.plot(offset[i] + trace * scale, time, 'k')
        # first-break
        plt.plot(offset[i], sensors_list[i].first_break_time, 'ro')

    plt.gca().invert_yaxis()
    plt.xlabel("Trace Number")
    plt.ylabel("Time (s)")
    plt.title(plot_title)
    plt.show()

def plot_traces_subplots(full_data, fs, n_show=None):
    """
    Function for plotting traces of all the sensors samples according to [Time * Amplitude]
    """
    n_traces, n_samples = full_data.shape
    dt = 1.0 / fs
    time = np.arange(n_samples) * dt

    if n_show is None:
        n_show = n_traces
    n_show = min(n_show, n_traces)

    fig, axes = plt.subplots(n_show, 1, figsize=(10, 2*n_show), sharex=True)
    if n_show == 1:
        axes = [axes]

    for i in range(n_show):
        axes[i].plot(time, full_data[i])
        axes[i].set_ylabel(f"Trace {i+1}")
        axes[i].grid(True)

    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout()
    plt.show()

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