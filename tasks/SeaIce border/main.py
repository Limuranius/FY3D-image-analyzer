from OptimizerVisualizer import OptimizerVisualizer
from database import FY3DImageArea

ids = [8917, 8918, 8919, 8920]
CHANNEL = 8


areas = [FY3DImageArea.get(id=area_id).get_channel_area(CHANNEL) for area_id in ids]

o = OptimizerVisualizer(areas, CHANNEL)

# o.optimize_cut_borders()
# o.validate_approximations()
o.calculate_individual_coefficients()
o.calculate_common_coefficients()
o.save_individual_approximation()
o.save_common_approximation()
o.save_indiv_coeffs()
