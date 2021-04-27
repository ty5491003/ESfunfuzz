import json
import pathlib
import tempfile

from collections import OrderedDict

from CaseMutator.getApisFromTestcase import ESAPI
from CaseMutator.getMutatedTestcase import mutate_testcase, get_info


class Mutator:
    def __init__(self):
        self.instance = ESAPI(get_config())

    def get_semantic_info(self, testcase):
        nodes = self.instance.parse_function_nodes(testcase)
        all_semantic_info = []
        if len(nodes) > 0:
            counter = self.instance.count_es_apis_in_testcase(nodes)
            api_node_info = {"testcase": testcase, "nodes": nodes, "counter": counter}
            with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
                api_node_info_path = pathlib.Path(f.name)
                with open(api_node_info_path, "w+") as f:
                    json.dump(api_node_info, f)
                try:
                    all_semantic_info = get_info(api_node_info_path)
                except Exception as e:
                    pass

        return all_semantic_info

    def mutate(self, testcase):
        nodes = self.instance.parse_function_nodes(testcase)

        mutated_testcase_set = [testcase]
        if len(nodes) > 0:
            counter = self.instance.count_es_apis_in_testcase(nodes)

            api_node_info = {"testcase": testcase, "nodes": nodes, "counter": counter}
            with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
                api_node_info_path = pathlib.Path(f.name)
                with open(api_node_info_path, "w+") as f:
                    json.dump(api_node_info, f)
                try:
                    mutated_testcase_set = set(mutate_testcase(api_node_info_path))

                except Exception as e:
                    pass
        return mutated_testcase_set

    def print_info(self, info):
        for i in info:  # i是字典
            print(f'{i.get("APIName")}:')
            semantic_info = i.get("Semantic_info")
            for j in semantic_info:
                if j.get('name') != 'that':
                    print(json.dumps(self.dict_order(j), indent=4, ensure_ascii=False))

            print('=' * 50)

    def dict_order(self, _dict):
        """Controls the print order of the dictionary
        """
        new_dict = OrderedDict()
        new_dict['name'] = _dict.get('name')
        new_dict['type'] = _dict.get('type')
        new_dict['conditions'] = _dict.get('conditions')
        new_dict['scopes'] = _dict.get('scopes')
        new_dict['values'] = _dict.get('values')
        return new_dict


def get_config():
    return {
    "function": "./CaseMutator/APIs/function.txt",
    "constructor": "./CaseMutator/APIs/constructor.txt",
    "classMethod": "./CaseMutator/APIs/classMethod.txt",
    "prototypeMethod": "./CaseMutator/APIs/prototypeMethod.txt"
  }
