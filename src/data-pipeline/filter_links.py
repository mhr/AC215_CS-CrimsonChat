import json


with open("/app/data/harvard_cs_links_by_depth_0.json", "r") as file:
    links_by_depth = json.load(file)
print(len(links_by_depth))

all_unique_links = set()

for depth, links in links_by_depth.items():
    unique_links = set(links) - all_unique_links
    all_unique_links.update(unique_links)
    print(f"Depth {depth}: {len(unique_links)} unique links")

print(f"Total unique links: {len(all_unique_links)}")


# # If you want to save the unique links back to a JSON file
# with open("data/harvard_cs_unique_links_deepest.json", "w") as file:
#     json.dump(list(all_unique_links), file, indent=4)


# with open("./data/unique_links_deepest.json", "r") as file:
#     urls = json.load(file)

unique_urls = set()

for url in all_unique_links:
    # Remove trailing slash if present
    normalized_url = url.rstrip("/")
    unique_urls.add(normalized_url)

urls = list(unique_urls)

unwanted_substrings = [
    ".hqx",
    "Pyret_Style_Guide",
    "mailto:",
    "#h.",
    ".key",
    ".rkt",
    ".pptx",
    ".ppt",
    ".pdf",
    "php#",
    ".gz",
    ".gif",
    "#",
    ".zip",
    ".png",
    ".jpg",
    ".ps",
    "login",
    "signin",
    ".py",
    ".sty",
    ".bib",
    ".shtml",
    "/images/",
    "/Videos",
    ".m",
    ".java",
    ".txt",
    ".tex",
    "/results/",
    "share=",
    "google.com/",
    "https://twitter.com/",
    "http://www.facebook.com/",
    ".doc",
    "binaries",
    ".tgz",
    "logout",
    "BorealisDemo",
    ".js",
    ".als",
    ".bz2",
    ".xlsx",
    ".dvi",
    ".plt",
    " ",
    ".swf",
    ".scm",
    "pyret",
    ".PDF",
    ".ppsx",
    ".git",
    "https://aizenberglab.seas.harvard.edu/media-gallery/detail",
    "Mailto:",
]

filtered_urls = [
    url for url in urls if all(unwanted not in url for unwanted in unwanted_substrings)
]

filtered_urls = list(set(filtered_urls))
filtered_urls.sort()
print(len(filtered_urls))

with open("/app/data/harvard_cs_filtered_links.json", "w") as file:
    json.dump(list(filtered_urls), file, indent=4)

with open("/app/gcp_static_data/harvard_cs_filtered_links.json", "w") as file:
    json.dump(list(filtered_urls), file, indent=4)
