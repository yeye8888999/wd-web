# 创建模型基类，所有模型都继承此基类
from django.db import models


class BaseModel(models.Model):
    """模型类基类"""
    # 创建时间
    create_time = models.DateTimeField(auto_now_add = True,verbose_name='创建时间')
    # 最后修改时间
    update_time = models.DateTimeField(auto_now=True,verbose_name='修改时间')

    class Meta(object):
        abstract = True