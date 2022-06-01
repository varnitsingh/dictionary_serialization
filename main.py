import json
class Blockonomics:
    def serialize(filename:str,data:dict) -> None:
        '''
        Serialize data to file.
        :param filename: str - filename
        :param data: dict - data to serialize
        '''
        with open(filename,'wb') as f:
            f.write(bytes(str(data), "utf-8"))

    def parse_column(data:str):
        column = data.strip().split(':')
        key = column[0].replace("'","").strip()
        # print(data)
        value = column[1].strip()
        # print(value)
        if value[0] == "'":
            value = str(value[1:-1]).strip()
        elif value == 'None':
            value = None
        elif value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif value.find('.') != -1:
            value = float(column[1].strip())
        elif value.isnumeric():
            value = int(column[1].strip())
        elif value[0] == '[':
            value = Blockonomics.nested_deserialization(value)
            # print(value)
        
        return key, value

    def parse_value(value:str) -> str:
        # print(value)
        if value[0] == '[' or value[0] == '{':
            value = Blockonomics.nested_deserialization(value)
        elif value[0] == "'":
            value = str(value[1:-1]).strip()
        elif value == 'None':
            value = None
        elif value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif value.find('.') != -1:
            value = float(value.strip())
        elif value.isnumeric():
            value = int(value.strip())
        return value


    def nested_deserialization(data:str):
        if data[0] == '[':
            return_list = []
            depth = 0
            previous_chunk_location = 0
            previous_column_location = 1
            previous_dict_location = None
            value = None
            for i in range(1,len(data)):
                if data[i] == ']' and depth == 0:
                    if len(data[previous_column_location:i].strip()) == 1:
                        value = Blockonomics.parse_value(data[previous_column_location:i].strip())
                        return_list.append(value)
                    return return_list
                elif data[i] == ']' and depth != 1:
                    # print(type(data[i]),len(data[i]),data[i],depth)
                    depth -= 1
                elif data[i] == ']' and depth == 1:
                    # print(type(data[i]),len(data[i]),data[i],depth)
                    depth -= 1
                    value = Blockonomics.nested_deserialization(data[previous_chunk_location:i+1].strip())
                    return_list.append(value)
                elif data[i] == '[':
                    # print(type(data[i]),len(data[i]),data[i],depth)
                    depth += 1
                    if depth == 1:
                        previous_chunk_location = i
                elif data[i] == ',' and depth == 0:
                    # print(type(data[i]),len(data[i]),data[i],depth,i)
                    value = Blockonomics.parse_value(data[previous_column_location:i].strip())
                    if type(value) != type([]) and type(value) != type({}):
                        return_list.append(value)
                    previous_column_location = i+1
                elif data[i] == '}' and depth != 1:
                    depth -= 1
                elif data[i] == '}' and depth == 1:
                    depth -= 1
                    # print(type(data[i]),len(data[i]),data[i],depth,i)
                    value = Blockonomics.nested_deserialization(data[previous_dict_location:i+1])
                    # print(value)
                    return_list.append(value)
                elif data[i] == '{':
                    depth += 1
                    previous_dict_location = i
                elif data[i] == '}':
                    depth -= 1
        elif data[0] == '{':
            return_dict = {}
            previous_column_location = None
            previous_chunk_location = 0
            depth = 0
            key, value = None, None
            for i in range(1,len(data)):
                # print(data[i],depth)
                if data[i] == '}' and depth == 0:
                    key, value = Blockonomics.parse_column(data[previous_column_location:i])
                    if key not in return_dict:
                        return_dict[key] = value
                    # print(key,value)
                    return return_dict
                elif data[i] == '}' and depth != 1:
                    depth -= 1
                elif data[i] == '}' and depth == 1:
                    depth -= 1
                    value = Blockonomics.nested_deserialization(data[previous_chunk_location:i+1])
                    key = data[previous_column_location:previous_chunk_location].strip().split(":")[0].replace("'","").strip()
                    return_dict[key] = value
                elif data[i] == '{':
                    depth += 1
                    if depth == 1:
                        previous_chunk_location = i
                elif data[i] == ',' and depth == 0:
                    key, value = Blockonomics.parse_column(data[previous_column_location:i])
                    if key not in return_dict:
                        return_dict[key] = value
                    previous_column_location = i+1
                elif data[i] == '[':
                    depth += 1
                elif data[i] == ']':
                    depth -= 1
                elif previous_column_location is None:
                    previous_column_location = i
        else:
            raise Exception('Invalid data')

    def deserialize(filename:str) -> dict:
        '''
        Deserialize data from file.
        :param filename: str - filename
        :return: dict - deserialized data
        '''
        data = None
        with open(filename,'rb') as f:
            data = f.read().decode("utf-8")
        if data:
            return Blockonomics.nested_deserialization(data)
            # return data
        else:
            return {}

if __name__ == '__main__':
    with open('MOCK_DATA.json','r') as rf:
        data = json.load(rf)
    Blockonomics.serialize("sample.bin",data)
    data = Blockonomics.deserialize("sample.bin")
    with open('data.json','w') as wf:
        json.dump(data,wf,indent=4)
