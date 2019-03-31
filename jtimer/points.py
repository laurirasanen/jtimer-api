import math


def calc_points(wr_time, pr_time, completions):
    """Tom "Tim" Sinister's point weight scaling algorithm"""
    wr_points = 200 * (5 + math.log(completions))
    scale_factor = wr_time / (wr_time + (pr_time - wr_time) * math.log(completions))
    points_awarded = round(wr_points * scale_factor)
    return points_awarded
