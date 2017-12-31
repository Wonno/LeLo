from lxml import html
import requests
import os
import os.path
import argparse
import json
import pathlib

LETSBUILD_URL = 'http://letsbuilditagain.com/instructions/'
LETSBUILD_IMAGES = '//*[@id="wrapper"]//section[@class="testimonial"]/div//img//@src'

LEGO_URL = 'https://www.lego.com/service/biservice/search?fromIndex=0&locale=de-DE&onlyAlternatives=false&prefixText='
LEGO_PLACEHOLDER_IMG = 'help-placeholder-product'


def readargs():
    parser = argparse.ArgumentParser(description='Downloader for LEGO building instructions.',
                                     epilog="Enjoy crafting again.")
    parser.add_argument('ids', metavar='1 23 456', type=int, nargs='+',
                        help='Lego Set IDs')
    parser.add_argument('--basedir', default='.',
                        help='destination directory for downloaded sets')
    parsed_args = parser.parse_args()
    return parsed_args


def letsbuilditagain_load(_dir, _product_id):
    id_url = LETSBUILD_URL + _product_id + '/'
    page = requests.get(id_url)

    if page.status_code != 200:
        raise ValueError("Set not found on letsbuilditagain.com " + _product_id)

    tree = html.fromstring(page.content)
    images = tree.xpath(LETSBUILD_IMAGES)

    dirname = prepare_dest_dir(_dir, _product_id)
    for image in images:
        image_file = image.replace("./", "")
        imageurl = id_url + image_file
        store_url(dirname, image_file, imageurl)


def store_url(dirname, filename, url):
    response = requests.get(url)
    print("Downloading", url)
    if response.status_code == 200:
        complete_name = os.path.join(dirname, filename)
        filename = open(complete_name, "wb")
        filename.write(response.content)
        filename.close()
    else:
        raise ValueError("Download not successfull: ", response.status_code, url)


def prepare_dest_dir(_dir, _product_id):
    dirname = os.path.realpath(os.path.join(_dir, _product_id))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname


def lego_load(_dir, _product_id):
    id_url = LEGO_URL + _product_id
    page = requests.get(id_url)
    response_json = json.loads(page.content)

    if 1 == response_json['totalCount']:
        pass
    else:
        raise ValueError("Set not found on lego.com " + _product_id)

    product = response_json['products'][0]
    product_image_url = product['productImage']
    product_name = product['productName']
    building_instructions = product['buildingInstructions']

    pdf_url = search_best_pdflink(building_instructions)

    dirname = prepare_dest_dir(_dir, _product_id)

    suffix = ".pdf"
    filename = _product_id + ' ' + product_name + suffix
    store_url(dirname, filename, pdf_url)

    if LEGO_PLACEHOLDER_IMG not in product_image_url:
        suffix = pathlib.Path(product_image_url).suffix
        filename = _product_id + ' ' + product_name + suffix
        store_url(dirname, filename, product_image_url)


def search_best_pdflink(building_instructions):
    pdf_url = None
    for buildingInstruction in building_instructions:
        description = buildingInstruction['description']
        pdf_url = buildingInstruction['pdfLocation']
        # search for A4 format
        if description.endswith("IN") or description.endswith("V29"):
            break

    if pdf_url is None:
        raise ValueError("PDF url not found.")

    return pdf_url


def check_dest_dir(basedir):
    if not os.path.exists(basedir):
        raise ValueError(basedir + "not existing.")
    if not os.access(basedir, os.W_OK):
        raise ValueError(basedir + "not writeable.")


if __name__ == "__main__":
    args = readargs()
    check_dest_dir(args.basedir)

    for product_id in args.ids:
        found = False
        prod_id = str(product_id)
        try:
            lego_load(args.basedir, prod_id)
            found = True
        except ValueError as err:
            print(err)
        except:
            print("Lego.com failed.")

        try:
            letsbuilditagain_load(args.basedir, prod_id)
            found = True
        except ValueError as err:
            print(err)
        except:
            print("letsbuilditagain.com failed")

        if not found:
            print("Could not download set id", product_id)
            exit(1)
