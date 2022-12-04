"""
A python script for generating pictures related to 1 original image.
made by: Deniz Bicer
12/4/2022
"""
import openai as ai  # for image generation
from json import load  # to load the config file
from PIL import Image  # to resize the image
from io import BytesIO  # to convert the image to bytes

io = BytesIO()


def read_config():
    """
    expected config:
        output_size: widthxheight or width*height
        output_quantity: example -> 1, 2, 5, 10, 100
        save_images: True or False
    """
    with open("config.json") as f:
        data = load(f)
    return data


def generate(specs):
    ai.api_key = specs["api_key"]
    im = Image.open(specs["image_path"])
    # converts input from cpnfig to a tuple
    new_size = specs["output_size"].split("x")
    try:
        if "*" in new_size[0]:
            new_size = new_size[0].split("*")
    except:
        pass
    new_size = (int(new_size[0]), int(new_size[1]))

    if im.size != new_size:  # checks if the imnput file has the same size as the requested output file
        print("RESIZING")
        im = im.resize(new_size)
    im.save(io, "PNG")
    im_data = io.getvalue()  # converts the image to bytes
    data = ai.Image.create_variation(image=im_data, n=int(
        specs["output_quantity"]), size=f"{new_size[0]}x{new_size[1]}")  # generates the images
    return data


def main():
    order_details = {key: input(f"Please input {key}:").replace('"', "") if value == "" else value
                     for key, value in read_config().items()}  # loads the config file to a dict
    pics = generate(order_details)["data"]  # generates images
    if order_details["save_images"] == "True":
        print("SAVING IMAGES")
        from requests import get
        from shutil import copyfileobj
        i = 1
        for data in pics:  # loops through the images and tries to download them
            res = get(data["url"], stream=True)  # makes a request
            if res.status_code == 200:
                with open(f"output/{i}.png", "wb") as f:
                    copyfileobj(res.raw, f)
            else:
                print(
                    "Failed to retrieve the image, instead outputting the urls to the output folder.")
                with open(f"urloutput/{i}.txt", "w") as f:
                    f.write(data["url"])
            i += 1
    else:
        print("outputting image urls to the outputs folder.")
        i = 1
        for data in pics:
            with open(f"urloutput/{i}.txt", "w") as f:
                f.write(data["url"])
    print("Program executed successfully")


if __name__ == "__main__":
    main()
