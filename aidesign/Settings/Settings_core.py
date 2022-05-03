import xml.etree.ElementTree as ET
from os import path
from ast import literal_eval


class Settings(object):
    def __init__(self, filename: str = None):
        """Loads XML file and parses into nested dictionaries
        This module is used as the backbone for all future modules.
        If filename is not given, can be passed straight to self.load_XML()

        :param filename [optional]: filename from which to load XML
        """
        self.loaded_modules = {}
        self.loaded_data_options = {}

        """valid_tags lists the available XML tags and their function
        TODO: populate the modules in this list automatically
        """
        self._valid_tags = {
            "pipeline": "declaration",
            "datastructure": "declaration",
            "relationships": "relationships",
            "plugin": "plugin",
            "coordinates": "list",
            "Initialiser": "entry_point",
            "Output": "exit_point",
            "UserFeedback": "module",
            "DataProcessing": "module",
            "Modelling": "module",
            "InputData": "module",
            "DecisionMaking": "module",
            "loop": "loop"
        }

        if filename is not None:
            self.load_XML(filename)

    def set_filename(self, filename: str):
        """Converts relative paths into absolute before setting."""
        if filename[0] == ".":
            self.filename = path.join(path.dirname(__file__), filename)
        elif filename[0] == "/" or (filename[0].isalpha() and filename[0].isupper()):
            self.filename = filename

    def new_config_file(self, filename: str = None):
        """Constructs new XML file with minimal format"""
        if filename is not None: 
            self.set_filename(filename)
        self.tree = ET.ElementTree(ET.Element("Settings"))
        self.root = self.tree.getroot()
        self.pipeline_tree = ET.SubElement(self.root,"pipeline")
        self.data_tree = ET.SubElement(self.root,"datastructure")

    def load_XML(self, filename: str):
        """Loads XML file into class. 
        """
        if filename != None:
            self.set_filename(filename)
        self.tree = ET.parse(self.filename)
        self._parse_XML()

    def _parse_XML(self):
        self.root = self.tree.getroot()

        self.pipeline_tree = self.root.find("pipeline")
        self._parse_tags(self.pipeline_tree, self.loaded_modules)

        self._parse_data_structure()

    def _parse_tags(self, element: ET.Element, parent:dict):
        """Detect tags and send them to correct method for parsing
        Uses getattr to call the correct method

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        for child in element:
            try:
                tag_type = self._valid_tags[child.tag]
                getattr(self, "_load_{}".format(tag_type))(child, parent)
            except KeyError:
                print("\nError: Invalid XML Tag.")
                print("XML tag \"{0}\" in \"{1}\" not found".format(child.tag,element.tag))
                print("Valid tags are: \n\t- {}".format(",\n\t- ".join([*self._valid_tags])))

    def _load_module(self, element: ET.Element, parent:dict):
        """Parses tags associated with modules and appends to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        module_name = element.attrib["name"]
        module_type = element.tag
        parent[module_name] = {"name":module_name,
                                "class":self._valid_tags[module_type],
                                "module_type": module_type}
        self._parse_tags(element,parent[module_name])

    def _load_plugin(self, element: ET.Element, parent:dict):
        """Parses tags associated with plugins and appends to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        parent["plugin"] = {}
        parent["plugin"]["plugin_name"] = element.attrib["type"]
        parent["plugin"]["options"] = {}
        for child in element:
            if child.text != None:
                val = self._parse_text_to_list(child)
                parent["plugin"]["options"][child.tag] = val
            for key in child.attrib:
                parent["plugin"]["options"][child.tag] = {key:child.attrib[key]}
            

    def _load_entry_point(self, element: ET.Element, parent:dict):
        """Parses tags associated with initialiser and appends to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        initialiser_name = element.attrib["name"]
        parent[initialiser_name] = {"name":initialiser_name,
                                    "class":self._valid_tags[element.tag]}
        self._parse_tags(element,parent[initialiser_name])

    def _load_exit_point(self, element: ET.Element, parent:dict):
        """Parses tags associated with output and appends to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        parent["output"] = {"name":"output","class":self._valid_tags[element.tag]}
        self._parse_tags(element,parent["output"])

    def _load_loop(self, element: ET.Element, parent:dict):
        """Parses tags associated with loops and appends to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        loop_name = element.attrib["name"]
        parent[loop_name] = {
            "name":loop_name,
            "class":self._valid_tags[element.tag],
            "type": element.attrib["type"].lower(),
            "condition": element.attrib["condition"],
        }
        self._parse_tags(element, parent[loop_name])

    def _load_relationships(self, element: ET.Element, parent:dict):
        """Parses tags associated with relationships and adds to parent dict

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        parent["parents"] = []
        parent["children"] = []
        for rel in element:
            if rel.tag == "parent":
                parent["parents"].append(rel.attrib["name"])
            elif rel.tag == "child":
                parent["children"].append(rel.attrib["name"])

    def _load_list(self, element: ET.Element, parent:dict):
        """Parses elements consisting of lists, e.g. coordinates

        :param elem: xml.etree.ElementTree.Element to be parsed
        :param parent: dict or dict fragment parsed tags will be appened to
        """
        if element.text != None:
            parent[element.tag] = self._parse_text_to_list(element)
            if len(parent[element.tag]) == 1:
                parent[element.tag] = parent[element.tag][0]

    def _parse_data_structure(self):
        """Parses tags associated with data structure"""
        self.data_tree = self.root.find("datastructure")
        for child in self.data_tree:
            self.loaded_data_options[child.tag]\
                = self._parse_text_to_list(child)

    def _parse_text_to_list(self, element: ET.Element) -> list:
        """Formats raw text data

        :param elem: xml.etree.ElementTree.Element to be parsed
        :returns out: list containing parsed text data
        """
        new = element.text.strip().replace(" ", "")
        out = new.split("\n")
        raw_elem_text = str()
        for idx in range(0, len(out)):
            raw_elem_text = (raw_elem_text+"\n{}").format(out[idx])
            if "[" in out[idx] and "]" in out[idx]:
                out[idx] = literal_eval(out[idx])
            if "(" in out[idx] and ")" in out[idx]:
                out[idx] = list(literal_eval(out[idx]))
        element.text = raw_elem_text
        return out

    def _print_pretty(self, element: ET.Element):
        """Print indented dictionary to screen"""
        from pprint import PrettyPrinter
        pp = PrettyPrinter(sort_dicts=False, width=100)
        pp.pprint(element)

    def print_loaded_modules(self):
        """Print indented pipeline specifications to screen"""
        self._print_pretty(self.loaded_modules)

    def print_loaded_data_structure(self):
        """Print indented data structure specifications to screen"""
        self._print_pretty(self.loaded_data_options)

    def write_to_XML(self):
        """Formats XML Tree correctly, then writes to filename
        TODO: add overwrite check and alternate filename option
        """
        self._indent(self.root)
        self.tree.write(self.filename)

    def _indent(self, elem: ET.Element, level: int = 0):
        """Formats XML tree to be human-readable before writing to file

        :param elem: xml.etree.ElementTree.Element to be indented
        :param level: int, level of initial indentation
        """
        sep = "    "
        i = "\n" + level*sep
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + sep
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
            if elem.text:
                elem.text = elem.text.replace("\n", ("\n" + (level+1)*sep))
                elem.text = ("{0}{1}").format(elem.text, i)

    def _get_element_from_name(self, name: str):
        """Find a module name and return its parent tags"""
        if name == None:
            return self.pipeline_tree
        elems = self.root.findall(".//*[@name='{0}']".format(name))
        unique_elem = [e for e in elems if e.tag != "parent" and e.tag != "child"]
        assert len(unique_elem)<2, "Error: More than one tag with same identifier"
        assert len(unique_elem)>0, "Error: No element exists with name \"{0}\"".format(name)
        return unique_elem[0]

    def _get_all_elements_with_tag(self, tag: str):
        """Return all elements with a given tag
        
        :param tag: string with tag name
        """
        elems = self.root.findall(".//*{0}".format(tag))
        return elems

    def _loop_rels_autofill(self,
                            elem:ET.Element,
                            xml_child:str):
        """Add the name of a new nested module to the relationships of a loop
        
        :param elem: ET.Element
        :param xml_child:str name of child to be nested in XML
        """
        if elem.tag != "loop":
            return elem
        else:
            return self._add_relationships(elem,[],[xml_child])

    def _add_relationships(self, 
                            elem:ET.Element, 
                            parents:list, 
                            children:list):
        """Add parents and/or children as a subelement
        Checks for duplicates before appending
        
        :param elem: ET.Element to which the relationship are appeneded
        :param parents: list of strings of parents to be appended
        :param children: list of strings of children to be appended
        """
        rels_elem = ET.SubElement(elem, "relationships")
        for p in parents:
            if not elem.findall(".//parent/[@name='{0}']".format(p)):
                new_parent = ET.SubElement(rels_elem, "parent")
                new_parent.set('name', p)
        for c in children:
            if not elem.findall(".//child/[@name='{0}']".format(c)):
                new_child = ET.SubElement(rels_elem, "child")
                new_child.set('name', c)
        return elem

    def _add_coords(self, 
                    elem:ET.Element, 
                    coords:list=None):
        if coords == None:
            return elem
        coords_elem = ET.SubElement(elem, "coordinates")
        coords_elem.text = str("\n{0}".format(coords))
        return elem

    def _add_plugin_options(self, 
                            plugin_elem:ET.Element,
                            options
                            ):
        for key in options.keys():
            if isinstance(options[key], list):
                new_option = ET.SubElement(plugin_elem, key)
                option_text = ("\n{}".format(
                    "\n".join([*options[key]])))
                new_option.text = option_text
            elif isinstance(options[key], (int,float,str)):
                new_option = ET.SubElement(plugin_elem, key)
                text_lead = "\n" if "\n" not in str(options[key]) else ""
                new_option.text = "{0} {1}".format(text_lead, str(options[key]))
            elif isinstance(options[key], (dict)):
                self._add_plugin_options(plugin_elem,options[key])

    def append_plugin_to_module(self,
                                plugin_type: str,
                                plugin_options: dict,
                                xml_parent: ET.Element or str,
                                overwrite_existing: bool = False
                                ):
        """Appened plugin as subelement to existing module element
        
        :param plugin_type: string type of plugin to be loaded into module
        :param plugin_options: dict where keys & values are options & values
        :param xml_parent: dict OR str. 
                            If string given, parent elem is found via search,
                            Otherwise, plugin appeneded directly
        """
        if isinstance(xml_parent,str):
            xml_parent = self._get_element_from_name(xml_parent)
            
        plugin_elem = xml_parent.find("./plugin")

        if plugin_elem is not None and overwrite_existing:
            xml_parent.remove(plugin_elem)
            plugin_elem = None

        if plugin_elem is None:
            plugin_elem = ET.SubElement(xml_parent, "plugin")
            plugin_elem.set('type', plugin_type) 
        self._add_plugin_options(plugin_elem,plugin_options)
        

    def append_pipeline_module(self,
                                module_type: str,
                                module_name: str,
                                plugin_type: str,
                                plugin_options: dict,
                                parents: list,
                                children: list,
                                xml_parent_element: str,
                                coords: list = None
                                ):
        """Append new pipeline module to existing XML elementTree to be written later
        
        :param module_type: string declare type of module (UserFeedback,data_processing etc)
        :param module_name: string give module a user-defined name
        :param plugin_type: string type of plugin to be loaded into module
        :param plugin_options: dict where keys & values are options & values
        :param parents: list of parent names for this module (can be empty)
        :param children: list of child names for this module (can be empty)
        :param xml_parent_element: str containing name of parent Element for new module
        :param coords [optional]: list of coordinates for UserFeedback canvas
        """
        xml_parent_element = self._get_element_from_name(xml_parent_element)

        new_mod = ET.Element(module_type.replace(" ", ""))
        new_mod.set('name', module_name)

        self.append_plugin_to_module(plugin_type,
                                        plugin_options,
                                        new_mod,
                                        0
                                        )

        if xml_parent_element.tag =="loop":
            parents.append(xml_parent_element.attrib["name"])
        new_mod = self._add_relationships(new_mod,parents,children)
        new_mod = self._add_coords(new_mod,coords)

        self._loop_rels_autofill(xml_parent_element, module_name)
        xml_parent_element.append(new_mod)

    def append_pipeline_loop(self,
                                loop_type: str,
                                condition: str,
                                loop_name: str,
                                parents: list,
                                children: list,
                                xml_parent_element: str = None, 
                                coords: list = None
                                ):
        """Append new pipeline module to existing XML file
        
        :param loop_type: string declare type of loop (for/while/manual etc)
        :param loop_name: string give loop a user-defined name
        :param plugin_type: string type of plugin to be loaded into module
        :param parents: list of parent names for this module (can be empty)
        :param children: list of child names for this module (can be empty)
        :param xml_parent_element: str containing name of parent Element for new module
        :param coords [optional]: list of coordinates for UserFeedback canvas
        """
        xml_parent_element = self._get_element_from_name(xml_parent_element)

        new_loop = ET.Element("loop")
        new_loop.set('type', loop_type)
        new_loop.set('condition', condition)
        new_loop.set('name', loop_name)

        if xml_parent_element.tag =="loop":
            parents.append(xml_parent_element.attrib["name"])
        new_loop = self._add_relationships(new_loop,parents,children)
        new_loop = self._add_coords(new_loop,coords)

        self._loop_rels_autofill(xml_parent_element, loop_name)
            
        xml_parent_element.append(new_loop)


    def append_data_structure_field(self,
                                            field_type: str,
                                            value: list,
                                            field_name: str = None):
        """Add new tags for data structure to XML file

        :param field_type: str of desired XML tag to add
        :param value: list of values for field_type
        :param field_name [optional]: str with user defined name for tag
        """
        new_field = ET.Element(field_type)
        if field_name is not None:
            new_field.set('name', field_name)
        new_field.text = value
        self.data_tree.append(new_field)



# Use case examples:
if __name__ == "__main__":
    s = Settings("./resources/Hospital.xml")
    # s = Settings("./resources/example_config.xml")
    # s = Settings()
    # s.new_config_file("./resources/example_config.xml")
    # s._get_all_elements_with_tag("loop")
    # s.load_XML("./resources/example_config.xml")
    s.append_plugin_to_module("Input Data Plugin",{"option":{"test":4}},"Input data",1)
    s.print_loaded_modules()
    
    # s.write_to_XML()
    # s.append_pipeline_loop("for",
    #                       "10",
    #                       "my_loop_3",
    #                       ["Init"],
    #                       [])
    # s.append_pipeline_module("UserFeedback thing",
    #                       "added_mod",
    #                       "startpage",
    #                       {"class_list":["test_1","test_2"],"class_list_2":["test_1","test_2"]},
    #                       ["loop0"],
    #                       ["Output","loop0"],
    #                       "loop0",
    #                       [2,3,4,5])
    # s.write_to_XML()
    # s.append_data_structure_field_to_file("replay_buffer", "1")
    # s.print_loaded_data_structure()
