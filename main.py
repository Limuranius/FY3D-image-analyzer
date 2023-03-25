import vars
from FY3DImageManager import FY3DImageManager
import logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s\t%(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    )
    manager = FY3DImageManager(vars.CONFIG_PATH)
    manager.save_colored_images()
    manager.analyze_images()


if __name__ == "__main__":
    main()