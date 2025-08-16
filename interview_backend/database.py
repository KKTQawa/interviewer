import os
import json
import mysql.connector
from config import DATABASE_CONFIG
from typing import Dict, List, Optional, Union,Any,Tuple # 导入类型提示
from contextlib import contextmanager  # 用于上下文管理器

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)#显式指定返回词典
            #self._init_tables()
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            raise

    def __del__(self):
        try:
            # 关闭游标
            if self.cursor is not None:
                try:
                    self.cursor.close()
                except Exception as e:
                    print(f"关闭游标失败: {str(e)}")
                finally:
                    self.cursor = None  # 确保引用被清除

            # 关闭连接
            if self.connection is not None:
                try:
                    if self.connection.is_connected():  # mysql-connector特有检查
                        self.connection.close()
                except Exception as e:
                    print(f"关闭连接失败: {str(e)}")
                finally:
                    self.connection = None  # 确保引用被清除
        except Exception as e:
            print(f"关闭数据库资源时发生错误: {str(e)}")

    def commit(self):
        """提交当前事务"""
        print("提交当前事务-------------------------------------------")
        try:
            self.connection.commit()  # mysql-connector-python 的提交方式
        except mysql.connector.Error as e:  # 异常类不同
            print(f"  提交事务时发生错误: {e}")
            self.connection.rollback()  # 回滚事务
            raise

    def rollback(self):
        """回滚当前事务"""
        self.connection.rollback()

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def _validate_identifier(self, name: str) -> str:
        """验证SQL标识符（表名、列名）防止注入"""
        #暂时不启用
        return name

    def _build_where_clause(self, conditions: Dict[str, Any]) -> Tuple[str, Tuple]:
        """安全构建WHERE子句"""
        where_parts = []
        params = []
        for col, val in conditions.items():
            self._validate_identifier(col)
            where_parts.append(f"{col} = %s")
            params.append(val)
        return " AND ".join(where_parts), tuple(params)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """执行查询操作（安全参数化）"""
        try:
            with self.connection.cursor(dictionary=True ) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            raise

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新操作（安全参数化）"""
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                affected=cursor.rowcount
                return affected
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"Error executing update: {e}")
            raise

    def insert(self, table: str, data: Dict) -> int:
        """安全插入数据"""
        print("执行插入操作:","插入",table,'内容为',data)
        self._validate_identifier(table)
        columns = ", ".join([self._validate_identifier(col) for col in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_update(query, tuple(data.values()))

    def select(self, table: str, columns: List[str] = ["*"],
               conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        print("执行查询操作:","从",table,"查询",columns,"条件",conditions,"-------------------------------")
        """安全查询数据"""
        self._validate_identifier(table)
        validated_columns = [self._validate_identifier(col) if col != "*" else "*"
                             for col in columns]
        columns_str = ", ".join(validated_columns)

        query = f"SELECT {columns_str} FROM {table}"
        params = ()

        if conditions:
            where_clause, params = self._build_where_clause(conditions)
            query += f" WHERE {where_clause}"

        return self.execute_query(query, params)

    def update(self, table: str, data: Dict,
               conditions: Optional[Dict[str, Any]] = None) -> int:
        """安全更新数据"""
        print("执行更新操作:","更新",table,"条件",conditions,"内容:",data)
        self._validate_identifier(table)
        set_parts = []
        set_params = []
        for col, val in data.items():
            self._validate_identifier(col)
            set_parts.append(f"{col} = %s")
            set_params.append(val)

        query = f"UPDATE {table} SET {', '.join(set_parts)}"
        params = tuple(set_params)

        if conditions:
            where_clause, where_params = self._build_where_clause(conditions)
            query += f" WHERE {where_clause}"
            params += where_params

        return self.execute_update(query, params)

    def delete(self, table: str, conditions: Dict[str, Any]) -> int:
        """安全删除数据"""
        print("执行删除操作:","删除",table,"条件",conditions,"-------------------------------")
        self._validate_identifier(table)
        where_clause, params = self._build_where_clause(conditions)
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_update(query, params)

    def _init_tables(self):
        """初始化数据库表"""
        try:
            # 创建用户表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建社区帖子表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    post_type ENUM('面试题', '实时面试', '经验分享', '资源分享') NOT NULL,
                    tags VARCHAR(255),
                    views INT DEFAULT 0,
                    likes INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建帖子评论表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_comments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT NOT NULL,
                    user_id INT NOT NULL,
                    content TEXT NOT NULL,
                    likes INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES community_posts(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建资源链接表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    url VARCHAR(512) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    tags VARCHAR(255),
                    clicks INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()

        except Exception as e:
            print(f"数据库表初始化失败: {str(e)}")
            self.connection.rollback()
            raise
