from PIL import Image
import parser
from generator import create_factions_configuration

def main():

    REGION_AMOUNT = 5

    with open("../input/descr_regions.txt", "r") as f:
        regions_data = f.read()
    with open("../input/descr_names.txt", "r") as f:
        names_data = f.read()
    with open("../input/descr_strat.txt", "r") as f:
        campaign_text = f.read()

    with Image.open("../input/map_regions.tga") as img:
        region_map = img.convert("RGB")

    regions = parser.parse_regions(regions_data)
    parser.parse_settlement_coordinates(region_map, regions)
    names = parser.parse_names(names_data)
    
    #should be text returned
    campaign_setup = create_factions_configuration(regions, names, 5)

    
    
if __name__ == "__main__":
        main()