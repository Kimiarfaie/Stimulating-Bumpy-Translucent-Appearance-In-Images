from PIL import Image
from PIL import ImageDraw
import numpy as np
import os
import math
import params as prm

def max_contrast_sensitivity_ratio() -> float:
    max_ratio = 1.0
    for f in range(0, 255):
        w = (prm.A_K + prm.A_a * (f ** prm.A_c)) * (math.e ** (-1 * prm.A_b * f)) / prm.A_K
        if max_ratio < w:
            max_ratio = w
    return max_ratio

def modulation_gray(filename):
    img, _, _ = Image.open("./img2/" + filename).convert(prm.color_space).split()
    f_xy = np.asarray(img)
    f_uv = np.fft.fft2(f_xy)
    shifted_f_uv = np.fft.fftshift(f_uv)
    x_pass_filter = Image.new(mode="L", size=(shifted_f_uv.shape[0], shifted_f_uv.shape[1]), color=0)
    draw = ImageDraw.Draw(x_pass_filter)
    center = (shifted_f_uv.shape[0] // 2, shifted_f_uv.shape[1] // 2)
    ellipse_pos = (center[0] - prm.outside_r, center[1] - prm.outside_r, center[0] + prm.outside_r, center[1] + prm.outside_r)
    draw.ellipse(ellipse_pos, fill=255)
    ellipse_pos = (center[0] - prm.inside_r, center[1] - prm.inside_r, center[0] + prm.inside_r, center[1] + prm.inside_r)
    draw.ellipse(ellipse_pos, fill=0)
    filter_array = np.asarray(x_pass_filter)

    # output
    out_dir = "./results/" 
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Method 1
    gray_signal = []
    shifted_f_uv_ms = shifted_f_uv.copy()
    for f in prm.scalefactor:
        for j in range(filter_array.shape[0]):
            for i in range(filter_array.shape[1]): #This filter has binary values: 0 or 255
                if (filter_array[j][i] == 255):
                    shifted_f_uv_ms[j][i] = shifted_f_uv[j][i] * f
                else:
                    shifted_f_uv_ms[j][i] = shifted_f_uv[j][i]
        unshifted_f_uv = np.fft.fftshift(shifted_f_uv_ms) #Changes are done in the Fourier-domain, and now we are inverting to save the image
        i_f_xy = np.fft.ifft2(unshifted_f_uv).real
        gray_signal.append((Image.fromarray(i_f_xy).convert("L"), "{:.2f}".format(f), 1))

    # Method 2
    #filter_array_cont = np.zeros(shape=(shifted_f_uv.shape[0], shifted_f_uv.shape[1]), dtype=np.float32)
    #center = (filter_array_cont.shape[0] // 2, filter_array_cont.shape[1] // 2)
    #angle = 3.416
    #max_f_ratio = max_contrast_sensitivity_ratio()
    #for rate in prm.scalefactor:
     #   for j in range(filter_array_cont.shape[1]):
      #      for i in range(filter_array_cont.shape[0]):
       #         f = math.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2) / angle
        #        if rate > 1.0:
         #           w = (prm.A_K + prm.A_a * (f ** prm.A_c)) * (math.e ** (-1 * prm.A_b * f)) / prm.A_K
          #          filter_array_cont[j][i] = w
           #         reg_ratio = (w - 1.0 / max_f_ratio - 1.0) * (rate - 1.0) + 1.0
            #    else:
             #       _rate = 1.0 + (1.0 - rate)
              #      w = (prm.A_K + prm.A_a * (f ** prm.A_c)) * (math.e ** (-1 * prm.A_b * f)) / prm.A_K
               #     filter_array_cont[j][i] = w
                #    reg_ratio = 1.0 / ((w - 1.0 / max_f_ratio - 1.0) * (_rate - 1.0) + 1.0)
                #if filter_array_cont[j][i] >= 1.0 and filter_array[j][i] == 255:
                 #   shifted_f_uv_ms[j][i] = shifted_f_uv[j][i] * reg_ratio
                #else:
                #    shifted_f_uv_ms[j][i] = shifted_f_uv[j][i]
        #unshifted_f_uv = np.fft.fftshift(shifted_f_uv_ms)
        #i_f_xy = np.fft.ifft2(unshifted_f_uv).real
        # 平均輝度の差分を加算する ----------------------
        #src_mean = f_xy.mean()
        #edited_mean = i_f_xy.mean()
        #i_f_xy = i_f_xy + (src_mean - edited_mean)
        # -----------------------------------------------
        #gray_signal.append((Image.fromarray(i_f_xy).convert("L"), "{:.2f}".format(rate), 2))

    return gray_signal

def modulation_color_using_gray(filename, gray) -> None:
    _, cb, cr = Image.open("./img2/" + filename).convert(prm.color_space).split()

    out_dir = "./results/" 
    image_base_name = os.path.splitext(filename)[0]

    for (signal, string, method) in gray:
        out = Image.merge(prm.color_space, (signal, cb, cr)).convert("RGB") #Signal is modulated Y component
    #    if method == 1:
    #        out.save(out_dir + "method1/" + string + ".png")
    #    else:
    #        out.save(out_dir + "method2/" + string + ".png")
        if method == 1:
            out.save(out_dir + f"{image_base_name}_method1_{string}.png")
        else:
            out.save(out_dir + f"{image_base_name}_method2_{string}.png")

if __name__ == "__main__":
    files = os.listdir("./img2")
    #files = ["1.png","2.png","4.png","5.png","6.png","7.png","8.png","9.png","11.png","12.png","13.png","14.png","15.png","16.png","17.png","19.png","21.png","24.png","29.png","30.png","31.png","32.png","34.png","35.png","36.png","38.png","39.png","41.png", "42.png","43.png","44.png","45.png","46.png","48.png","50.png","51.png","52.png","53.png","54.png","58.png","59.png","60.png"]
    files =["1.png","2.png","3.png","4.png","5.png","6.png","7.png","8.png","9.png","10.png","11.png","12.png", "13.png","14.png","15.png","16.png","17.png","18.png","19.png"]
    for file in files:
        print(file)
        gray = modulation_gray(file)
        modulation_color_using_gray(file, gray)