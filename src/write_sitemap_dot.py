import os, sys

from site_data import Site
from template_loader import render_template, sanatize_name

if __name__ == '__main__':

    try:
        site_data_path, output_path = sys.argv[1:]
    except:
        print("USAGE ERROR: write_sitemap_dot.py site_data.yml output.dot")
        sys.exit(1)

    data = Site.load(site_data_path)

    # Load template
    src = render_template('sitemap.dot',
        data = data,
        sn = sanatize_name)

    # Render template
    print("Writing " + output_path)
    with open(output_path, 'w') as fh:
        fh.write(src)
