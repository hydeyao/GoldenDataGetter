import DataReslut
import argparse
from configparser import ConfigParser
import os
import csv
import win32api


def _args_parse():
    parser = argparse.ArgumentParser(description="A python csv script")
    parser.add_argument('-a', '--AF', action='store_true', dest='AF', required=False, default=False,
                        help='collect AF data')
    return parser.parse_args()


def _parse_config(af_need):
    config_map = {}
    conf = ConfigParser()
    file_path = os.path.join(os.path.abspath('.'), 'config.ini')
    assert os.path.exists(file_path)
    conf.read(file_path)

    config_map["src_dir"] = conf.get("File", "SourceDataDir")
    config_map["dst_file"] = conf.get("File", "outPutDir")

    config_map["SerialCount"] = int(conf.get("File", "SerialCount"))
    config_map["AddrEnd"] = int(conf.get("File", "AddrEnd"), 16)
    config_map["AWB_Begin_Addr"] = int(conf.get("Module", "AWB_Begin_Addr"), 16)
    config_map["AWB_End_Addr"] = int(conf.get("Module", "AWB_End_Addr"), 16)
    config_map["AWB_Data_Mod"] = int(conf.get("Module", "AWB_Data_Mod"), 16)

    config_map["LSC_Begin_Addr"] = int(conf.get("Module", "LSC_Begin_Addr"), 16)
    config_map["LSC_End_Addr"] = int(conf.get("Module", "LSC_End_Addr"), 16)
    config_map["LSC_Data_Mod"] = int(conf.get("Module", "LSC_Data_Mod"), 16)

    if af_need:
        config_map["AF_Begin_Addr"] = int(conf.get("Module", "AF_Begin_Addr"), 16)
        config_map["AF_End_Addr"] = int(conf.get("Module", "AF_End_Addr"), 16)
        config_map["AF_Data_Mod"] = int(conf.get("Module", "AF_Data_Mod"), 16)

    return config_map


def _get_all_files_path(config_map):
    filenames = []
    for root, dirs, files in os.walk(mod_configs["src_dir"]):
        for f in files:
            filenames.append(os.path.join(root, f))

    return filenames


def _handle_files(config_map, af_need=0):
    files_arr = _get_all_files_path(config_map)
    cam_obj = None
    awb_header = ["Serial", "AWB_R", "AWB_GR", "AWB_GB", "AWB_G"]
    lsc_header = []
    for i in range(0, 221):
        lsc_header.append("B" + str(i))
    lsc_header.insert(0, "Serial")

    awb_row = None
    out_dir = config_map["dst_file"]
    out_awb = open(out_dir + "/awb_result.csv", 'w', newline="")
    out_lsc_r = open(out_dir + "/lsc_R_result.csv", 'w', newline="")
    out_lsc_gr = open(out_dir + "/lsc_Gr_result.csv", 'w', newline="")
    out_lsc_gb = open(out_dir + "/lsc_Gb_result.csv", 'w', newline="")
    out_lsc_b = open(out_dir + "/lsc_B_result.csv", 'w', newline="")
    awb_writer = csv.writer(out_awb)
    awb_writer.writerow(awb_header)

    lsc_r_writer = csv.writer(out_lsc_r)
    lsc_r_writer.writerow(lsc_header)

    lsc_gr_writer = csv.writer(out_lsc_gr)
    lsc_gr_writer.writerow(lsc_header)

    lsc_gb_writer = csv.writer(out_lsc_gb)
    lsc_gb_writer.writerow(lsc_header)

    lsc_b_writer = csv.writer(out_lsc_b)
    lsc_b_writer.writerow(lsc_header)

    for file in files_arr:
        cam_obj = DataReslut.CamMod(file, config_map["SerialCount"], config_map["AddrEnd"])
        awb_row = cam_obj.get_awb_data(config_map["AWB_Begin_Addr"], config_map["AWB_End_Addr"],
                                       config_map["AWB_Data_Mod"])
        awb_writer.writerow(awb_row)
        lsc_r, lsc_gr, lsc_gb, lsc_b = cam_obj.get_lsc_data(config_map["LSC_Begin_Addr"],
                                                            config_map["LSC_End_Addr"], 1, 1)
        lsc_r_writer.writerow(lsc_r)
        lsc_gr_writer.writerow(lsc_gr)
        lsc_gb_writer.writerow(lsc_gb)
        lsc_b_writer.writerow(lsc_b)

        cam_obj.data_clear()

    out_awb.close()
    out_lsc_r.close()
    out_lsc_gr.close()
    out_lsc_gb.close()
    out_lsc_b.close()


if __name__ == '__main__':
    ag_pars = _args_parse()
    mod_configs = _parse_config(ag_pars.AF)
    _handle_files(mod_configs)
    win32api.MessageBox(0, " lsc data get done", "OK")
