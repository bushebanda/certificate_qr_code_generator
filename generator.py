from argparse import ArgumentParser
import io
import os

import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("arial.ttf", size=13)


def generate_signature(name: str) -> Image.Image:
    global font
    
    image = Image.new("RGB", (150, 20), color=("#FFFFFF"))

    draw_text = ImageDraw.Draw(image)
    draw_text.text((10, 4), name, font=font, fill=("#000000"))

    return image


def fetch_qr_code(id_certificate: str) -> Image.Image:
    response = requests.get(
        f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=;{id_certificate}?"
    )
    buffer = io.BytesIO(response.content)
    return Image.open(buffer)


def generate_qr(id_certificate: str, name: str) -> Image.Image:
    signature_image = generate_signature(name)
    qr_image = fetch_qr_code(id_certificate)
    
    signature_width, signature_height = signature_image.size
    qr_width, qr_height = qr_image.size
    max_width = max(signature_width, qr_width)
    
    result_image = Image.new("RGB", (max_width, signature_height + qr_height))
    result_image.paste(signature_image, ((max_width - signature_width) // 2, 0))
    result_image.paste(qr_image, ((max_width - qr_width) // 2, signature_height))
    
    return result_image


def remove_special_symbols(text: str) -> str:
    def is_allowed(char: str) -> bool:
        return char.isalnum() or char in ("-", "_", " ")
    
    return "".join(filter(is_allowed, text))


def main(input_file: str, output_folder: str):
    df = pd.read_excel(input_file)
    os.makedirs(output_folder, exist_ok=True)
    
    size = len(df)
    
    for i, row in df.iterrows():
        id_certificate = str(row["id_certificate"])
        name =  str(row["name"])
        department = str(row["department"])
        qr_image = generate_qr(
            id_certificate,
            name
        )
        image_name = f"{remove_special_symbols(name)} - {remove_special_symbols(department)}.png"
        qr_image.save(os.path.join(output_folder, image_name))
        
        print(f"[{i+1}/{size}]: {name}")


if __name__ == "__main__":
    parser = ArgumentParser("Certificate QR code generator")
    parser.add_argument(
        "--input_file",
        type=str,
        default="id_certificate.xlsx",
        help="certificate descritption file with columns: id_certificate, name, department",
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="certificates",
        help="folder to save generated certificates",
    )
    args = parser.parse_args()

    main(args.input_file, args.output_folder)
