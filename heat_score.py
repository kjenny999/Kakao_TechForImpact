def heat_score(utci, heat, shade, wind, w):
    return (
        w["utci"] * utci +
        w["heat"] * heat -
        w["shade"] * shade -
        w["wind"] * wind
    )