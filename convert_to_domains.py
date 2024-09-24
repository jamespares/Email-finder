import re

def extract_domain(url):
    # Extract the domain from the URL
    domain = re.search(r'://(www\.)?([^/]+)', url)
    return domain.group(2) if domain else None

def convert_websites_to_domains(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            parts = line.strip().split(',')
            if len(parts) == 3:
                url = parts[2]
                domain = extract_domain(url)
                if domain:
                    outfile.write(domain + '\n')

if __name__ == "__main__":
    convert_websites_to_domains('websites.txt', 'domains.txt')