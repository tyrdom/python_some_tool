import glob
import json
import sys
import os
from trans_a_cell import c_data

from xlrd import open_workbook as op


def getFileData(f):
    '''
    转化为横表数据结构
    :param f:
    :return:
    '''

    def getSheet(f):
        '''
        获取目标sheet
        :param f:
        :return:
        '''
        return op(f).sheets()[0]

    def isHorizontalTable(sht):
        '''
        判断是否是横表
        :return:true是
        '''
        return sht._cell_values[0][0].replace(' ', '').upper() != 'transpose'.upper()

    sht = getSheet(f)
    if isHorizontalTable(sht):
        return [i for i in sht._cell_values]
    # 竖表
    ret = []
    rows = sht._cell_values[1:]  # 第一行标识转置，过滤
    for i in range(5):
        ret.append([rows[ii][i] for ii in range(len(rows))])
    colNum = len(sht._cell_values[1])
    for i in range(5, colNum, 1):
        ret.append([rows[ii][i] for ii in range(len(rows))])
    return ret


def getTableHeaderConfig(fileData):
    '''
    获取表头，非游戏数值部分结构
    :param f:
    :return:
    '''
    idIndex, valIndexList, notClientIndexList, originValList = 0, [], [], []
    r0, r4, originValList = fileData[0], fileData[4], fileData[5:]
    for i in range(len(r0)):
        if str(r0[i]).replace(' ', '').upper() == 'ID':
            idIndex = i
        elif len(r0[i].replace(' ', '')) != 0:
            valIndexList.append(i)

        nc = str(r4[i]).replace(' ', '').replace('.0', '')
        if len(nc) == 1 and int(nc) == 1:
            notClientIndexList.append(i)

    filteredOriginValList = []

    for i in originValList:
        if len(str(i[idIndex]).replace(' ', '')) > 0:
            filteredOriginValList.append(i)

    # 程序运行需要的业务逻辑信息
    return {'idIndex': idIndex, 'valIndexList': valIndexList, 'notClientIndexList': notClientIndexList,
            'fileData': fileData, 'filteredOriginValList': filteredOriginValList}


def getTableData(tableHeaderConfig):
    '''
    获取表主体，游戏数值部分数据
    :param retD:
    :return:
    '''
    factory_id = lambda x: c_data('string', x)

    client = {'content_name': {}, 'content_info': {}, 'content_schema': {}, 'content': []}
    server = {'content_name': {}, 'content_info': {}, 'content_schema': {}, 'content': []}
    notClientIndexList = tableHeaderConfig['notClientIndexList']
    valIndexList = tableHeaderConfig['valIndexList']
    keys_name, keys_name_zh, keys_remark, keys_type, keys_client = tableHeaderConfig['fileData'][0:5]
    for i in range(0, len(keys_name), 1):
        if i not in valIndexList:
            continue
        name, name_zh, remark, type_ = keys_name[i], keys_name_zh[i], \
                                       keys_remark[i], keys_type[i]
        if i not in notClientIndexList:
            client['content_name'][name] = name_zh
            client['content_info'][name] = remark
            client['content_schema'][name] = type_
        server['content_name'][name] = name_zh
        server['content_info'][name] = remark
        server['content_schema'][name] = type_
    val_list = tableHeaderConfig['filteredOriginValList']
    idIndex = tableHeaderConfig['idIndex']
    for i in val_list:
        k = factory_id(i[idIndex])
        v = i
        c_use, s_use = {'id': k}, {'id': k}
        try:
            for ii in range(0, len(keys_name), 1):
                if ii not in valIndexList or ii == idIndex:
                    continue
                t = keys_type[ii]
                try:
                    ret_v = c_data(t, v[ii])
                    if ii not in notClientIndexList:
                        c_use[keys_name[ii]] = ret_v
                    s_use[keys_name[ii]] = ret_v
                except Exception as e:
                    raise BaseException('请检查原始文件,id=', k, '表格值=', v, e)
            server['content'].append(s_use)
            client['content'].append(c_use)
        except Exception as e:
            print(e)
    return {'server': server, 'client': client}


def writeFile(d, f):
    '''
    生成生成文件
    :param d:
    :param f:
    :return:
    '''

    s = json.dumps(d, ensure_ascii=False)
    with open(f, 'w', encoding='utf-8') as fw:
        fw.write(s)


if __name__ == '__main__':
    fileName, fileExtension = '', '.xlsx'
    thisFilePath, originDir, retDir = sys.path[0], 'configXlsx', 'json'
    getOriginFiles = lambda fileFeature=fileName + fileExtension: glob.glob(
        thisFilePath + os.sep + originDir + os.sep + '*' + fileFeature)
    originFiles = getOriginFiles()
    for f in originFiles:
        # print(f)
        nf_c = f.replace(originDir, 'c_' + retDir).replace(fileExtension, '')
        nf_s = f.replace(originDir, 's_' + retDir).replace(fileExtension, '')
        sF, cF = nf_s + '_s.json', nf_c + '_c.json'
        try:
            fileData = getFileData(f)
            print(f)
            tableHeaderConfig = getTableHeaderConfig(fileData)
            ret = getTableData(tableHeaderConfig)
            s, c = ret['server'], ret['client']
            writeFile(s, sF)
            writeFile(c, cF)
        except Exception as e:
            print(e)
