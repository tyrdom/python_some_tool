import re


def c_data(some_type, some_data):
    str_type = str(some_type)
    str_data = str(some_data)
    # print(str_data)
    if str_type.endswith('[]'):
        new_type = str_type[:-2]
        data_list = c_list(str_data)
        result = list(map(lambda x: c_data(new_type, x), data_list))
        return result

    elif str_type.startswith('[') & str_type.endswith(']'):
        res_tuple = c_tuple(str_type, str_data)
        return res_tuple

    elif str_type.startswith('{') & str_type.endswith('}'):
        res_obj = c_simple_obj(str_type, str_data)
        return res_obj

    else:
        return c_basic(str_type, str_data)


def rmv_pattern(some_str):
    if some_str.startswith('[') & some_str.endswith(']'):
        return some_str[1:-1]
    else:
        return some_str


def rmv_big_pattern(s_str):
    if s_str.startswith('{') & s_str.endswith('}'):
        return s_str[1:-1]
    else:
        return s_str


def c_tuple(s_type, s_data):
    str_type = rmv_pattern(s_type)
    str_data = rmv_pattern(s_data)
    split_type = my_split(str_type)
    split_data = my_split(str_data)
    if len(split_type) == len(split_data):
        return list(map(lambda x, y: c_data(x, y), split_type, split_data))
    else:
        print('~~~~~~~~~~~~~~~~~~~~waring~~~~~~~~~~~', str_type, 'data:::', str_data)
        return []


def c_list(s_data):
    if s_data == '':
        return []
    else:
        return my_split(str(s_data))


# 对象格式{key|type=key|type=key|type}
# 对象数据[value=value=value],把tuple转为字典对象
def c_simple_obj(obj_type, obj_data):
    type_str = rmv_big_pattern(obj_type)
    keys, types = get_properties([], [], type_str)

    str_data = rmv_pattern(obj_data)
    # print(str_data)
    data_list = my_split(str_data)
    # print(keys,types,data_list)

    c_obj = {}
    for i in range(len(keys)):
        c_obj[keys[i]] = c_data(types[i], data_list[i])
    return c_obj


def get_properties(keys, types, obj_type_str):
    if obj_type_str == '':
        return keys, types
    else:
        a_key, type_and_rest = obj_type_str.split('|', 1)
        new_keys = keys + [a_key]
        res = slice_a_type(type_and_rest)
        rest = res[1]
        new_types = types + [res[0]]
        return get_properties(new_keys, new_types, rest)


def slice_a_type(sm_str):

    p = 0
    for i in range(len(sm_str)):
        if sm_str[i] == '[':
            p += 1
        elif sm_str[i] == ']':
            p -= 1

        if (sm_str[i] == '=') & (p == 0):

            # print([sm_str[:i], sm_str[i + 1:]])
            return sm_str[:i], sm_str[i + 1:]
    return sm_str, ''


def split_2_part(sm_str):
    p = 0
    for i in range(len(sm_str)):
        if sm_str[i] == '[':
            p += 1
        elif sm_str[i] == ']':
            p -= 1

        if p == 0:
            return sm_str[:i + 1], sm_str[i + 2:]


def my_split(s_str):
    out_list = []
    to_list = split_data_to_list(out_list, s_str)
    return to_list


def split_data_to_list(a_list, rest_str):
    if rest_str == '':
        return a_list
    elif rest_str.startswith('['):
        a_unit, rest = split_2_part(rest_str)
        unit_ = a_list + [a_unit]
        return split_data_to_list(unit_, rest)
    else:
        res = rest_str.split('=', 1)
        if len(res) == 1:
            rest = ''
        else:
            rest = res[1]
        return split_data_to_list(a_list + [res[0]], rest)


def c_basic(s_type, s_data):
    if s_type == 'int':
        if s_data == '':
            return 0
        else:
            return int(float(s_data))
    elif s_type == 'float':
        if s_data == '':
            return 0.0
        else:
            return float(s_data)
    elif s_type == 'bool':
        # print("!!!!!!!Bool!!!!!!",s_data)
        if s_data == '1.0':
            # print("!!!!!!!True!!!!!!")
            return True
        else:
            return False
    else:
        if is_number(s_data) & s_data.endswith('.0'):
            # print('data:----', s_data)
            return str(int(float(s_data)))
        else:
            return str(s_data)


def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False
