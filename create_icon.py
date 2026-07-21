from PIL import Image, ImageDraw, ImageFont


size = 512


img = Image.new(
    "RGBA",
    (size, size),
    (30, 30, 30, 255)
)


draw = ImageDraw.Draw(
    img
)


# Yuvarlak arka plan

draw.ellipse(
    (40, 40, 472, 472),
    fill=(0, 120, 212, 255)
)



# AI yazısı

try:

    font = ImageFont.truetype(
        "arial.ttf",
        150
    )

except:

    font = None



text = "AI"


bbox = draw.textbbox(
    (0,0),
    text,
    font=font
)


x = (size - (bbox[2]-bbox[0])) // 2
y = (size - (bbox[3]-bbox[1])) // 2



draw.text(
    (x,y),
    text,
    fill="white",
    font=font
)



# Kaydet

img.save(
    "icon.ico",
    sizes=[
        (256,256),
        (128,128),
        (64,64),
        (32,32),
        (16,16)
    ]
)


print(
    "icon.ico oluşturuldu"
)