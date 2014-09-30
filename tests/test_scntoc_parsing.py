import unittest
import xml.etree.ElementTree as ET

import scntoc

import os
demo1_path = os.path.join(os.path.dirname(scntoc.__file__),
                          'tests',
                          'demo1.scntoc')


from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'ISO-8859-1')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class TestParsing(unittest.TestCase):
    def test_creation(self):
        s = scntoc.SCNTOC()
        assert len(s.models()) == 0
        assert s.sources() is None
        assert s.passes() is None
        assert s.parametersValues() is None
        assert s.postLoadScript() is None
        assert s.sceneInfo() is None
        assert s.compoundOverride() is None

    def test_add_model(self):
        s = scntoc.SCNTOC()
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'path_to_file', True)
        s.add_model(model)

        self.assertEquals(len(s.models()), 1)

    def test_add_duplicate_model(self):
        s = scntoc.SCNTOC()

        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'path_to_file', True)
        s.add_model(model)

        self.assertEquals(len(s.models()), 1)

        with self.assertRaises(RuntimeError):
            s.add_model(model)

        self.assertEquals(len(s.models()), 1)

    def test_reading_from_file(self):
        st = scntoc.SCNTOC.from_file(demo1_path)

        self.assertEquals(len(st.models()), 5)
        assert type(st.sources()) is ET.Element
        assert type(st.passes()) is ET.Element
        assert type(st.parametersValues()) is ET.Element
        assert type(st.postLoadScript()) is ET.Element
        assert type(st.sceneInfo()) is ET.Element
        assert type(st.compoundOverride()) is ET.Element

    def test_xml_generation(self):
        st = scntoc.SCNTOC.from_file(demo1_path)

        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'path_to_file', True)
        st.add_model(model)

        print prettify(st.xml())
        #self.assertEquals(ET.tostring(st.xml()), xml_elem.tostring())

class TestBackupCreation(unittest.TestCase):
    expected_backup_path = demo1_path + '.bak'
    def tearDown(self):
        os.remove(self.expected_backup_path)

    def test_parsing_with_backup(self):
        st = scntoc.SCNTOC.from_file(demo1_path, backup=True)
        assert os.path.exists(self.expected_backup_path)

