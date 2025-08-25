import numpy as np
from itertools import product
from code.sensors import SensorObj
from code.consts import DATA_FILES, SENSOR_NUMBERS_Q1
from code.utils import load_mat_file, plot_seismogram, add_noise, plot_traces_subplots


def temp_main(path_file=DATA_FILES[0], sensor_number=0):
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import numpy as np
    # Sample amplitude data
    g = load_mat_file(mat_path_file=path_file)
    amplitudes = g['data'][sensor_number]
    time = np.arange(len(amplitudes))  # Assuming uniform time intervals
    # Create the main window
    root = tk.Tk()
    root.title("Amplitude vs Time")
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(time, amplitudes, marker='o', linestyle='-', color='blue')
    ax.set_title('Amplitude vs Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.grid(True)
    # Embed the plot in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    root.mainloop()


def main(data_file_path=DATA_FILES[1], noise_type=None, snr_db=0, plot_title="General title"):
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_list, signal_pattern = [], None
    sample_rate = sensors_data_dict['fs'][0][0]

    for sensor_num in range(SENSOR_NUMBERS_Q1):
        temp_sensor_obj = SensorObj(data=sensors_data_dict['data'][sensor_num],
                                    sampling_rate=sample_rate,
                                    geometry_location=sensors_data_dict['geometry'][sensor_num])
        if sensor_num == 0:
            first_break_frame, end_break_frame = temp_sensor_obj.find_break_range()
            signal_pattern = temp_sensor_obj.data[first_break_frame:end_break_frame]
            print(f"{sensor_num + 1} - [{first_break_frame}:{end_break_frame}]")

        if noise_type:
            temp_sensor_obj.add_noise(snr_db=snr_db, noise_type=noise_type)

        correlation_result = temp_sensor_obj.cross_correlation(signal_pattern)
        temp_sensor_obj.first_break_time = np.argmax(correlation_result) / sample_rate
        print("Sensor number: {} \n The first break is in: {}".
              format(sensor_num + 1, temp_sensor_obj.first_break_time))
        sensors_list.append(temp_sensor_obj)

    plot_seismogram(sensors_list, plot_title=plot_title)


for snr_db, noise_type in product([0,10],['white','pink']):
    main(data_file_path=DATA_FILES[1], noise_type=noise_type, snr_db=snr_db,
         plot_title="Seismogram with Cross-correlation with {} snr ratio and nosie: {}".format(snr_db, noise_type))

# temp_main(path_file=DATA_FILES[1], sensor_number=0)
# for i in [0, 10]:
#     nosie_data = add_noise(load_mat_file(mat_path_file=DATA_FILES[1])['data'], snr_db=i, noise_type='pink')
#     plot_traces_subplots(nosie_data, 2000, n_show=None)