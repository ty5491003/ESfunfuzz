# -*- coding: utf-8 -*-
# 
# @Version: python 3.7
# @File: testcase.py
# @Author: ty
# @E-mail: nwu_ty@163.com
# @Time: 2020/12/29
# @Description: 与testcase_pool做orm的对象
# @Input:
# @Output:
#
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func, select


Base = declarative_base()


# 定义测试用例及其结果类
class Testcase(Base):

    # 必须显式指定映射的表名
    __tablename__ = 'testcase_pool'

    # OMR映射，具体字段含义参考Readme.md文档
    # 注意这里的String映射到MySQL中的话是 varchar，属于变长字符串
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_code = Column(String(10))
    testcase = Column(Text)
    timeout = Column(Integer)
    parent_id = Column(Integer)
    date = Column(Text, nullable=False)
    assign = Column(String(20), nullable=True)
    remark = Column(Text, nullable=True)

    def __repr__(self):
        return f"Testcase(id={self.id}, state_code={self.state_code}, " \
            f"parent_id={self.parent_id}, count={self.count})"


class FilteredTestcase(Base):

    # 必须显式指定映射的表名
    __tablename__ = 'filtered_testcase_pool'

    # OMR映射，具体字段含义参考Readme.md文档
    # 注意这里的String映射到MySQL中的话是 varchar，属于变长字符串
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_code = Column(String(10))
    testcase = Column(Text)
    timeout = Column(Integer)
    parent_id = Column(Integer)
    date = Column(Text, nullable=False)
    assign = Column(String(20), nullable=True)
    remark = Column(Text, nullable=True)

    def __repr__(self):
        return f"FilteredTestcase(id={self.id}, state_code={self.state_code}, " \
            f"parent_id={self.parent_id})"


class DataBase:
    def __init__(self, db_path_url: str) -> None:
        # 创建数据库连接和基本映射类(假如数据库存在就用已存在的)
        self.engine = create_engine(db_path_url, echo=False)
        Base.metadata.create_all(self.engine, checkfirst=True)

        # 测试数据库连接是否正常
        self.test_db_connect()

    def test_db_connect(self):
        connect = self.engine.connect()
        result = connect.execute("select 1")
        assert result.fetchone()[0] == 1, "数据库连接有误，请检查后重试！"

    def add(self, Testcase: object) -> object:
        """
        向表中插入一条记录（即新的Testcase对象）
        Args:
            Testcase (): 新Testcase的记录

        Returns:
            新记录插入后的id序号
        """
        # 获取Session及其实例
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # type_id表示插入后的id，默认为0
        new_id = 0
        # 插入数据
        try:
            session.add(Testcase)
            session.flush()
            new_id = Testcase.id
            # 提交
            session.commit()
        except Exception as e:
            pass
        finally:
            session.close()
            return new_id

    def get_a_record_randomly(self) -> Testcase:
        """
        随机从表中读取一条记录，用来执行突变并Fuzzing
        性能消耗：当表中有10000条记录时，此方法耗时约0.015~0.025秒，尚能接受
        Returns:
            读出的Testcase实例对象
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        random_testcase = None
        try:
            random_testcase = session.query(Testcase).order_by(func.random()).first()
        except Exception as e:
            pass
        finally:
            session.close()
            return random_testcase

    def compare_and_filter(self, _Testcase: Testcase) -> bool:
        """
        比较Fuzzing结果是否已经存在
        Args:
            _Testcase (): 要查询的Testcase对象实例

        Returns:
            bool，返回True表示没有重复；返回False表示有重复记录，需要被过滤
        """
        # 获取Session及其实例
        Session = sessionmaker(bind=self.engine)
        session = Session()
        flag = True

        try:
            all_possible_results = session.query(Testcase).filter(
                Testcase.state_code == _Testcase.state_code
            ).all()

            if len(all_possible_results) != 0:
                flag = False
        finally:
            session.close()
            return flag
