import numpy as np
from code_section.sensors import SensorObj
from code_section.consts import DATA_FILES, SENSOR_NUMBER_SIZE
from code_section.utils.utils import load_mat_file, separate_channels, aic_pick
from code_section.utils.graph_utils import plot_seismogram, plot_traces_subplots

def full_picking_algorithm(sensors_data, sensors_geometry_data,
                           sensors_length, sensors_sample_rate, noise_type="", snr_db=2):
    assert sensors_length, "Sensors data is empty!"
    sensors_list, signal_pattern = [], None

    for sensor_num in range(sensors_length):
        temp_sensor_obj = SensorObj(data=sensors_data[sensor_num],
                                    sampling_rate=sensors_sample_rate,
                                    geometry_location=sensors_geometry_data[sensor_num])
        if sensor_num == 0:
            first_break_frame, end_break_frame = temp_sensor_obj.find_break_range()
            signal_pattern = temp_sensor_obj.data[first_break_frame:end_break_frame]
            print(f"{sensor_num + 1} - [{first_break_frame}:{end_break_frame}]")

        if noise_type:
            temp_sensor_obj.add_noise(snr_db=snr_db, noise_type=noise_type)

        correlation_result = temp_sensor_obj.cross_correlation(signal_pattern)
        temp_sensor_obj.first_break_time = np.argmax(correlation_result) / sensors_sample_rate
        print("Sensor number: {} \n The first break is in: {}".
              format(sensor_num + 1, temp_sensor_obj.first_break_time))
        sensors_list.append(temp_sensor_obj)

    return sensors_list

def full_picking_algorithm2(sensors_data, sensors_geometry_data,
                           sensors_length, sensors_sample_rate, noise_type="", snr_db=2):
    assert sensors_length, "Sensors data is empty!"
    sensors_list, signal_pattern = [], None

    for sensor_num in range(sensors_length):
        temp_sensor_obj = SensorObj(data=sensors_data[sensor_num],
                                    sampling_rate=sensors_sample_rate,
                                    geometry_location=sensors_geometry_data[sensor_num])
        if sensor_num == 0:
            first_break_frame = int(aic_pick(sensors_data[sensor_num]))
            end_break_frame = first_break_frame + 450 # figure how to find the end break frame
            signal_pattern = temp_sensor_obj.data[first_break_frame:end_break_frame]
            print(f"{sensor_num + 1} - [{first_break_frame}:{end_break_frame}]")

        if noise_type:
            temp_sensor_obj.add_noise(snr_db=snr_db, noise_type=noise_type)

        correlation_result = temp_sensor_obj.cross_correlation(signal_pattern)
        temp_sensor_obj.first_break_time = np.argmax(correlation_result) / sensors_sample_rate
        print("Sensor number: {} \n The first break is in: {}".
              format(sensor_num + 1, temp_sensor_obj.first_break_time))
        sensors_list.append(temp_sensor_obj)

    return sensors_list


def questions123(data_file_path=DATA_FILES[1], noise_type='', snr_db=0, plot_title="General title"):
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_sample_rate = sensors_data_dict['fs'][0][0]
    sensors_list = full_picking_algorithm2(sensors_data=sensors_data_dict['data'],
                                          sensors_sample_rate= sensors_sample_rate,
                                          sensors_geometry_data=sensors_data_dict['geometry'],
                                          sensors_length=SENSOR_NUMBER_SIZE, noise_type=noise_type, snr_db=snr_db)

    plot_seismogram(sensors_list, plot_title=plot_title)

def questions4(data_file_path=DATA_FILES[2], noise_type='', snr_db=0, plot_title="General title"):
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_data = sensors_data_dict['data']
    sensors_sample_rate = sensors_data_dict['fs'][0][0]
    full_data_separate_by_channels = []
    for sensor_num in range(SENSOR_NUMBER_SIZE):
        channels_durations = separate_channels(SensorObj(data=sensors_data[sensor_num],
                                                         sampling_rate=sensors_sample_rate))
        if sensor_num == 0:
            full_data_separate_by_channels = [[] for _ in range(len(channels_durations))]

        for i in range(len(channels_durations)):
            full_data_separate_by_channels[i].append(sensors_data[i][int(channels_durations[i][0] * sensors_sample_rate):
                                                                     int(channels_durations[i][1]*sensors_sample_rate)])
    full_data_including_picking = []
    for i in range(len(full_data_separate_by_channels)):
         full_data_including_picking.append(full_picking_algorithm(sensors_data=full_data_separate_by_channels[i],
                                              sensors_sample_rate= sensors_sample_rate,
                                              sensors_geometry_data=sensors_data_dict['geometry'],
                                              sensors_length=SENSOR_NUMBER_SIZE, noise_type=noise_type, snr_db=snr_db))

    # TODO: Change the plot_seismogram for print the combine channels
    plot_seismogram(full_data_including_picking, plot_title=plot_title)

questions123(noise_type='pink', snr_db=0, plot_title="Seismogram with AIC SNR=0db(pink noise)")
# Part 1:
# for snr_db, noise_type in product([0,10],['','white','pink']):
#     main(data_file_path=DATA_FILES[1], noise_type=noise_type, snr_db=snr_db,
#          plot_title="Seismogram with Cross-correlation with {} snr ratio and nosie: {}".format(snr_db, noise_type))


# for i in [0, 10]:
#     nosie_data = add_noise(load_mat_file(mat_path_file=DATA_FILES[1])['data'], snr_db=i, noise_type='pink')
#     plot_traces_subplots(load_mat_file(mat_path_file=DATA_FILES[2])['data'], 2000, n_show=None)
