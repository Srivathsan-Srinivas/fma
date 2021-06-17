import json
import os
import subprocess


class JsonUtilities:
    def __init__(self):
        pass

    @staticmethod
    def prettify_json(in_json_file, out_json_file):
        """
        Prettifies a json file.
        :param in_json_file: Input json file with absolute path.
        :param out_json_file: Output json file with absolute path.
        :return:
        """
        cmd = "jq . " + in_json_file + " > " + out_json_file
        flag = True
        try:
            p = subprocess.Popen(cmd, shell=True)
            os.waitpid(p.pid, 0)
        except:
            flag = False
        return flag

    @staticmethod
    def write_dict_to_json_file(dict_obj, directory, full_file_name):
        """
        :param dict_obj: Eg., d = {"name": "Oscar", "sex": "Male", "Age": 32, "ids": [32, 65, 322, 644]}
        :param directory:
        :param full_file_name:
        :return: A json file where the dict keys are sorted.
                {"Age": 32, "ids": [32, 65, 322, 644], "name": "Oscar", "sex": "Male"}
        """
        flag = False
        if os.path.exists(directory):
            if dict_obj:
                with open(full_file_name, 'w') as fp:
                    try:
                        json.dump(dict_obj, fp, sort_keys=True)
                    except:
                        raise Exception("Unable to write to JSON file: %s", full_file_name)
                    else:
                        flag = True
            else:
                raise Exception("Sample dict object is empty. Unable to write to file.")
        else:
            raise Exception("Directory %s doesn't exist. Unable to write file to directory", directory)
        return flag
