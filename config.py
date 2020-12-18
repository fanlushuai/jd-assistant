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

    def rewrite_by_cmd(self, cmd):
        # 使用命令行参数，1. 重写已有的配置文件参数。2. 添加额外的参数，对于无值参数，使用CMD_SECTION section。有自定义section的会添加section
        for arg in vars(cmd):
            print(arg)
            arg_split = arg.split(".")
            section_cmd = CMD_SECTION

            if arg_split.__len__() == 1:
                section_cmd = CMD_SECTION
                key = arg_split[0]
            elif arg_split.__len__() == 2:
                section_cmd = arg_split[0]
                key = arg_split[1]
            else:
                continue

            if not self._config.has_section(section_cmd):
                self._config.add_section(section_cmd)
            if getattr(cmd, arg):
                self._config.set(section_cmd, str(key), str(getattr(cmd, arg)))
        return self

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

parser.add_argument('--aps', action='store_true', help='采用定时调度方式启动')

# 添加覆盖 配置文件参数的，section.key 格式的参数。 此处只添加了两个。根据主要可以直接如下添加。后续的代码能自动适配config.Config.rewrite_by_cmd
parser.add_argument('--sku.sku_id', type=str, help='购买商品id.优先级最高')
parser.add_argument('--sku.buy_time', type=str, help='购买时间.优先级最高')

cmd_args = parser.parse_args()

global_config = Config(config_file=cmd_args.config_file if cmd_args.config_file else 'config.ini',
                       cmd=cmd_args).rewrite_by_cmd(cmd_args)
