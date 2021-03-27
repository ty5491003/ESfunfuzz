# 作者：ty
# 时间：2019-6-12
# 作用：本脚本用来完成以下3个任务：
# 1. 下载仓库
# 2. 删除掉仓库中的非.js文件（防止占用空间太大）
# 3. 将仓库按序号重命名（防止同名仓库发生覆盖）


cat qian2000.txt | while read line
do
    str="$line"

    # # 字符串拆分，得到三项数据
    arr=(${str//,/ })
    idx="${arr[0]}"
    repo="${arr[1]}"
    download_path="${arr[2]}"

    # 根据数据下载仓库
    git clone --depth 1 $download_path   # --depth 1: 不下载 .git文件

    # 进入该仓库,获得该仓库内的所有js文件路径。修改：进入目录之前，要先判断是否存在。
    if [ -d $repo ];then

        cd $repo

        # 先删除掉其.git文件夹（假如存在的话）
        if [ -d ".git" ];then
            rm -rf ".git"
        fi

        # 将查找到的非.js文件都列出来
        find . -type f | grep -vP "\.js$" > NISL_FILE_LIST.txt

        # 将非.js文件全部删除
        cat NISL_FILE_LIST.txt | while read line
        # for line in `cat NISL_FILE_LIST.txt`
        do
            rm -f "$line"
        done

        # 退出该文件夹，并以序号重命名
        cd /f/ty/top_4000_repos   # 不用 cd ..
        mv $repo $idx
    fi
done
