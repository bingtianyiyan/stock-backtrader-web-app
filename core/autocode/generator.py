# -*- coding: utf-8 -*-
import logging
import os
from typing import List

from core.autocode.templates import all_tpls
from core.contract import IntervalLevel, AdjustType
from core.utils.file_utils import list_all_files
from core.utils.git_utils import get_git_user_name, get_git_user_email
from core.utils.time_utils import now_pd_timestamp

logger = logging.getLogger(__name__)


def all_sub_modules(dir_path: str):
    """
    list all module name in specific directory

    :param dir_path:
    :return:
    """
    modules = []
    for entry in os.scandir(dir_path):
        if entry.is_dir() or (entry.path.endswith(".py") and not entry.path.endswith("pre_init.py")):
            module_name = os.path.splitext(os.path.basename(entry.path))[0]
            # ignore hidden
            if module_name.startswith(".") or not module_name[0].isalpha():
                continue
            modules.append(module_name)
    return modules


def _remove_start_end(line: str, start="class ", end="("):
    if line.startswith(start) and (end in line):
        start_index = len(start)
        end_index = line.index(end)
        return line[start_index:end_index]
    if not start and (end in line):
        end_index = line.index(end)
        return line[:end_index]


def _get_interface_name(line: str):
    """
    get interface name of the line

    :param line: the line of the source
    :return:
    """
    if line.startswith("class "):
        return _remove_start_end(line, "class ", "(")
    elif line.startswith("def "):
        return _remove_start_end(line, "def ", "(")


def _get_var_name(line: str):
    """
    get var name of the line

    :param line: the line of the source
    :return:
    """
    if not _get_interface_name(line):
        words = line.split(" ")
        if len(words) >= 2 and words[1] == "=":
            return words[0]


def all_sub_all(sub_module):
    return """

# import all from submodule {0}
from .{0} import *
from .{0} import __all__ as _{0}_all

__all__ += _{0}_all""".format(
        sub_module
    )


def fill_package_if_not_exist(dir_path: str):
    fill_package(dir_path)
    for entry in os.scandir(dir_path):
        if entry.is_dir():
            fill_package(entry.path)
            fill_package_if_not_exist(entry.path)
        elif entry.is_file():
            pass


def fill_package(dir_path: str):
    base_name = os.path.basename(dir_path)
    if base_name[0].isalpha():
        if os.path.isdir(dir_path):
            pkg_file = os.path.join(dir_path, "pre_init.py")
            if not os.path.exists(pkg_file):
                package_template = "# -*- coding: utf-8 -*-\n"
                with open(pkg_file, "w", encoding="utf-8") as outfile:
                    outfile.write(package_template)


def gen_exports(
    dir_path="./domain",
    gen_flag="# the __all__ is generated",
    export_from_package=False,
    exclude_modules=None,
    export_modules=None,
    excludes=None,
    export_var=False,
):
    if not excludes:
        excludes = ["logger"]
    if os.path.isfile(dir_path):
        files = [dir_path]
    else:
        fill_package_if_not_exist(dir_path=dir_path)
        files = list_all_files(dir_path=dir_path)
    for file in files:
        exports = []
        lines = []
        # read and generate __all__
        with open(file, encoding="utf-8") as fp:
            line = fp.readline()
            while line:
                if line.startswith(gen_flag):
                    break
                lines.append(line)
                export = _get_interface_name(line)
                if export_var and not export:
                    export = _get_var_name(line)
                if export and export[0].isalpha() and export not in excludes:
                    exports.append(export)
                line = fp.readline()
        print(f"{file}:{exports}")
        end_empty_lines_count = 0
        for i in range(-1, -len(lines) - 1, -1):
            if not lines[i].isspace():
                break
            end_empty_lines_count = end_empty_lines_count + 1
        lines = lines[: len(lines) - end_empty_lines_count]

        if not lines:
            lines.append("# -*- coding: utf-8 -*-#")

        lines.append("\n\n")
        lines.append(gen_flag)
        lines.append("\n")
        exports_str = f"__all__ = {exports}"
        exports_str = exports_str.replace("'", '"')
        if len(exports_str) > 120:
            exports_wrap = [f'\n    "{item}",' for item in exports]
            exports_str = "__all__ = [" + "".join(exports_wrap) + "\n]"
            exports_str = exports_str.replace("'", '"')
        lines.append(exports_str)
        lines.append("\n")

        # the package module
        if export_from_package:
            basename = os.path.basename(file)
            if basename == "pre_init.py":
                dir_path = os.path.dirname(file)
                modules = all_sub_modules(dir_path)
                if modules:
                    if exclude_modules:
                        modules = set(modules) - set(exclude_modules)
                    if export_modules:
                        modules = set(modules) & set(export_modules)
                    lines.append(
                        """
# pre_init.py structure:
# common code of the package
# export interface in __all__ which contains __all__ of its sub modules"""
                    )
                    for mod in modules:
                        lines.append(all_sub_all(mod))
                    lines.append("\n")

        # write with __all__
        with open(file, mode="w", encoding="utf-8") as fp:
            fp.writelines(lines)


# kdata schema rule
# 1)name:{entity_type.capitalize()}{IntervalLevel.value.capitalize()}Kdata
# 2)one db file for one schema


def gen_kdata_schema(
    pkg: str,
    providers: List[str],
    entity_type: str,
    levels: List[IntervalLevel],
    adjust_types=None,
    entity_in_submodule: bool = False,
    kdata_module="quotes",
):
    if adjust_types is None:
        adjust_types = [None]
    tables = []

    base_path = "./domain"

    if kdata_module:
        base_path = os.path.join(base_path, kdata_module)
    if entity_in_submodule:
        base_path = os.path.join(base_path, entity_type)

    if not os.path.exists(base_path):
        logger.info(f"create dir {base_path}")
        os.makedirs(base_path)

    providers_str = f"{providers}".replace("'", '"')
    for level in levels:
        for adjust_type in adjust_types:
            level = IntervalLevel(level)

            cap_entity_type = entity_type.capitalize()
            cap_level = level.value.capitalize()

            # you should define {EntityType}KdataCommon in kdata_module at first
            kdata_common = f"{cap_entity_type}KdataCommon"

            if adjust_type and (adjust_type != AdjustType.qfq):
                class_name = f"{cap_entity_type}{cap_level}{adjust_type.value.capitalize()}Kdata"
                table_name = f"{entity_type}_{level.value}_{adjust_type.value.lower()}_kdata"
            else:
                class_name = f"{cap_entity_type}{cap_level}Kdata"
                table_name = f"{entity_type}_{level.value}_kdata"

            tables.append(table_name)

            schema_template = f"""# -*- coding: utf-8 -*-
# this file is generated by gen_kdata_schema function, dont't change it
from sqlalchemy.orm import declarative_base

from core.contract.register import register_schema
from {pkg}.domain.{kdata_module} import {kdata_common}

KdataBase = declarative_base()


class {class_name}(KdataBase, {kdata_common}):
    __tablename__ = "{table_name}"


register_schema(providers={providers_str}, db_name="{table_name}", schema_base=KdataBase, entity_type="{entity_type}")

"""
            # generate the schema
            with open(os.path.join(base_path, f"{table_name}.py"), "w", encoding="utf-8") as outfile:
                outfile.write(schema_template)

        # generate the package
        pkg_file = os.path.join(base_path, "pre_init.py")
        if not os.path.exists(pkg_file):
            package_template = """# -*- coding: utf-8 -*-
"""
            with open(pkg_file, "w", encoding="utf-8") as outfile:
                outfile.write(package_template)

    # generate exports
    gen_exports("./domain")


def gen_plugin_project(entity_type, prefix: str = "zvt", dir_path: str = ".", providers=["joinquant"]):
    """
    generate a standard plugin project

    :param entity_type: the entity type of the plugin project
    :param prefix:  project prefix
    :param dir_path: the root path for the project
    :param providers: the supported providers
    """

    # generate project files
    project = f"{prefix}_{entity_type}"
    entity_class = entity_type.capitalize()
    project_path = os.path.join(dir_path, project)
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    current_time = now_pd_timestamp()
    user_name = get_git_user_name()
    user_email = get_git_user_email()

    for tpl in all_tpls(project=project, entity_type=entity_type):
        file_name = tpl[0]
        tpl_content = tpl[1].safe_substitute(
            project=project,
            entity_type=entity_type,
            entity_class=entity_class,
            providers=providers,
            provider=providers[0],
            Provider=providers[0].capitalize(),
            year=current_time.year,
            user=user_name,
            email=user_email,
        )
        file_path = os.path.join(project_path, file_name)

        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(tpl_content)


# the __all__ is generated
__all__ = [
    "all_sub_modules",
    "all_sub_all",
    "fill_package_if_not_exist",
    "fill_package",
    "gen_exports",
    "gen_kdata_schema",
    "gen_plugin_project",
]
