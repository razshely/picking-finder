# picking-finder
Tool for find picking in a varied audio data
### Example Use:



#### Example use of the questions123 function
    for snr_db, noise_type in product([-5,0,5,10,15],['white','pink']):
       questions123(data_file_path=DATA_FILES[1], noise_type=noise_type, snr_db=snr_db,plot_title="Seismogram for continuous data\n For: STA/LTA + AIC picker + Cross-correlation\nSNR ratio: {} and nosie: {}".format(snr_db, noise_type))


#### Example use of the performance analysis function
    res = run_performance_analysis(data_file_path=DATA_FILES[0], num_iterations=100)
    for i in range(len(res)):
        plot_performance_results(results=res, snr_range=SNR_RATIO_DB, sampling_rate=2000, sensor_index=i)

#### Example use of the bonus:

    questions4()

In the end of each element you will get the relevant graph!