from itertools import product

from code_section.sensors import SensorObj
from code_section.consts import DATA_FILES, SENSOR_NUMBER_SIZE, SNR_RATIO_DB, NOISE_TYPES
from code_section.utils.utils import load_mat_file, separate_channels
from code_section.utils.graph_utils import plot_seismogram, plot_traces_subplots, plot_performance_results
from code_section.algorithms import full_picking_algorithm, full_picking_algorithm2, run_performance_analysis


def questions123(data_file_path=DATA_FILES[1], noise_type='', snr_db=0, plot_title="General title"):
    """
    The manager that used the algorithm to find the firs-break on solo channel and export the seismogram.
    """
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_sample_rate = sensors_data_dict['fs'][0][0]
    sensors_list = full_picking_algorithm(sensors_data=sensors_data_dict['data'],
                                          sensors_sample_rate= sensors_sample_rate,
                                          sensors_geometry_data=sensors_data_dict['geometry'],
                                          sensors_length=SENSOR_NUMBER_SIZE, noise_type=noise_type, snr_db=snr_db)

    plot_seismogram(sensors_list, plot_title=plot_title)


def questions4(data_file_path=DATA_FILES[2], noise_type='', snr_db=0, plot_title="Seismogram for Multi-channel with AIC picker + STA/LTA"):
    """
    Function that use:
    1. Separate channels function.
    2. Algorithm to find the first-break for each channel.
    3. Plot the seismogram.
    The function handle with multichannel data.
    """
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_data = sensors_data_dict['data']
    sensors_sample_rate = sensors_data_dict['fs'][0][0]
    full_data_separate_by_channels = []
    pick_channels_for_all_sensors = []

    # 1. Separate the channels in each sensor
    for sensor_num in range(SENSOR_NUMBER_SIZE):
        channels_durations = separate_channels(SensorObj(data=sensors_data[sensor_num],
                                                         sampling_rate=sensors_sample_rate))
        if sensor_num == 0:
            full_data_separate_by_channels = [[] for _ in range(len(channels_durations))]

        pick_channels = []
        for i in range(len(channels_durations)):
            start_index = int(channels_durations[i][0] * sensors_sample_rate)
            end_index = int(channels_durations[i][1] * sensors_sample_rate)
            pick_channels.append([start_index, end_index])
            full_data_separate_by_channels[i].append(sensors_data[sensor_num][start_index:end_index])

        pick_channels_for_all_sensors.append(pick_channels)

    # 2. Use the algorithm form the previous question and collect the first-break in each channel
    all_first_breaks = [[] for _ in range(SENSOR_NUMBER_SIZE)]
    for i in range(len(full_data_separate_by_channels)):
        tmp = full_picking_algorithm2(sensors_data=full_data_separate_by_channels[i],
                                          sensors_sample_rate= sensors_sample_rate,
                                          sensors_geometry_data=sensors_data_dict['geometry'],
                                          sensors_length=SENSOR_NUMBER_SIZE, noise_type=noise_type, snr_db=snr_db)

        for sensor_num in range(SENSOR_NUMBER_SIZE):
            start_index = pick_channels_for_all_sensors[sensor_num][i][0]
            end_index = pick_channels_for_all_sensors[sensor_num][i][1]
            sensors_data[sensor_num][start_index:end_index] = tmp[sensor_num].data
            break_time_founded = int(tmp[sensor_num].first_break_time * sensors_sample_rate)
            all_first_breaks[sensor_num].append(start_index + break_time_founded)

    # 3. Organize the data for seismogram plot
    final_picking = []
    for sensor_num in range(SENSOR_NUMBER_SIZE):
        temp_sensor_obj = SensorObj(data=sensors_data[sensor_num],
                                    sampling_rate=sensors_sample_rate)
        temp_sensor_obj.first_break_time = all_first_breaks[sensor_num]
        final_picking.append(temp_sensor_obj)

    plot_seismogram(final_picking, plot_title=plot_title)

# Example use of the bonus
# questions4()

# Example use of the questions123 function
# for snr_db, noise_type in product([-5,0,5,10,15],['white','pink']):
#     questions123(data_file_path=DATA_FILES[1], noise_type=noise_type, snr_db=snr_db,
#         plot_title="Seismogram for continuous data\n For: STA/LTA + AIC picker + Cross-correlation\nSNR ratio: {} and nosie: {}".format(snr_db, noise_type))


# Example use of the performance analysis function
# res = run_performance_analysis(data_file_path=DATA_FILES[0], num_iterations=100)
# for i in range(len(res)):
#     plot_performance_results(results=res, snr_range=SNR_RATIO_DB, sampling_rate=2000, sensor_index=i)
