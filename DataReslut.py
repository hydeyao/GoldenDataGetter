import csv


class DataMod:
    ModDefault = 0
    ModSingle = 1
    ModRate = 2
    Mod16MSB = 4
    Mod16LSB = 8


def data_merge(h_byte, l_byte):
    return h_byte << 8 | l_byte


class CamMod:
    serial = ''
    data_map = {}

    awb_r = 0
    awb_gr = 0
    awb_gb = 0
    awb_b = 0

    awb_r2g = 0
    awb_b2g = 0
    awb_gb2gr = 0

    af_inf = 0
    af_mac = 0

    quan_lsc_r = list()
    quan_lsc_gr = list()
    quan_lsc_gb = list()
    quan_lsc_b = list()

    def __init__(self, filepath, serial_cnt, addr_end):
        self.filepath = filepath
        self.serial_cnt = serial_cnt
        self.addr_end = addr_end
        self.__init_data_map()

    def get_serial(self):
        self.serial = self.filepath.left(self.serial_cnt)
        return self.serial

    def __get_data(self, begin, end, mode=DataMod.ModSingle):
        res_arr = []
        if mode == 0:
            for addr in range(begin, end + 1):
                res = self.data_map[addr]
                res_arr.append(res)
        else:
            for addr in range(begin, end + 1, 2):
                res = data_merge(self.data_map[addr], self.data_map[addr + 1])
                res_arr.append(res)
        return res_arr

    def __init_data_map(self):
        f = open(self.filepath)
        reader = csv.reader(f)
        for row in reader:
            tmp = row[1]
            if tmp[0:2] == '0x':
                if int(tmp, 16) >= self.addr_end:
                    break
                self.data_map[int(row[1], 16)] = int(row[2], 16)
        f.close()

    def get_awb_data(self, awb_addr_bg, awb_addr_end, mode=1, base=512):
        awb_res_arr = self.__get_data(awb_addr_bg, awb_addr_end, 0)
        if mode == DataMod.ModSingle:

            self.awb_r = awb_res_arr[0]
            self.awb_gr = awb_res_arr[1]
            self.awb_gb = awb_res_arr[2]
            self.awb_b = awb_res_arr[3]

            self.awb_r2g = int((float(awb_res_arr[0]) / float(awb_res_arr[1]) * base) + 0.5)
            self.awb_b2g = int((float(awb_res_arr[3]) / float(awb_res_arr[1]) * base) + 0.5)
            self.awb_gb2gr = int((float(awb_res_arr[2]) / float(awb_res_arr[1]) * base) + 0.5)
        else:
            self.awb_r2g = awb_res_arr[0]
            self.awb_b2g = awb_res_arr[1]
            self.awb_gb2gr = awb_res_arr[2]

        awb_res_arr.insert(0, self.serial)
        return awb_res_arr

    def get_af_data(self, af_bg, af_end, mode=1):
        af_res_arr = self.__get_data(af_bg, af_end, 1)
        self.af_inf = af_res_arr[0]
        self.af_mac = af_res_arr[1]
        return af_res_arr

    def get_lsc_data(self, lsc_bg, ls_end, mode=1):
        lsc_res_arr = self.__get_data(lsc_bg, ls_end, 1)
        for i in range(0, len(lsc_res_arr), 4):
            self.quan_lsc_r.append(lsc_res_arr[i])
            self.quan_lsc_gr.append(lsc_res_arr[i + 1])
            self.quan_lsc_gb.append(lsc_res_arr[i + 2])
            self.quan_lsc_b.append(lsc_res_arr[i + 3])
