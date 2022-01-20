import time
from selenium import webdriver
import warnings

warnings.filterwarnings("ignore")

DRIVER = "~/path/to/your/chrome/driver/"
driver = webdriver.Chrome(DRIVER)

BASE = "https://www.senato.it/"
NUM_LEGISTLATURES = 18


FILENAME = "../data/it-parliamentary-groups-senate.txt"


def get_legislature_urls(base):
    """
    Returns list of urls pointing to legislature webpages.
    """
    urls = []
    base = base + "/leg/"
    for leg in range(1, NUM_LEGISTLATURES + 1):
        leg = str(leg)
        if len(leg) < 2:
            leg = "0" + leg
        leg_url = f"{base}{leg}/BGT/Schede/GruppiStorici/Grp.html"
        urls.append(leg_url)
    return urls


def get_group_urls(legis_url):
    """
    Returns list of urls pointing to parliamentary group webpages for a specific legislature.
    """
    group_urls = []
    driver.get(legis_url)  # go to legislature url
    groups = driver.find_elements_by_xpath("//td/a")
    for group in groups:
        group_url = group.get_attribute("href")
        group_urls.append(group_url)
    time.sleep(2)
    return group_urls


def get_group_data(group_url):
    """
    Returns a group id (string) and a list containing the memebers' names
    """
    driver.get(group_url)
    group = driver.find_elements_by_tag_name("h1")[1].text.split(" ")
    if not group[0]:
        group = driver.find_elements_by_tag_name("h1")[2].text.split(" ")
    group = " ".join(group[1:])

    group_members = driver.find_elements_by_xpath("//td/a")
    group_members = [m.text for m in group_members]
    time.sleep(2)
    return group, group_members


def write_hypergraph(
    data, filename, n_sep=",", col_sep=";",
):
    """
    Writes data to text file.
    Each line represents an hyperedge.
    Columns (name, nodes) are separated by a semicolon.
    Nodes are separated by a colon.
    """
    with open(filename, "w") as out_file:
        out_file.write("name" + col_sep + "nodes\n")

        for hyperedge, node_list in data.items():
            line = hyperedge + col_sep + n_sep.join(node_list) + "\n"
            out_file.write(line)


def main():
    data = dict()

    legis_urls = get_legislature_urls(BASE)

    for legis_url in legis_urls:
        group_urls = get_group_urls(legis_url)
        for group_url in group_urls:
            group, group_members = get_group_data(group_url)
            group += "-" + legis_url[27:29]  # add legislature id
            print("Scraped members of", group, "successfully!")
            data[group] = group_members

    write_hypergraph(data, FILENAME)
    print(f"Successfully saved data as {FILENAME}!")

