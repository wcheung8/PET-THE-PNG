from PIL import Image, ImageFilter, ImageDraw


def makeTransparent(img):
    alpha = img.getchannel('A')

    # Convert the image into P mode but only use 255 colors in the palette out of 256
    img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)

    # Set all pixel values below 128 to 255 , and the rest to 0
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

    # Paste the color of index 255 and use alpha as a mask
    img.paste(255, mask)

    # The transparency index is 255
    img.info['transparency'] = 255

    return img


def makeGIF(path, offset=(0, 0), smoosh_factor=(0.075, 0.025), shake_factor=(1, 1)):
    gif = []
    for i in range(5):
        smoosh = min(5 - i, i)

        hand = Image.open('hand/{}.png'.format(i))
        target = Image.open(path)
        image = Image.new("RGBA", target.size)
        image.paste(target)

        w, h = hand.size

        new_w = int(w * (1 + smoosh_factor[0] * smoosh))
        new_h = int(image.size[1] * (w / image.size[0]) * (1 - smoosh_factor[1] * smoosh))

        image = image.resize((new_w, new_h), Image.LANCZOS)
        ImageDraw.floodfill(image, (0, 0), (255, 255, 255, 0), border=None)
        ImageDraw.floodfill(image, (image.size[0] - 1, 0), (255, 255, 255, 0), border=None)

        output = Image.new("RGBA", (112, 112))
        output.paste(image, ((112 - image.size[0]) // 2 - int(shake_factor[0] * smoosh) + offset[0],
                             112 - image.size[1] - int(shake_factor[1] * smoosh) + offset[1]))
        output.paste(hand, (0, 0), hand)
        output = makeTransparent(output)
        gif.append(output)

    gif[0].save('out.gif', save_all=True, append_images=gif[1:], optimize=False, duration=40, loop=0, disposal=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--png", type=str, default="chika.jpg")
    parser.add_argument("--offset", type=str, default="0,0")
    parser.add_argument("--smoosh_factor", type=str, default="0.075,0.025")
    parser.add_argument("--shake_factor", type=str, default="1,1")

    args = parser.parse_args()
    offset = [int(i) for i in args.offset.split(',')]
    smoosh_factor = [float(i) for i in args.smoosh_factor.split(',')]
    shake_factor = [float(i) for i in args.shake_factor.split(',')]

    assert len(offset) == len(smoosh_factor) == len(shake_factor) == 2

    makeGIF(args.png, offset, smoosh_factor, shake_factor)
