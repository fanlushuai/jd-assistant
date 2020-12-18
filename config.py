# -*- coding: utf-8 -*-
import argparse
import configparser
import os

CMD_SECTION = 'cmd'


class Config(object):

    def __init__(self, config_file='config.ini', cmd=None):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("No such file: config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8')

        # 使用命令行参数，重写部分配置
        if cmd:
            if self._config.has_section('sku'):
                if cmd.sku_id:
                    self._config.set('sku', 'sku_id', cmd.sku_id)
                if cmd.buy_time:
                    self._config.set('sku', 'buy_time', cmd.buy_time)

        # 添加cmd配置section，如果需要的话
        if not self._config.has_section(CMD_SECTION):
            self._config.add_section(CMD_SECTION)

        if cmd.aps:
            self._config.set(CMD_SECTION, 'aps', 'true')

    def get(self, section, name, strip_blank=True, strip_quote=True):
        s = self._config.get(section, name)
        if strip_blank:
            s = s.strip()
        if strip_quote:
            s = s.strip('"').strip("'")

        return s

    def getboolean(self, section, name):
        return self._config.getboolean(section, name)


parser = argparse.ArgumentParser(description='jd 抢购')
parser.add_argument('--config_file', type=str,
                    help='指定配置文件，可以用于隐藏自己的私有配置.默认配置为config.ini，'
                         '路径基于当前工作空间目录，比如，--config_file=cookies/config.ini  正好cookies是被gitignone隐藏的。就很ok')
parser.add_argument('--sku_id', type=str, help='购买商品id.优先级最高')
parser.add_argument('--buy_time', type=str, help='购买时间.优先级最高')
parser.add_argument('--aps', action='store_true', help='采用定时调度方式启动')
cmd_args = parser.parse_args()

global_config = Config(config_file=cmd_args.config_file if cmd_args.config_file else 'config.ini', cmd=cmd_args)
