import execjs


def mutate_testcase(file_path):
    """
    mutate testcase according ECMAScript-262 10 edition
    :param file_path: the file that contain the testcase and API nodes
    :return: the mutated tastcases
    """
    mutation = execjs.compile("""
        let {testcaseMutation} = require("./CaseMutator/mutation")

        function mutation(filePath){
            return testcaseMutation(filePath);
        }
     """)
    return mutation.call("mutation", str(file_path))


def get_info(file_path):
    """
    获取突变过程中的信息，用于中途打印
    Args:
        file_path ():

    Returns:

    """
    getter = execjs.compile("""
        let {get_semantic_info} = require("./CaseMutator/mutation")
        function get(filePath){
            return get_semantic_info(filePath);
        }
     """)
    return getter.call("get", str(file_path))