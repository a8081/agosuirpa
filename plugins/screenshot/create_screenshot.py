import os
import agosuirpa.generic_utils as util
from experiments.models import Variations
from agosuirpa.generic_utils import detect_function
from agosuirpa.settings import sep, var_func_modify_properties
import json
from PIL import Image
import numpy as np
import ast

def manage_dependency(experiment, var_function_name, arguments, argumentsSave, screenshots_args, case, scenario, activity, variant, balanced, log_size, image_path_to_save, capture_path, coordinates, object_json_properties):
    if "args_dependency" in screenshots_args:
        dependant_row = Variations.objects.filter(experiment=experiment, case_id=case, scenario=scenario, balanced=balanced, log_size=log_size,
                                               activity=screenshots_args["args_dependency"]["Activity"], case_variation_id=screenshots_args["args_dependency"]["id"], variant=screenshots_args["args_dependency"]["V"]).order_by("id")
        row=dependant_row[len(dependant_row)-1]
        tmp = ast.literal_eval(row.arguments)
        arguments = tmp+arguments
        var_function_name = row.function_name
        if len(arguments) > 0:
            arguments[0].insert(0, row.result)
        else:
            arguments.append(row.result)
            
    process_info = {"variant": variant, "activity": activity, "object_json_properties": object_json_properties}
    arguments.append(process_info)
    
    if var_function_name in var_func_modify_properties:
        image_element, object_json_properties = util.detect_function(var_function_name)(arguments)
    else:
        image_element = util.detect_function(var_function_name)(arguments)
        
    if type(image_element) == str:
        Variations.objects.create(experiment=experiment, case_id=case, scenario=scenario, balanced=balanced, log_size=log_size,
                                  case_variation_id=screenshots_args["id"], activity=activity, variant=variant, function_name=var_function_name,
                                  arguments=argumentsSave, result=image_element, image_path_to_save=image_path_to_save,
                                  capture_path=capture_path, coordinates=coordinates)
    return image_element, object_json_properties

def generate_capture(experiment, columns_ui, columns, element, acu, case, generate_path, attr, activity, variant, attachments_path, balanced, log_size, original_experiment):
    '''
    Generate row reading the json
    args:
        dict: json with the trace
        case: number of the case
        variante: if use the initial value or the generate
    '''
    # actual_path = os.getcwd()
    if original_experiment:
        capture_path = attachments_path + sep + element["initValue"]
    else:
        capture_path = element["initValue"]
    args_tmp = element["args"]
    args = [generate_path, acu]
    #new_image = generate_screenshot_demo(args)
    new_image = detect_function(
        experiment.screenshot_name_generation_function)(args)
    
    capture_img = Image.open(capture_path)
    
    # if os.path.isfile(image_path_to_save + '.json'):
    #     with open(image_path_to_save + '.json', 'r') as f:
    #         json_properties = json.load(f)
    # else:
    json_properties = {
            "img_shape": [
                np.array(capture_img).shape
            ],
            "compos": []
        }
    id = 1
    
    try:
        for i in columns_ui:
            try:
                arguments = []
                if i in args_tmp:
                    func = args_tmp[i]
                    for screenshots_args in func:
                        if element is not None:
                            coordinates = screenshots_args["coordinates"]
                            var_function_name = screenshots_args["name"]
                            # TODO: generate autocolumns in front and edit this line
                            if not "args_dependency" in screenshots_args: 
                                if experiment.screenshot_name_generation_function == "insert_text_image" and i in columns or "TextInput" in columns:
                                    arguments.append(attr[columns.index(i)])
                                args = util.args_by_function_in_order(screenshots_args["args"],var_function_name)
                                arguments.append(args)
                            if not sep in new_image:
                                image_path_to_save = generate_path + new_image
                            else:
                                image_path_to_save = new_image

                            # Check if there are previous variations applied to the original image and substitute the original image path by the modified one
                            if os.path.exists(image_path_to_save):
                                capture_path = image_path_to_save

                            argumentsSave = arguments.copy()
                            arguments.append(image_path_to_save)
                            arguments.append(capture_path)
                            arguments.append(coordinates)

                            ui_element_class = i.split('.')
                            ui_element_class = ui_element_class[len(ui_element_class)-1]

                            object_json_properties =  {
                                    "id": id,
                                    "class": ui_element_class,
                                    "column_min": coordinates[1],
                                    "row_min": coordinates[0],
                                    "column_max": coordinates[3],
                                    "row_max": coordinates[2],
                                    "width": coordinates[2]-coordinates[0],
                                    "height": coordinates[3]-coordinates[1]
                                }
                            
                            object_property, object_json_properties = manage_dependency(experiment, var_function_name, arguments, argumentsSave, screenshots_args, case, 0, 
                                              activity, variant, balanced, log_size, image_path_to_save, capture_path, coordinates, object_json_properties)

                            json_properties["compos"].append(object_json_properties)
                            id +=1
                            
                            with open(image_path_to_save + '.json', 'w') as f:
                                json.dump(json_properties, f, indent=4)
                            

                        else:
                            new_image = ""
                        arguments = []
            except Exception as e:
                print("Unexpected error: " + str(e)) # TODO
                arguments = []
    except Exception as e:
        print("Unexpected error: " + str(e))
        # func = args_tmp[i] or content = attr[ind_text]: list out of range
        new_image = ""
    return new_image


def generate_scenario_capture(experiment, element, case, generate_path, activity, variant, new_image, scenario, attachments_path):
    '''
    Generate row reading the json
    args:
        dict: json with the trace
        case: number of the case
        variante: if use the initial value or the generate
    '''
    capture_path = attachments_path + sep + element["initValue"]
    json_args = element["args"]
    args = [generate_path, case]

    arguments = []
    for gui_component_label in json_args:
        for variation_conf in json_args[gui_component_label]:
            if element is not None:
                coordinates = variation_conf["coordinates"]
                var_function_name = variation_conf["var_function_name"]
                if not "args_dependency" in variation_conf: 
                    args = util.args_by_function_in_order(variation_conf["args"],var_function_name)
                    arguments.append(args)
                if not sep in new_image:
                    image_path_to_save = generate_path + new_image
                else:
                    image_path_to_save = new_image

                # Check if there are previous variations applied to the original image and substitute the original image path by the modified one
                if os.path.exists(image_path_to_save):
                    capture_path = image_path_to_save

                argumentsSave = arguments.copy()
                arguments.append(image_path_to_save)
                arguments.append(capture_path)
                arguments.append(coordinates)

                manage_dependency(experiment, var_function_name, arguments, argumentsSave,
                                  variation_conf, case, scenario, activity, variant, None, None)
            else:
                new_image = ""
            arguments = []

    return new_image
