import os
import itertools
import xml.etree.ElementTree as ET
import cv2
import shutil

base_path = 'CMP_facade_DB'
subfolders = ['base', 'extended']
subfolders = subfolders[0:1]
cropped_images_extension = 'jpg'
cropped_parts_path = "%s/cropped" % base_path

def get_all_xml_filenames(path):
    xml_filenames = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        filenames = list(filter(lambda x: x.endswith(".xml"), filenames))
        xml_filenames.extend(filenames)
        break
    return xml_filenames


def get_all_objects_from_xml_file(path):
    xml_objects = []
    with open(path) as f:
        it = itertools.chain('<root>', f, '</root>')
        root = ET.fromstringlist(it)
    
    for child in root:
        obj = {
            'label': '',
            'labelname': '',
            'flag': '',
            'points': {
                'x1': 0,
                'x2': 0,
                'y1': 0,
                'y2': 0,
            },
        }

        for v in child.iter("label"):
#             print ("tag: %s text: %s" % (v.tag, v.text.strip())) 
            obj[v.tag] = v.text.strip()
        for v in child.iter("labelname"):
#             print ("tag: %s text: %s" % (v.tag, v.text.strip()))
            obj[v.tag] = v.text.strip()
        for v in child.iter("flag"):
#             print ("tag: %s text: %s" % (v.tag, v.text.strip()))
            obj[v.tag] = v.text.strip()        
        for points in child.iter("points"):
            i = 1
            for v in points.iter("x"):
#                 print ("tag: %s text: %s" % (v.tag.strip(), v.text.strip()))
                obj["points"]["%s%s" % (v.tag.strip(), str(i))] = float(v.text.strip())
                i += 1
            i = 1
            for v in points.iter("y"):
#                 print ("tag: %s text: %s" % (v.tag.strip(), v.text.strip()))
                obj["points"]["%s%s" % (v.tag.strip(), str(i))] = float(v.text.strip())
                i += 1   
#         print(obj)
        xml_objects.append(obj)
    return xml_objects


def crop_object_from_img(img, points):
    y1 = int(img.shape[1] * points['y1'])
    y2 = int(img.shape[1] * points['y2'])
    x1 = int(img.shape[0] * points['x1'])
    x2 = int(img.shape[0] * points['x2'])
    return img[x1:x2, y1:y2]

print("Cleaning %s" % cropped_parts_path)
shutil.rmtree(cropped_parts_path)
if not os.path.exists(cropped_parts_path):
    print("Adding %s" % cropped_parts_path)
    os.makedirs(cropped_parts_path)
print('\n')

total_number_added = 0
total_number_skipped = 0
for subfolder in subfolders:
    
    subfolder_path = '%s/%s' % (base_path, subfolder)
    xml_filenames = get_all_xml_filenames(subfolder_path)
    
    for xml_filename in xml_filenames:
        print("Processing %s" % xml_filename)
        img_filename = xml_filename.replace('xml', 'jpg')
        img = cv2.imread('%s/%s' % (subfolder_path, img_filename))        
        
        xml_objects = get_all_objects_from_xml_file('%s/%s' % (subfolder_path, xml_filename))
        number_added = 0
        number_skipped = 0
        
        for xml_object in xml_objects:
            img_cropped = crop_object_from_img(img, xml_object['points'])
            label_folder_name = '%s/%s' % (cropped_parts_path, xml_object['labelname'])
            if not os.path.exists(label_folder_name):
                os.makedirs(label_folder_name)
            
            cropped_image_base_name = '%s/%s' % (label_folder_name, img_filename.rsplit(".", 1)[0])
            i = 1            
            cropped_image_name = '%s_%s.%s' % (cropped_image_base_name, i, cropped_images_extension)

            while os.path.exists(cropped_image_name):
                i = i + 1
                cropped_image_name = '%s_%s.%s' % (cropped_image_base_name, i, cropped_images_extension)

            if (img_cropped.shape[0] == 0 or img_cropped.shape[1] == 0):
                print("One object in image %s is being skipped because cropped area is has 0 in one of the dimensions" % img_filename)
                print("xml_object", xml_object)
                print("img_cropped.shepe", img_cropped.shape)
                print("\n")
                number_skipped += 1
            else:
                cv2.imwrite(cropped_image_name, img_cropped)
                number_added += 1
        if number_skipped > 0:
            print("Cropped %s items from %s number of skipped objects %s " % (str(number_added), img_filename, str(number_skipped)))
        else:
            print("Cropped %s items from %s" % (str(number_added), img_filename))
        
        total_number_added += number_added
        total_number_skipped += number_skipped
        
        print(' ')
        
print('In total, added: %s skipped: %s' %(int(total_number_added), int(total_number_skipped)))
print('Finished')