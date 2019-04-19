from PIL import Image
import hitherdither
import numpy as np


class Config:
    def __init__(self, widthheightratio=1.307, outputpixelWidth=133, outputpixelHeight=114):
        self.widthheightratio = widthheightratio
        self.outputpixelWidth = outputpixelWidth
        self.outputpixelHeight = outputpixelHeight


def apply_brightness_contrast(input_img, brightness=0, contrast=0, threshhold=0):
    if brightness:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        def brightness_func(c):
            return c * (highlight - shadow) / 255 + shadow

        buf = input_img.point(brightness_func)
    else:
        buf = input_img

    if contrast:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))

        def contrast_func(c):
            return c * f + 127 * (1 - f)

        buf = buf.point(contrast_func)

    ## set threshold from 0 to 127
    if threshhold:
        f = threshhold

        def threshold_func(c):
            if c > 256 - f:
                return 256
            if c < f:
                return 0
            return c

        buf = buf.point(threshold_func)
    return buf


def maketoratio(imgin, config):
    img = imgin
    width, height = img.size
    widthheightratio = config.widthheightratio
    outputpixelWidth = config.outputpixelWidth
    outputpixelHeight = config.outputpixelHeight
    newheight = int(height * widthheightratio)
    maxsize = (outputpixelWidth, outputpixelHeight)
    img = img.resize((width, newheight))
    img.thumbnail(maxsize, Image.BICUBIC)
    realwidth, realheight = img.size
    return (img, realwidth, realheight)


def change_all_of_the_1st_color_to_the_second_color(im, ori_color, replace_color):
    ### oricolor should be a tuple of rgb
    ###replace
    imgnew = im.convert('RGB')
    data = np.array(imgnew)

    red, green, blue = data.T

    ori = (red == ori_color[0]) & (green == ori_color[1]) & (blue == ori_color[2])
    # print(data)
    ##changr
    data[...][ori.T] = replace_color
    # data[...,:-1][ori.T]=(0,255)
    # print( data[...])
    a = Image.fromarray(data)
    # a.show()
    return a


def AutoGenerate(inputpath='static/img/importfile.jpg', outputpath='static/trans/outputfile.bmp', threshhold=0,
                 brightness=0, contrast=0, widthheightratio=1, outputpixelWidth=150, outputpixelHeight=250):
    im = Image.open(inputpath)

    # Image.offset(xoffset, yoffset=None)
    ### ONLY if I use InmageEnhancer plugin: Should not use this la
    # enhancer = ImageEnhance.Contrast(im)
    # # factor from 0 to 1 0 will decrease
    # # as inputs are -100 to 100 so have to change to 0 to 1for negative and 1  to 11 for positive
    # contrast_factor = (contrast+100)/100 if contrast<=0  else (contrast+1)
    # im = enhancer.enhance(contrast_factor)

    my_config = Config(widthheightratio, outputpixelWidth, outputpixelHeight)

    (im, realwidth, realheight) = maketoratio(im, my_config)
    # im.show()
    ##Use this instead : I developed my own contrast function
    im = apply_brightness_contrast(im, contrast=contrast, brightness=brightness, threshhold=threshhold)

    # maxsize = (outputpixelWidth, outputpixelHeight)
    # im.thumbnail(maxsize,Image.BICUBIC)
    # change to black and white CANCELLED
    # im = im.convert('L')
    # define the pallete to differ
    palette = hitherdither.palette.Palette.create_by_median_cut(im, n=4)
    ## I dont know why bu this will return 4 color
    ## the one below will slice the strongest color away
    palette = hitherdither.palette.Palette(palette.colours[0:3])
    # print(palette.colours)

    # palette = hitherdither.palette.Palette(
    # [0x000000, 0xFFFFFF, 0x666666]
    # )
    ###

    # hitherdither.palette.Palette.create_PIL_png_from_rgb_array(palette).show()

    # print(palette.colours)
    # img_dithered = hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(im, palette, order=8)
    img_dithered = hitherdither.diffusion.error_diffusion_dithering(im, palette, 'floyd-steinberg', 2)

    # print(hitherdither.palette._get_all_present_colours(img_dithered))
    # ### *** threshold are from 0 to 127
    # im = im.convert('1')
    # im = im.convert('L')
    # img_dithered.show()
    a = tuple(map(tuple, palette.colours))
    # print(a[0])
    show_color = ((0, 0, 0), (127, 127, 127), (255, 255, 255))
    # print(show_color[0])
    img_change_color = img_dithered
    for i in range(3):
        img_change_color = change_all_of_the_1st_color_to_the_second_color(img_change_color, a[i], show_color[i])

    # img_change_color.show()
    # img_change_color.show()
    img_change_color.save(outputpath)
    return (True, realwidth, realheight, widthheightratio)

