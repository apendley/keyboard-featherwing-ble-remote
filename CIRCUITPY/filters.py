############################################################
# Adapted from https://dlbeer.co.nz/articles/tsf.html
############################################################
def cmp_swap(arr, i, j):
    if arr[i] > arr[j]:
        arr[i], arr[j] = arr[j], arr[i]

# Simple median filter
class MedianFilter:
    def __init__(self):
        self._samples = [0] * 5

    def __call__(self, x, reset):
        if reset:
            self._samples = [x] * 5
            return x
        else:
            self._samples.pop(0)
            self._samples.append(x)

            # https://en.wikipedia.org/wiki/Sorting_network#Optimal_sorting_networks
            sorted_samples = self._samples[:]
            cmp_swap(sorted_samples, 0, 1)
            cmp_swap(sorted_samples, 2, 3)
            cmp_swap(sorted_samples, 0, 2)
            cmp_swap(sorted_samples, 1, 4)
            cmp_swap(sorted_samples, 0, 1)
            cmp_swap(sorted_samples, 2, 3)
            cmp_swap(sorted_samples, 1, 2)
            cmp_swap(sorted_samples, 3, 4)
            cmp_swap(sorted_samples, 2, 3)

        return sorted_samples[2]

# Infinite impulse response filter
# https://en.wikipedia.org/wiki/Infinite_impulse_response
class IIRFilter:
    def __init__(self, N, D):
        self._N = N
        self._D = D
        self._s = 0

    def __call__(self, x, reset=False):
        if reset:
            self._s = x
            return x

        self._s = (self._N * self._s + (self._D - self._N) * x + self._D // 2) // self._D
        return self._s

# Combine median and IIR filter into a combined channel filter
class ChannelFilter:
    def __init__(self, N, D):
        self._median_filter = MedianFilter()
        self._iir_filter = IIRFilter(N, D)

    def __call__(self, x, reset=False):
        median_value = self._median_filter(x, reset)
        return self._iir_filter(median_value, reset)

# Filters a 2D point. Useful for touchscreen and other 2D point/vector filtering.
class XYSampleFilter:
    def __init__(self, N, D):
        self._x_filter = ChannelFilter(N, D)
        self._y_filter = ChannelFilter(N, D)

    def __call__(self, x, y, reset=False):
        filtered_x = self._x_filter(x, reset)
        filtered_y = self._y_filter(y, reset)
        return (filtered_x, filtered_y)
