# coding=utf-8

import sys

# 兼容 python2 的编码
try:
    reload(sys)
    # pylint: disable=no-member
    sys.setdefaultencoding('utf-8')
except NameError as e:
    pass

# 导入线程库
from threading import Thread, Lock

# 导入 python-gitlab
import gitlab

# 导入配置
from config import gitlabInfos, projectNames, userNames, startTime, endTime

# 线程
threads = []
# 查询结果
result = {}

lock = Lock()

# 查询指定 GitLab
def inquireGitLab(url, token):
    # 登录 获取gitlab操作对象gl
    gl = gitlab.Gitlab(url, token)

    # 先把所有项目查出来
    projects = gl.projects.list(all=True)

    # 遍历每一个项目
    for project in projects:
        if project.name in projectNames:
            callback = lambda: inquireProject(project)
            thread = Thread(target=callback)
            threads.append(thread)
            thread.start()

# 查询指定项目
def inquireProject(project):
    commitIds = []
    # 把每个项目下面的所有分支查出来
    branches = project.branches.list()
    # 然后再遍历每一个分支
    for branch in branches:
        # 根据时间、分支名遍历该分支下面所有的提交记录
        params = { 'since': startTime, 'until': endTime, 'ref_name': branch.name }
        commits = project.commits.list(all=True, query_parameters=params)
        # 然后再遍历每个提交记录
        for commit in commits:
            # 去重
            if commit.id in commitIds:
                continue
            # 去除 Merge
            if commit.title.startswith('Merge'):
                continue
            name = commit.author_name
            # 去除非指定用户
            if (name not in userNames):
                continue
            lock.acquire()
            result[name] = result.get(name, 0) + 1
            lock.release()
            commitIds.append(commit.id)
            print(name, result[name])

# 启动查询
for info in gitlabInfos:
    inquireGitLab(info[0], info[1])

# 等待所有线程任务结束
for t in threads:
    t.join()

print("result ===========>")
print(result)
