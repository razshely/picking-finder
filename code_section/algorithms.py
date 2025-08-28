import numpy as np

from code_section.sensors import SensorObj
from code_section.consts import SENSOR_NUMBER_SIZE, SNR_RATIO_DB, NOISE_TYPES, STA_LTA_PARAMS
from code_section.utils.utils import load_mat_file, aic_pick

def run_performance_analysis(data_file_path: str, num_iterations: int):
    """
    Runs a performance analysis of the first break picking algorithm.
    The num_iterations arg is the number of Monte Carlo iterations for each setting.

    Returns:
        A dictionary containing the mean and std dev of the picking error for each sensor and represent its
        noise type and SNR level.
    """
    sensors_data_dict = load_mat_file(mat_path_file=data_file_path)
    sensors_sample_rate = sensors_data_dict['fs'][0][0]
    true_first_break_samples = [sensor_data.first_break_time for sensor_data in full_picking_algorithm(
        sensors_data=sensors_data_dict['data'],
        sensors_sample_rate=sensors_sample_rate,
        sensors_geometry_data=sensors_data_dict['geometry'],
        sensors_length=SENSOR_NUMBER_SIZE, noise_type='')]


    results = [{} for _ in range(SENSOR_NUMBER_SIZE)]

    for noise_type in NOISE_TYPES:
        mean_errors = [[] for _ in range(SENSOR_NUMBER_SIZE)]
        std_errors = [[] for _ in range(SENSOR_NUMBER_SIZE)]

        for snr in SNR_RATIO_DB:
            current_errors = [[] for _ in range(SENSOR_NUMBER_SIZE)]
            for i in range(num_iterations):
                first_break_samples_with_snr = [sensor_data.first_break_time for sensor_data in full_picking_algorithm(
                    sensors_data=sensors_data_dict['data'],
                    sensors_sample_rate=sensors_sample_rate,
                    sensors_geometry_data=sensors_data_dict['geometry'],
                    sensors_length=SENSOR_NUMBER_SIZE, noise_type=noise_type, snr_db=snr)]

                errors = [first_break_samples_with_snr[i] - true_first_break_samples[i] for i in range(len(first_break_samples_with_snr))]
                for sensor_num in range(SENSOR_NUMBER_SIZE):
                    current_errors[sensor_num].append(errors[sensor_num])

            for sensor_num in range(SENSOR_NUMBER_SIZE):
                mean_error = np.mean(current_errors[sensor_num])
                std_error = np.std(current_errors[sensor_num])
                mean_errors[sensor_num].append(mean_error)
                std_errors[sensor_num].append(std_error)

            print(f"SNR: {snr:5.1f} dB | Mean Error: {mean_error:6.2f} samples | Std Dev: {std_error:6.2f} samples")

        for i in range(SENSOR_NUMBER_SIZE):
            results[i][noise_type] = {'mean': np.array(mean_errors[i]), 'std': np.array(std_errors[i])}

    return results


def full_picking_algorithm(sensors_data, sensors_geometry_data,
                           sensors_length, sensors_sample_rate, noise_type="", snr_db=2):
    """
    One variation of the algorithm that use: 1) STA/LTA 2) AIC picker 3)cross correlation .
    on the first sensor data and used it for the other sensors.
    The function can add noises to the cleaning signal and show the seismogram.
    Comment: The function can use only the STA/LTA  + AIC picker without the cross correlation, for each sensor.
    """
    assert sensors_length, "Sensors data is empty!"
    sensors_list, signal_pattern = [], None

    for sensor_num in range(sensors_length):
        temp_sensor_obj = SensorObj(data=sensors_data[sensor_num],
                                    sampling_rate=sensors_sample_rate,
                                    geometry_location=sensors_geometry_data[sensor_num])
        if sensor_num == 0: #Used the same first-break signal pattern for all the sensors?
            first_break_frame, end_break_frame = temp_sensor_obj.find_break_range(**STA_LTA_PARAMS)
            first_break_frame = int(aic_pick(temp_sensor_obj.data[first_break_frame:end_break_frame]))
            signal_pattern = temp_sensor_obj.data[first_break_frame:end_break_frame]
            print(f"{sensor_num + 1} - [{first_break_frame}:{end_break_frame}]")

        if noise_type:
            temp_sensor_obj.add_noise(snr_db=snr_db, noise_type=noise_type)

        correlation_result = temp_sensor_obj.cross_correlation(signal_pattern)
        temp_sensor_obj.first_break_time = np.argmax(correlation_result) / sensors_sample_rate
        print("Sensor number: {} \n The first break is in: {}".format(sensor_num + 1, temp_sensor_obj.first_break_time))
        sensors_list.append(temp_sensor_obj)

    return sensors_list

def full_picking_algorithm2(sensors_data, sensors_geometry_data,
                           sensors_length, sensors_sample_rate, noise_type="", snr_db=2):
    """
    One variation of the algorithm that use: AIC picker and cross correlation on the first
    sensor data and used it for the other sensors.
    The function can add noises to the cleaning signal and show the seismogram.
    Comment: The function can use only the AIC picker without the cross correlation, for each sensor.
    """
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

        if noise_type: #Used the same first-break signal pattern for all the sensors?
            temp_sensor_obj.add_noise(snr_db=snr_db, noise_type=noise_type)

        correlation_result = temp_sensor_obj.cross_correlation(signal_pattern)
        temp_sensor_obj.first_break_time = np.argmax(correlation_result) / sensors_sample_rate
        print("Sensor number: {} \n The first break is in: {}".
              format(sensor_num + 1, temp_sensor_obj.first_break_time))
        sensors_list.append(temp_sensor_obj)

    return sensors_list