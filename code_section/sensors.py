import numpy as np
from typing import Any
from scipy.signal import correlate, stft
from numpy import ndarray, dtype, float64


class SensorObj:
    """
    Class for sensor representing.
    This class have the all methods and attributes for find and analyze the sensors data.
    """
    def __init__(self, data, sampling_rate, geometry_location=[0, 0, 0]):
        self.data = (data - np.mean(data)) / np.std(data)
        self.sampling_rate = sampling_rate
        self.time = np.arange(len(data)) / sampling_rate
        self.geometry_location = geometry_location
        self.first_break_time = -1
        self.noise_type = None

    def _calculate_sta_lta(self, sta_group_size, lta_group_size) -> ndarray[tuple[Any, ...], dtype[float64]]:
        """
        Calculate STA/LTA according to the groups dividing the user enter.
        :return: STA/LTA.
        """
        sta = np.convolve(np.abs(self.data), np.ones(sta_group_size)/sta_group_size, mode='same')
        lta = np.convolve(np.abs(self.data), np.ones(lta_group_size)/lta_group_size, mode='same') + 1e-12
        return sta / lta

    def _find_first_break(self, ratio, threshold):
        """
        Function to find the start of break frame.
        The first index where ratio < threshold.
        :param ratio: STA/LTA.
        """
        first_break_frame = np.argmax(ratio > threshold)
        return first_break_frame

    def _find_end_break(self, ratio, first_break_frame, threshold, max_time=0.1):
        """
        Function to find the end of break frame, te function have two options:
        - first frame after onset where ratio < threshold
        - force offset = min(onset + max_time (s), data length)
        :param ratio: STA/LTA.
        :param max_time: argument for determine the maximum time for picking search
        """
        picking_parts = ratio[first_break_frame + 1:]
        end_break_frame = None

        if np.any(picking_parts < threshold):
            end_break_frame = first_break_frame + np.argmax(picking_parts < threshold) + 1

        max_gap = int(max_time * self.sampling_rate)
        if end_break_frame is None or (end_break_frame - first_break_frame) > max_gap:
            end_break_frame = min(first_break_frame + max_gap, len(ratio) - 1)

        return end_break_frame

    def find_break_range(self, sta_group_size=30, lta_group_size=90, threshold=1.75):
        """
        Function for calculating break range(first_break, end_break) in signals.
        :param lta_group_size: The group size for LTA calculation.
        :param sta_group_size: The group size for STA calculation.
        """
        ratio = self._calculate_sta_lta(sta_group_size, lta_group_size)
        first_break_frame = self._find_first_break(ratio=ratio,
                                                  threshold=threshold)
        end_break_frame = self._find_end_break(ratio=ratio,
                                              first_break_frame=first_break_frame,
                                              threshold=threshold/2)
        return first_break_frame, end_break_frame

    def cross_correlation(self, signal_pattern):
        """
        Cross-correlation between shorter signal x and longer signal y,
        returning only the valid alignments (len(y) - len(x) + 1 values).
        """
        assert len(self.data) >= len(signal_pattern), "The full data must be the longer then the signal"
        return correlate(self.data, signal_pattern, mode='valid')

    def add_noise(self, snr_db=2, noise_type="white") -> np.ndarray:
        """
        Add noise (white or pink) to a signal according to a given SNR.
        """
        self.noise_type = noise_type

        sig_power = np.mean(self.data ** 2)
        # SNR: convert dB → linear
        snr_linear = 10 ** (snr_db / 10)
        noise_power = sig_power / snr_linear

        if noise_type.lower() == "white":
            noise = np.random.normal(0, np.sqrt(noise_power), len(self.data))

        elif noise_type.lower() == "pink":
            # Pink noise via frequency-domain shaping (1/sqrt(f))
            white = np.random.normal(0, 1, len(self.data))
            fft_vals = np.fft.rfft(white)
            freqs = np.fft.rfftfreq(len(self.data), 1 / self.sampling_rate)
            fft_vals /= np.where(freqs == 0, 1, np.sqrt(freqs))  # scale by 1/sqrt(f)
            pink = np.fft.irfft(fft_vals, n=len(self.data))
            pink = pink / np.std(pink) * np.sqrt(noise_power)  # scale to match power
            noise = pink

        else:
            raise ValueError("noise_type must be 'white' or 'pink'")

        self.data += noise
        return self.data

    def time_to_frequency_domain(self):
        """
        Compute FFT magnitude spectrum on the time domain signal.

        Returns:
        frequency - Frequency bins for FFT.
        magnitude - Magnitude spectrum (one-sided).
        """
        fft_vals = np.fft.rfft(self.data)
        magnitude = np.abs(fft_vals) / len(self.data)
        frequency = np.fft.rfftfreq(len(self.data), 1 / self.sampling_rate)
        return frequency, magnitude

    def get_spectrogram_attribute(self, nperseg=256, noverlap=128):
        """
        Compute STFT spectrogram of time domain signal.
        nperseg : int
            Window size for STFT (default 256).
        noverlap : int
            Overlap between STFT windows (default 128).

        Returns:
        frequency - STFT frequency bins.
        time - STFT time bins.
        magnitude - STFT complex spectrogram.
        """
        frequency, time, magnitude = stft(self.data, fs=self.sampling_rate, nperseg=nperseg, noverlap=noverlap, boundary=None)
        return frequency, time, magnitude
