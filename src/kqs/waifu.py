from typing import Dict, List
from xml.dom import minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree

from .global_const import KQS_GENERATOR, KQS_START_ID, KQS_VERSION
from .model_basic import BaseOsmModel
from .type_constraint import Bounds, Member
from .type_element import Node, Relation, Way


class Waifu:
    def __init__(self):
        self.node_dict: Dict[int, Node] = {}
        self.bounds_list: List[Bounds] = []
        self.version: str = "0.6"
        self.way_dict: Dict[int, Way] = {}
        self.generator: str = KQS_GENERATOR + "/" + KQS_VERSION
        self.relation_dict: Dict[int, Relation] = {}

    @staticmethod
    def __set_attrib(attrib: Dict[str, str], key: str, value):
        if value is not None:
            attrib[key] = str(value)

    def __parse(self, element: Element):
        # judge whether is N/W/R then invoke function.
        pass

    def __parse_node(self, element: Element):
        # Will move to method_parse.py
        attrib: Dict[str, str] = element.attrib
        tag_dict: Dict[str, str] = {}
        for sub_element in element:
            tag_dict[sub_element.attrib["k"]] = sub_element.attrib["v"]
        self.node_dict[int(attrib["id"])] = Node(attrib, tag_dict)

    def __parse_way(self, element: Element):
        # Will move to method_parse.py
        attrib: Dict[str, str] = element.attrib
        tag_dict: Dict[str, str] = {}
        nd_list: List[int] = []

        for sub_element in element:
            if sub_element.tag == "nd":
                nd_list.append(int(sub_element.attrib["ref"]))
            elif sub_element.tag == "tag":
                tag_dict[sub_element.attrib["k"]] = sub_element.attrib["v"]
            else:
                raise TypeError(
                    f"Unexpected element tag type: {sub_element.tag} in Way"
                )
        self.way_dict[int(attrib["id"])] = Way(attrib, tag_dict, nd_list)

    def __parse_relation(self, element: Element):
        # Will move to method_parse.py
        attrib: Dict[str, str] = element.attrib
        tag_dict: Dict[str, str] = {}
        member_list: List[Member] = []

        for sub_element in element:
            if sub_element.tag == "member":
                member_list.append(
                    Member(
                        sub_element.attrib["type"],
                        int(sub_element.attrib["ref"]),
                        sub_element.attrib["role"],
                    )
                )
            elif sub_element.tag == "tag":
                tag_dict[sub_element.attrib["k"]] = sub_element.attrib["v"]
            else:
                raise TypeError(
                    f"Unexpected element tag type: {sub_element.tag} in Relation"
                )
        self.relation_dict[int(attrib["id"])] = Relation(
            attrib, tag_dict, member_list
        )

    def pre_parse_classify(self, root):
        for element in root:
            if element.tag == "node":
                self.__parse_node(element)
            elif element.tag == "way":
                self.__parse_way(element)
            elif element.tag == "relation":
                self.__parse_relation(element)
            elif element.tag == "bounds":
                self.bounds_list.append(Bounds(element.attrib))
            else:
                # raise TypeError('Unexpected element tag type: ' + element.tag)
                pass

    def meow(self):
        print("==============================")
        print("Keqing load successful!")
        print("==============================")
        print(len(self.node_dict),len(self.way_dict),len(self.relation_dict),len(self.bounds_list))
        print("==============================")

    def read(self, mode=None, file_path="", text="", url=""):
        if mode == "file":
            self.read_file(file_path)
        elif mode == "memory":
            self.read_memory(text)
        elif mode == "network":
            self.read_memory(url)
        else:
            raise TypeError(f"Unexpected read mode: {mode}")

    def read_file(self, file_path: str):
        tree: ElementTree = ET.parse(file_path)
        root: Element = tree.getroot()
        self.pre_parse_classify(root)

    def read_memory(self, text: str):
        root: Element = ET.fromstring(text)
        self.pre_parse_classify(root)

    def read_network(self, url: str):
        # https://github.com/enzet/map-machine/blob/main/map_machine/osm/osm_getter.py
        pass

    def write(self, mode=None, file_path=""):
        if mode == "file":
            self.write_file(file_path)
        elif mode == "network":
            self.write_network()
        elif mode == "josm_remote_control":
            # maybe remote_control_josm will be better?
            self.write_josm_remote_control()
        else:
            raise TypeError(f"Unexpected write mode: {mode}")

    def write_file(self, file_path: str):
        root: Element = Element("osm")
        root.attrib["version"] = self.version
        root.attrib["generator"] = self.generator

        for i in self.bounds_list:
            element: Element = Element("bounds")
            Waifu.__set_attrib(element.attrib, "minlat", i.min_lat)
            Waifu.__set_attrib(element.attrib, "minlon", i.min_lon)
            Waifu.__set_attrib(element.attrib, "maxlat", i.max_lat)
            Waifu.__set_attrib(element.attrib, "maxlon", i.max_lon)
            Waifu.__set_attrib(element.attrib, "origin", i.origin)
            root.append(element)

        def base_osm_model_to_xml(
            tag_name: str, model: BaseOsmModel
        ) -> Element:
            tag: Element = Element(tag_name)
            tag.attrib["id"] = str(model.id)
            Waifu.__set_attrib(tag.attrib, "action", model.action)
            Waifu.__set_attrib(tag.attrib, "timestamp", model.timestamp)
            Waifu.__set_attrib(tag.attrib, "uid", model.uid)
            Waifu.__set_attrib(tag.attrib, "user", model.user)
            tag.attrib["visible"] = "true" if model.visible else "false"
            Waifu.__set_attrib(tag.attrib, "version", model.version)
            Waifu.__set_attrib(tag.attrib, "changeset", model.changeset)
            for k, v in model.tags.items():
                sub_element: Element = Element("tag")
                sub_element.attrib["k"] = k
                sub_element.attrib["v"] = v
                tag.append(sub_element)
            return tag

        for i in self.node_dict.values():
            if i.has_diff() and i.action != "delete":
                i.action = "modify"
            node: Element = base_osm_model_to_xml("node", i)
            node.attrib["lat"] = str(i.lat)
            node.attrib["lon"] = str(i.lon)
            root.append(node)
        for i in self.way_dict.values():
            if i.has_diff() and i.action != "delete":
                i.action = "modify"
            way: Element = base_osm_model_to_xml("way", i)
            for ref in i.nds:
                e: Element = Element("nd")
                e.attrib["ref"] = str(ref)
                way.append(e)
            root.append(way)
        for i in self.relation_dict.values():
            if i.has_diff() and i.action != "delete":
                i.action = "modify"
            relation = base_osm_model_to_xml("relation", i)
            for member in i.members:
                e: Element = Element("member")
                e.attrib["type"] = member.type
                e.attrib["ref"] = str(member.ref)
                e.attrib["role"] = member.role
                relation.append(e)
            root.append(relation)

        raw_text = ET.tostring(root)
        dom = minidom.parseString(raw_text)
        with open(file_path, "w", encoding="utf-8") as file:
            dom.writexml(file, indent="\t", newl="\n", encoding="utf-8")

    def write_network(self):
        # will imply in the future
        pass

    def write_josm_remote_control(self):
        # Thanks to @AustinZhu's idea about this branch of output stream
        # will imply in the long future
        pass

    def __new_id(self, model_dict: Dict[int, BaseOsmModel]) -> int:
        """
        ????????????????????????id????????????????????????????????????id?????????????????????1???????????????KQS_START_ID???
        :param model_dict:???????????????????????????????????????
        :return: id
        """
        min_id: int = min(model_dict.keys())
        min_id = min_id if min_id < 0 else KQS_START_ID
        return min_id - 1

    def flush(self,id:str)->None:
        # ????????????"n123,w456,r789"??????????????????????????????flush
        pass

    def new_node_id(self) -> int:
        """
        ??????????????????????????????id???
        :return: ??????id
        """
        return self.__new_id(self.node_dict)

    def new_way_id(self) -> int:
        """
        ??????????????????????????????id???
        :return: ??????id
        """
        return self.__new_id(self.way_dict)

    def new_relation_id(self) -> int:
        """
        ??????????????????????????????id???
        :return: ??????id
        """
        return self.__new_id(self.relation_dict)
