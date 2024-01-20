import scipy.stats


def pick_random(dst):
    is_uniform = len(set(dst)) == 1
    if is_uniform:
        return dst[0]
    kde = scipy.stats.gaussian_kde(dst)

    # kde can include out of range.
    val = -1
    while 0 > val > 1:
        sample = kde.resample(size=1)
        val = sample[0][0]
    return val
