DATA_FILES = [
    r"C:\dev\picking-finder\data\simulation_ricker.mat",
    "C:\dev\picking-finder\data\simulation_continuous.mat",
    "C:\dev\picking-finder\data\simulation_multisource.mat"
]
SENSOR_NUMBER_SIZE = 64
SNR_RATIO_DB = [x for x in range(-5,15)]
NOISE_TYPES = ["white", "pink"]
STA_LTA_PARAMS = {'sta_group_size': 30, 'lta_group_size': 90, 'threshold': 1.75}
"""
-) -10 dB to 0 dB: This represents a challenging environment where the noise power is equal to or greater than the signal power. 
It's crucial for testing the robustness and lower limits of your algorithm.

-) 0 dB to 10 dB: This is a moderately noisy range. Signals are detectable but still require effective noise suppression. 
Many real-world seismic recordings fall into this category.

-) 10 dB to 20 dB: This represents a relatively clean signal. Testing in this range confirms your algorithm works 
correctly under ideal conditions and establishes a performance baseline.
"""
