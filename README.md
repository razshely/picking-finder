# picking-finder
Algorithm to find first break picking in a varied audio data.
### images - directory
Directory images contain the graph results for the exercise.

1) iperformance analysis directory: This is the main and final dir that conatin: (Ricker STA-LTA and AIC without CC is unrelevant)
   1) Ricker STA-LTA + AIC + CC directory: That contain the graphs of algorithm performance studies for error detected as a function of SNR for         the algorithm, for the 'simulation_ricker.mat' data.
   2) continuous STA-LTA + AIC + CC directory: That contain the graphs of algorithm performance studies for error detected as a function of SNR         for the algorithm, for the 'simulation_continuous.mat' data.
   3) seismograms directory: That contains the all seismogram graphs for the all relevant data + type noises + SNr ratio. (The seismogram of             the bonus 'simulation_multisource.mat' contain there either.
2) iq1 directory: Contain the time domain graph picture of the all sensors for the 'simulation_ricker.mat' file, and seismgorams of STA/LTA + cross correlation.
3) iq2 directory:  Contain the time domain graph picture of the all sensors for the 'simulation_continuous.mat' file, and seismgorams of STA/LTA + cross correlation
4) iq3 directory: Contain 2 directories: 1.white noise 2.pink noise.
                   Both of them contains time domain graphs with the noises + seismograms according to the relevant SNR ratio.
5) iq4 directory: Contain the time domain graph picture of the all sensors for the 'simulation_multisource.mat' and their frequency domain + spectrograms.

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
