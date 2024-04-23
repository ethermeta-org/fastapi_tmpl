# fastapi模版仓库

1. 预先准备

> python >= 3.11

2. 开发准备

```bash
pip install -r requirements.txt 
```

3. 编译

```bash
docker build -t app:latests --no-cache .
```

4. 使用方法：

> 1. 修改release.py文件夹中的内容，设定关于项目的名称
> 2. 修改config.py文件中关于envvar_prefix，关于环境变量前缀
