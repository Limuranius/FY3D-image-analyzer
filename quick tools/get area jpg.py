import FY3DImage


img_path = r"C:\Users\Gleb\Desktop\Диплом\Снимки со спутников\2020\FY3D_MERSI_GBAL_L1_20200320_2345_1000M_MS.HDF"
output_path = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\quick tools\area img"
img = FY3DImage.FY3DImage(img_path)
# x1, y1, x2, y2 = 725, 988, 790, 1036
x1, y1, x2, y2 = 530, 719, 680, 883


area = img.get_area(x1, y1, x2-x1, y2-y1)
area.save_channels_img_to_dir(output_path)