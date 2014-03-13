import xml.etree.ElementTree as ET
from xml.dom import minidom


class Resolution(object):
    def __init__(self, name, id, href):
        self._name = name
        self._id = id
        # so we can make sure href is of a valid format
        # (starts with file://, uses / delims)
        self.set_href(href)

    @classmethod
    def from_xml(self, xml_element):
        name = xml_element.attrib['name']
        id = xml_element.attrib['id']
        href = xml_element.attrib['href']

        obj = Resolution(name, id, href)
        return obj

    def name(self):
        return self._name

    def id(self):
        return self._id

    def href(self):
        return self._href

    def path(self):
        '''
        The same as href(), only strips off the file:// prefix
        '''

        return self.href().replace('file://', '')

    def set_name(self, new_name):
        self._name = new_name

    def setId(self, new_id):
        self._id = new_id

    def set_href(self, new_href):
        # first we convert backward slashes to forward ones
        new_href = new_href.replace('\\', '/')

        # then we check if the href starts with file://, unless it's blank
        if new_href != '' and not new_href.startswith('file://'):
            new_href = 'file://' + new_href

        self._href = new_href

    def xml(self):
        xml_root = ET.Element('resolution')
        xml_root.set('name', self.name())
        xml_root.set('id', str(self.id()))
        xml_root.set('href', self.href())

        return xml_root


class Model(object):
    def __init__(self, name):
        self._name = name
        self._active_resolution = 0
        self._resolutions = []

        self.add_resolution('Offloaded', '')

    @classmethod
    def from_xml(self, xml):
        #print 'creating a model object from xml with name', xml.attrib['name']
        obj = Model(xml.attrib['name'])
        obj._active_resolution = int(xml.attrib['active_resolution'])
        for resolution_elem in xml.findall('resolution'):
            if resolution_elem.attrib['name'] in [r.name() for r in obj.resolutions()]:
                #print 'resolution named "%s" already exists, skipping creation' % resolution_elem.attrib['name']
                continue
            #print 'adding resolution', resolution_elem.attrib['name']
            obj.add_resolution(resolution_elem.attrib['name'], resolution_elem.attrib['href'], False)
        return obj

    def set_name(self, name):
        self._name = name

    def name(self):
        return self._name

    def active_resolution_id(self):
        return self._active_resolution

    def set_active_resolution(self, id):
        if id < len(self._resolutions):
            self._active_resolution = id
        else:
            raise RuntimeError('Invalid id! Too few resolutions.')

    def active_resolution(self):
        return self._resolutions[self._active_resolution]

    def add_resolution(self, name, href, set_as_active_resolution=True):
        next_id = len(self._resolutions)
        res = Resolution(name, next_id, href)
        self._resolutions.append(res)

        if set_as_active_resolution:
            self._active_resolution = next_id

    def resolutions(self, id=None):
        if id is None:
            return self._resolutions
        else:
            return self._resolutions[id]

    def remove_resolution(self, name):
        if name == 'Offloaded':
            raise RuntimeError("You cannot remove the 'Offloaded' resolution.")
        res_to_remove = None
        for resolution in reversed(self._resolutions):
            if resolution.name() == name:
                # we found a resolution matching the name
                res_to_remove = resolution
                break
        else:
            raise RuntimeError('Invalid resolution name specified!')

        # if we found something to remove we continue from here
        if self._active_resolution >= res_to_remove.id():
            self._active_resolution -= 1

        self._resolutions.remove(res_to_remove)

        for idx, resolution in enumerate(self._resolutions):
            resolution.setId(idx)

    def xml(self):
        xml_root = ET.Element('Model')
        xml_root.set('name', self.name())
        xml_root.set('active_resolution', str(self.active_resolution_id()))

        for res in self.resolutions():
            xml_root.append(res.xml())

        return xml_root


class SCNTOC(object):
    def __init__(self):
        self._models = []
        self._sources = None
        self._passes = None
        self._parametersValues = None
        self._postLoadScript = None
        self._sceneInfo = None
        self._compoundOverride = None
        self._scntocPath = ''

    @classmethod
    def from_file(cls, path_to_scntoc):
        tree = ET.parse(path_to_scntoc)
        s = SCNTOC()

        for m in tree.find('Models'):
            s._models.append(Model.from_xml(m))

        s._scntocPath = path_to_scntoc
        s._sources = tree.find('Sources')
        s._passes = tree.find('Passes')
        s._parametersValues = tree.find('ParametersValues')
        s._postLoadScript = tree.find('PostLoadScript')
        s._sceneInfo = tree.find('SceneInfo')
        s._compoundOverride = tree.find('CompoundOverride')

        return s

    def models(self):
        return self._models

    def add_model(self, model):
        if model.name() in [m.name() for m in self._models]:
            raise RuntimeError("A model named %s is already in the scntoc!")
        self._models.append(model)

    def sources(self):
        return self._sources

    def passes(self):
        return self._passes

    def parametersValues(self):
        return self._parametersValues

    def postLoadScript(self):
        return self._postLoadScript

    def sceneInfo(self):
        return self._sceneInfo

    def compoundOverride(self):
        return self._compoundOverride

    def xml(self):
        root = ET.Element('xsi_file')

        # header
        root.set('type', 'SceneTOC')
        root.set('xsi_version', '12.0.921.0')
        root.set('syntax_version', '2.0')

        # models
        models_element = ET.SubElement(root, 'Models')
        for m in self._models:
            models_element.append(m.xml())

        # sources
        if self._sources is not None:
            root.append(self._sources)

        # passes
        if self._passes is not None:
            root.append(self._passes)

        # parametersValues
        if self._parametersValues is not None:
            root.append(self._parametersValues)

        # postLoadScript
        if self._postLoadScript is not None:
            root.append(self._postLoadScript)

        # sceneInfo
        if self._sceneInfo is not None:
            root.append(self._sceneInfo)

        # compoundOverride
        if self._compoundOverride is not None:
            root.append(self._compoundOverride)

        return root

    def write(self):
        if self._scntocPath == '':
            raise RuntimeError('Invalid scntocpath of [%s]' % self._scntocPath)

        with open(self._scntocPath, 'wt') as f:
            f.write(prettify(self.xml()))


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'ISO-8859-1')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':
    demo1 = 'demo1.scntoc'

    s = SCNTOC.from_file(demo1)
    print s.models()[0]._resolution_names
