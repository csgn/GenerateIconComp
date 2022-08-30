import os
import sys
import argparse

COMPONENT_TEMPLATE = """
export default function {0}({{ width, height, fill, stroke, strokeWidth, linecap, linejoin }}) {{
    return (
        <>
            {1}
        </>
    )
}}
"""

def make_interpolation(components_metadata):
    def getElem(from_, filter_):
        element = list(filter(lambda x: filter_ in x, from_))[0]
        index = from_.index(element)

        return element, index

    def getInterpolation(element, set_):
        element = element.split("=")
        value = element[1].replace('"', '')

        return f"{{{set_} ?? '{value}'}}"

    interpolated = []

    for component in components_metadata:
        name, componentName, fileName, file = component.values()
        parts = file.split(" ")
        parts = parts[1:]
        parts[-1] = parts[-1].split("/>")[0]

        stroke_e, stroke_i = getElem(parts, "stroke=")
        fill_e, fill_i = getElem(parts, "fill=")
        width_e, width_i = getElem(parts, "width=")
        height_e, height_i = getElem(parts, "height=")
        strokeWidth_e, strokeWidth_i = getElem(parts, "stroke-width=")
        strokeLinecap_e, strokeLinecap_i = getElem(parts, "stroke-linecap=")
        strokeLinejoin_e, strokeLinejoin_i = getElem(parts, "stroke-linejoin=")

        parts[stroke_i] = "stroke=" + getInterpolation(stroke_e, "stroke")
        parts[fill_i] = "fill=" + getInterpolation(fill_e, "fill")
        parts[width_i] = "width=" + getInterpolation(width_e, "width")
        parts[height_i] = "height=" + getInterpolation(height_e, "height")
        parts[strokeWidth_i] = "stroke-width=" + getInterpolation(strokeWidth_e, "strokeWidth")
        parts[strokeLinecap_i] = "stroke-linecap=" + getInterpolation(strokeLinecap_e, "linecap")
        parts[strokeLinejoin_i] = "stroke-linejoin=" + getInterpolation(strokeLinejoin_e, "linejoin")

        new_parts = "<svg " + " ".join(parts) + "/></svg>"
        component["inner"] = new_parts
        interpolated.append(component)

    return interpolated



def generate_component_metadata(path, icons):
    metadata = []

    for icon in icons:
        parts = icon.split('.svg')[0].split('-')
        name = parts[0].title() + ''.join(x.title() for x in parts[1:])

        with open(path + icon, 'r') as f:
            file = f.read()

        metadata.append({
            "name": name,
            "componentName": name + "Icon",
            "fileName": name + ".Icon.jsx",
            "file": file,
        })

    return metadata


def generate(interpolated_components, dest):
    def generate_component(component):
        componentName = component.get("componentName")
        innerValue = component.get("innerValue")
        fileName = component.get("fileName")
        with open(dest + fileName, "w") as f:
            s = COMPONENT_TEMPLATE.format(componentName, innerValue)
            f.write(s)


    with open(dest + "index.js", "w") as f:
        for component in interpolated_components:
            f.writelines(f"export {{default as {component['componentName']}}} from '{component['fileName'].split('.jsx')[0]}';\n")
            generate_component(component)


def main(args):
    try:
        os.mkdir(args.dest)
    except:
        print("Destination is not created!")
        sys.exit(1)

    icons = os.listdir(args.icons)
    valid_icons = [icon for icon in icons if ".svg" in icon]

    components_metadata = generate_component_metadata(args.icons, valid_icons)
    interpolated_components = make_interpolation(components_metadata)

    try:
        generate(interpolated_components, args.dest)
    except:
        print("FAILED: generation is not successfull")
        sys.exit(1)

    print("SUCCESS: generation is successfull")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--icons", type=str, help="path of icons")
    parser.add_argument("--dest", type=str, help="path of destination")
    args = parser.parse_args()

    main(args)
