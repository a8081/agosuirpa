import os
import tools.generic_utils as util
from tools.database import create_connection, select_variations_by, create_variation

def generate_screenshot_demo(args):
    '''
    Generate an image name as string with an extension png
    '''
    # Random number and the extension with a img identification
    generate_path = args[0]
    number = args[1]
    return generate_path+str(number)+"_img.png"

def generate_capture(columns_ui,columns,element,acu,generate_path,attr,case, activity, variant):
    '''
    Generate row reading the json
    args:
        dict: json with the trace
        acu: number of the case
        variante: if use the initial value or the generate
    '''    
    actual_path = os.getcwd()
    capture_path= element["initValue"]
    args_tmp = element["args"]
    args = [generate_path,acu]
    new_image = generate_screenshot_demo(args)
    try:
        for i in columns_ui:
            try:
                arguments = []
                if i in columns:
                    ind_text = columns.index(i)
                    content = attr[ind_text]
                    arguments.append(content)
                if i in args_tmp:
                    func = args_tmp[i]
                    for j in func:
                        if element is not None:
                            coordinates = j["coordinates"]
                            name = j["name"]
                            args = j["args"]
                            if os.path.exists(actual_path+"\\"+new_image):
                                capture_path=new_image
                            arguments.append(args)
                            arguments.append(new_image)
                            arguments.append(capture_path)
                            arguments.append(coordinates)
                            if "dependency" in j:
                                con = create_connection()
                                dependant_row = select_variations_by(con, case, j["dependency"]) # fetch a list
                                arguments.append(dependant_row[0][4])
                                
                            image_element = util.detect_function(name)(arguments)
                            if type(image_element) == str:
                                create_variation(None, case, activity, variant, name, image_element)
                        else:
                            new_image="NaN"
                        arguments = []
            except:
                arguments = []
    except:
        new_image = "NaN"
    return new_image