import numpy as np
import matplotlib.pyplot as plt

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

def plot_frequency_analysis_multichannel(sensors_list, nperseg=256, noverlap=128, max_sensors_for_represent=8):
    """
    Plot magnitude spectrum and spectrogram for multiple sensors.
    """
    if not sensors_list:
        raise AttributeError("sensors_list is empty")

    n_sensors = len(sensors_list)
    n_show = min(n_sensors, max_sensors_for_represent)

    fig, axes = plt.subplots(2, n_show, figsize=(4*n_show, 8))

    if n_show == 1:  # keep axes 2D always
        axes = axes.reshape(2, 1)

    for i in range(n_show):
        # Magnitude spectrum
        frequency, magnitude = sensors_list[i].time_to_frequency_domain()

        axes[0, i].plot(frequency, magnitude, 'b')
        axes[0, i].set_title(f"Sensor {i+1} - Spectrum")
        axes[0, i].set_xlabel("Freq [Hz]")
        axes[0, i].set_ylabel("Mag")
        axes[0, i].grid(True)

        # Spectrogram
        frequency, time, magnitude = sensors_list[i].get_spectrogram_attribute(nperseg, noverlap)

        pcm = axes[1, i].pcolormesh(frequency, time, np.abs(magnitude), shading='gouraud')
        axes[1, i].set_title(f"Sensor {i+1} - Spectrogram")
        axes[1, i].set_xlabel("Time [s]")
        axes[1, i].set_ylabel("Freq [Hz]")
        fig.colorbar(pcm, ax=axes[1, i])

    plt.tight_layout()
    plt.show()
