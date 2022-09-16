import DataReslut
import argparse
from configparser import ConfigParser
import os
import csv


def _args_parse():
    parser = argparse.ArgumentParser(description="A python csv script")
    parser.add_argument('-d', '--dir', action='store', dest='directory', required=False, default="./",
                        help='source directory')
    parser.add_argument('-o', '--out', action='store', dest='out_file', required=False, default="result.csv",
                        help='output file path')
    parser.add_argument('-a', '--AF', action='store_true', dest='AF', required=False, default=False,
                        help='collect AF data')
    return parser.parse_args()


def _parse_config(af_need):
    config_map = {}
    conf = ConfigParser()
    file_path = os.path.join(os.path.abspath('.'), 'config.ini')
    assert os.path.exists(file_path)
    conf.read(file_path)

    config_map["SerialCount"] = conf.get("File", "SerialCount")
    config_map["AddrEnd"] = conf.get("File", "AddrEnd")
    config_map["AWB_Begin_Addr"] = conf.get("Module", "AWB_Begin_Addr")
    config_map["AWB_End_Addr"] = conf.get("Module", "AWB_End_Addr")
    config_map["AWB_Data_Mod"] = conf.get("Module", "AWB_Data_Mod")

    config_map["LSC_Begin_Addr"] = conf.get("Module", "LSC_Begin_Addr")
    config_map["LSC_End_Addr"] = conf.get("Module", "LSC_End_Addr")
    config_map["LSC_Data_Mod"] = conf.get("Module", "LSC_Data_Mod")

    if af_need:
        config_map["AF_Begin_Addr"] = conf.get("Module", "AF_Begin_Addr")
        config_map["AF_End_Addr"] = conf.get("Module", "AF_End_Addr")
        config_map["AF_Data_Mod"] = conf.get("Module", "AF_Data_Mod")

    return config_map


def _get_all_files_path(config_map):
    filenames = []
    for root, dirs, files in os.walk(mod_configs["src_dir"]):
        for f in files:
            filenames.append(os.path.join(root, f))

    return filenames


def _handle_files(config_map):

    files_arr = _get_all_files_path(config_map)
    cam_obj = None
    awb_header = ["Serial", "AWB_R", "AWB_GR", "AWB_GB", "AWB_G"]
    awb_row = None
    out_dir = config_map["dst_file"]
    out_awb = open(out_dir + "/awb_result.csv", 'w')
    awb_writer = csv.writer(out_awb)
    awb_writer.writerow(awb_header)

    for root, dirs, file in os.walk(mod_configs["src_dir"]):
        file_path = mod_configs["src_dir"] + "/" + file[0]
        cam_obj = DataReslut.CamMod(file_path, config_map["SerialCount"], config_map["AddrEnd"])
        awb_row = cam_obj.get_awb_data(config_map["AWB_Begin_Addr"], config_map["AWB_End_Addr"],
                                       config_map["AWB_Data_Mod"])
        awb_writer.writerow(awb_row)
    out_awb.close()


if __name__ == '__main__':
    ag_pars = _args_parse()
    mod_configs = _parse_config(ag_pars.AF)
    mod_configs["src_dir"] = ag_pars.directory
    mod_configs["dst_file"] = ag_pars.out_file

    _handle_files(mod_configs)
